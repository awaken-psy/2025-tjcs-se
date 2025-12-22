"""
评论树构建服务（不依赖数据库parent_id字段）
通过comment_content中的@username格式来识别回复关系
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
import re

from app.database.repositories.interaction_repository import InteractionRepository
from app.domain.interaction import Interaction, InteractionType, User
from app.model.interaction import CommentsListResponse, CommentItem, CommentUser


class CommentTreeService:
    """评论树构建服务"""

    def __init__(self, db: Session):
        self.db = db
        self.interaction_repo = InteractionRepository(db)

    def get_comments_with_tree(self, capsule_id: int, page: int = 1, page_size: int = 20,
                             sort: str = "latest") -> CommentsListResponse:
        """获取评论列表并构建评论树"""
        try:
            # 验证排序类型
            if sort not in ["latest", "hottest"]:
                raise ValueError("无效的排序类型")

            # 获取所有评论（不分页，因为需要在内存中构建树）
            all_comments = self.interaction_repo.get_all_comments_by_capsule(
                capsule_id=capsule_id,
                sort=sort
            )

            # 构建评论树
            comment_tree = self._build_comment_tree(all_comments)

            # 应用分页到顶层评论
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_comments = comment_tree[start_idx:end_idx]

            # 转换为API格式
            comment_items = []
            for comment in paginated_comments:
                user = self.interaction_repo.get_user_by_id(comment.user_id)
                if user:
                    comment_item = self._build_comment_item_with_replies(comment, user)
                    comment_items.append(comment_item)

            return CommentsListResponse(comments=comment_items)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"获取评论失败: {str(e)}")

    def _build_comment_tree(self, comments: List[Interaction]) -> List[Interaction]:
        """构建评论树

        通过解析comment_content中的@username格式来识别回复关系
        例如："@张三 这是回复内容" 会被识别为对用户"张三"的回复
        """
        # 创建用户ID到用户名的映射
        user_id_to_username = {}
        for comment in comments:
            user = self.interaction_repo.get_user_by_id(comment.user_id)
            if user:
                user_id_to_username[comment.user_id] = user.nickname

        # 识别顶级评论和回复
        top_level_comments = []
        reply_map: Dict[int, List[Interaction]] = {}

        for comment in comments:
            content = comment.comment_content or ""

            # 检查是否是回复（以@username开头）
            reply_to_user_id = self._extract_reply_to_user(content, user_id_to_username)

            if reply_to_user_id is not None:
                # 这是一个回复
                if reply_to_user_id not in reply_map:
                    reply_map[reply_to_user_id] = []
                reply_map[reply_to_user_id].append(comment)
            else:
                # 这是一个顶级评论
                top_level_comments.append(comment)

        # 为每个顶级评论附加其回复
        for top_comment in top_level_comments:
            replies = reply_map.get(top_comment.user_id, [])

            # 对回复按时间排序（最新的在前）
            replies.sort(key=lambda x: x.created_at or x.created_at, reverse=True)

            # 递归构建回复的回复
            for reply in replies:
                reply.replies = reply_map.get(reply.user_id, [])
                # 对回复的回复也排序
                reply.replies.sort(key=lambda x: x.created_at or x.created_at, reverse=True)

            top_comment.replies = replies

        # 对顶级评论排序
        if hasattr(top_level_comments[0] if top_level_comments else None, 'created_at'):
            # 按创建时间排序（最新的在前）
            top_level_comments.sort(key=lambda x: x.created_at or x.created_at, reverse=True)

        return top_level_comments

    def _extract_reply_to_user(self, content: str, user_id_to_username: Dict[int, str]) -> Optional[int]:
        """从评论内容中提取被回复用户的ID

        例如："@张三 这是回复" -> 返回张三的user_id
        """
        # 匹配 @username 格式（在评论开头）
        match = re.match(r'^@(\S+)\s*', content)
        if not match:
            return None

        username = match.group(1)

        # 查找对应的user_id
        for user_id, name in user_id_to_username.items():
            if name == username:
                return user_id

        return None

    def _build_comment_item_with_replies(self, comment: Interaction, user: User) -> CommentItem:
        """递归构建评论项及其回复"""
        # 获取点赞数
        like_count = self.interaction_repo.get_comment_like_count(comment.id or 0)

        # 构建当前评论项
        comment_user = CommentUser(
            user_id=user.user_id,
            nickname=user.nickname,
            avatar=user.avatar_url
        )

        # 递归构建回复列表
        reply_items = []
        if comment.replies:
            for reply in comment.replies:
                reply_user = self.interaction_repo.get_user_by_id(reply.user_id)
                if reply_user:
                    reply_item = self._build_comment_item_with_replies(reply, reply_user)
                    reply_items.append(reply_item)

        return CommentItem(
            id=str(comment.id) if comment.id else "",
            content=comment.comment_content or "",
            user=comment_user,
            created_at=comment.created_at or comment.created_at,
            like_count=like_count,
            is_liked=False,  # 简化实现，默认为未点赞
            replies=reply_items if reply_items else None
        )

    def get_comment_count(self, capsule_id: int) -> int:
        """获取胶囊的总评论数（包括所有回复）"""
        return self.interaction_repo.get_comment_count_by_capsule(capsule_id)
