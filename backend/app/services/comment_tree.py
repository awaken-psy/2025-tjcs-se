"""
评论树构建服务
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from app.database.repositories.interaction_repository import InteractionRepository
from app.domain.interaction import Interaction, InteractionType, User
from app.model.interaction import CommentsListResponse, CommentItem


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

            # 使用优化的评论树查询
            comments = self.interaction_repo.get_comments_by_capsule_with_tree(
                capsule_id=capsule_id,
                page=page,
                page_size=page_size,
                sort=sort
            )

            # 转换为API格式
            comment_items = []
            for comment in comments:
                # 获取评论用户信息
                user = self.interaction_repo.get_user_by_id(comment.user_id)
                if user:
                    comment_item = self._build_comment_item_with_replies(comment, user)
                    comment_items.append(comment_item)

            return CommentsListResponse(comments=comment_items)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"获取评论失败: {str(e)}")

    def _build_comment_item_with_replies(self, comment: Interaction, user: User) -> CommentItem:
        """递归构建评论项及其回复"""
        # 构建当前评论项
        comment_item = comment.to_api_comment_item(
            user=user,
            like_count=comment.like_count or 0,
            is_liked=False  # 简化实现，默认为未点赞
        )

        # 递归构建回复
        if comment.replies:
            reply_items = []
            for reply in comment.replies:
                # 获取回复用户信息
                reply_user = self.interaction_repo.get_user_by_id(reply.user_id)
                if reply_user:
                    reply_item = self._build_comment_item_with_replies(reply, reply_user)
                    reply_items.append(reply_item)
            comment_item.replies = reply_items

        return comment_item

    def create_comment_with_tree(self, user_id: int, capsule_id: int, content: str,
                               parent_id: Optional[int] = None):
        """创建评论（简化实现，不依赖数据库parent_id字段）"""
        # 验证用户存在
        user = self.interaction_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")

        # 验证胶囊存在且用户已解锁
        unlock_record = self.interaction_repo.get_unlock_record(user_id, capsule_id)
        if not unlock_record:
            raise ValueError("您还未解锁此胶囊，无法进行评论")

        # 简化parent_id验证：由于数据库没有parent_id字段，暂时不验证父评论关系
        # 但保留参数以便后续扩展

        # 清理评论内容
        content_clean = content.strip()
        if len(content_clean) > 500:
            raise ValueError("评论内容不能超过500个字符")

        # 创建评论（不传递parent_id到数据库）
        from app.database.repositories.interaction_repository import Interaction
        comment_interaction = self.interaction_repo.create_comment(
            user_id=user_id,
            capsule_id=capsule_id,
            content=content_clean,
            parent_id=None  # 数据库不支持parent_id，传None
        )

        # 转换为Comment领域对象
        comment = Comment(
            id=comment_interaction.id,
            capsule_id=capsule_id,
            user_id=user_id,
            content=content_clean,
            parent_id=parent_id,  # 在domain层保留parent_id信息
            created_at=comment_interaction.created_at
        )

        return comment.to_api_add_comment_response(user)


class CommentQueryBuilder:
    """评论查询构建器"""

    @staticmethod
    def build_hot_score_query():
        """构建热度评分查询"""
        return (
            func.coalesce(
                func.count()
                .filter(and_(
                    # 这里应该根据实际表结构调整
                )),
                0
            ) * 3 +  # 点赞权重为3
            func.coalesce(
                func.count()
                .filter(and_(
                    # 这里应该根据实际表结构调整
                )),
                0
            ) * 1   # 回复权重为1
        )

    @staticmethod
    def build_comment_tree_query(capsule_id: int, page: int = 1, page_size: int = 20,
                               sort: str = "latest"):
        """构建评论树查询"""
        offset = (page - 1) * page_size

        # 基础查询条件
        conditions = and_(
            # 胶囊ID条件
            # 评论类型条件
            # 非空内容条件
            # 父评论条件
        )

        # 排序逻辑
        if sort == "latest":
            order_by = desc("created_at")
        elif sort == "hottest":
            hot_score = CommentQueryBuilder.build_hot_score_query()
            order_by = desc(hot_score)

        return {
            "conditions": conditions,
            "offset": offset,
            "limit": page_size,
            "order_by": order_by
        }