from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.repositories.interaction_repository import InteractionRepository
from app.domain.interaction import (
    User, Interaction, CapsuleLike, CapsuleCollect, Comment,
    InteractionType, CommentSortType
)
from app.model.interaction import (
    LikeCapsuleResponse, AddCommentResponse, CommentsListResponse,
    CollectCapsuleResponse, CommentItem
)


class InteractionService:
    """交互相关业务逻辑"""

    def __init__(self, db: Session):
        self.interaction_repo = InteractionRepository(db)
        self.db = db

    def get_unlock_record(self, user_id: int, capsule_id: int):
        """获取用户的解锁记录"""
        return self.interaction_repo.get_unlock_record(user_id, capsule_id)

    def like_capsule(self, user_id: int, capsule_id: int) -> LikeCapsuleResponse:
        """点赞胶囊"""
        try:
            # 检查用户是否已点赞
            existing_like = self.interaction_repo.get_like_interaction(user_id, capsule_id)

            if existing_like:
                # 已点赞，执行取消点赞
                self.interaction_repo.delete_like_interaction(user_id, capsule_id)
                like_count = self.interaction_repo.get_like_count(capsule_id)
                return CapsuleLike(
                    user_id=user_id,
                    capsule_id=capsule_id,
                    is_liked=False,
                    like_count=like_count
                ).to_api_like_response()
            else:
                # 未点赞，执行点赞
                self.interaction_repo.create_like_interaction(user_id, capsule_id)
                like_count = self.interaction_repo.get_like_count(capsule_id)
                return CapsuleLike(
                    user_id=user_id,
                    capsule_id=capsule_id,
                    is_liked=True,
                    like_count=like_count
                ).to_api_like_response()
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"点赞操作失败: {str(e)}")

    def unlike_capsule(self, user_id: int, capsule_id: int) -> LikeCapsuleResponse:
        """取消点赞胶囊"""
        try:
            # 检查是否已点赞
            existing_like = self.interaction_repo.get_like_interaction(user_id, capsule_id)
            if not existing_like:
                # 未点赞，返回当前状态
                like_count = self.interaction_repo.get_like_count(capsule_id)
                return CapsuleLike(
                    user_id=user_id,
                    capsule_id=capsule_id,
                    is_liked=False,
                    like_count=like_count
                ).to_api_like_response()

            # 执行取消点赞
            success = self.interaction_repo.delete_like_interaction(user_id, capsule_id)
            if not success:
                raise ValueError("取消点赞失败")

            like_count = self.interaction_repo.get_like_count(capsule_id)
            return CapsuleLike(
                user_id=user_id,
                capsule_id=capsule_id,
                is_liked=False,
                like_count=like_count
            ).to_api_like_response()
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"取消点赞失败: {str(e)}")

    def add_comment(self, user_id: int, capsule_id: int, content: str,
                   parent_id: Optional[int] = None) -> AddCommentResponse:
        """添加评论"""
        try:
            # 验证用户存在
            user = self.interaction_repo.get_user_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")

            # 验证评论内容
            if not content or not content.strip():
                raise ValueError("评论内容不能为空")

            content_clean = content.strip()
            if len(content_clean) > 500:
                raise ValueError("评论内容不能超过500个字符")

            # 验证胶囊是否存在且用户已解锁
            unlock_record = self.get_unlock_record(user_id, capsule_id)
            if not unlock_record:
                raise ValueError("您还未解锁此胶囊，无法进行评论")

            # 如果是回复评论，验证父评论是否存在
            if parent_id:
                parent_comment = self.interaction_repo.get_comment_by_id(parent_id)
                if not parent_comment:
                    raise ValueError("回复的评论不存在")
                if parent_comment.capsule_id != capsule_id:
                    raise ValueError("回复的评论不属于当前胶囊")

            # 创建评论
            comment_interaction = self.interaction_repo.create_comment(
                user_id=user_id,
                capsule_id=capsule_id,
                content=content_clean,
                parent_id=parent_id
            )

            # 转换为Comment领域对象以使用其API转换方法
            comment = Comment(
                id=comment_interaction.id,
                capsule_id=capsule_id,
                user_id=user_id,
                content=content_clean,
                parent_id=parent_id,
                created_at=comment_interaction.created_at
            )

            return comment.to_api_add_comment_response(user)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"添加评论失败: {str(e)}")

    def get_comments(self, capsule_id: int, page: int = 1, page_size: int = 20,
                    sort: str = "latest") -> CommentsListResponse:
        """获取评论列表"""
        try:
            # 验证排序类型
            if sort not in [CommentSortType.LATEST.value, CommentSortType.HOTTEST.value]:
                raise ValueError("无效的排序类型")

            # 获取评论列表
            comments = self.interaction_repo.get_comments_by_capsule(
                capsule_id=capsule_id,
                page=page,
                page_size=page_size,
                sort=sort
            )

            # 转换为API格式
            comment_items = []
            for comment in comments:
                user = self.interaction_repo.get_user_by_id(comment.user_id)
                if user:
                    like_count = self.interaction_repo.get_comment_like_count(comment.id or 0)
                    comment_item = comment.to_api_comment_item(
                        user=user,
                        like_count=like_count,
                        is_liked=False  # 简化实现，默认为未点赞
                    )
                    comment_items.append(comment_item)

            return CommentsListResponse(comments=comment_items)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"获取评论失败: {str(e)}")

    def delete_comment(self, comment_id: int, user_id: int) -> None:
        """删除评论"""
        try:
            # 验证评论ID
            if not comment_id or comment_id <= 0:
                raise ValueError("无效的评论ID")

            success = self.interaction_repo.delete_comment(comment_id, user_id)
            if not success:
                raise ValueError("评论不存在或无权限删除")
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"删除评论失败: {str(e)}")

    def collect_capsule(self, user_id: int, capsule_id: int) -> CollectCapsuleResponse:
        """收藏胶囊"""
        try:
            # 检查用户是否已解锁胶囊
            unlock_record = self.get_unlock_record(user_id, capsule_id)
            if not unlock_record:
                raise ValueError("您还未解锁此胶囊，无法收藏")

            # 检查是否已收藏
            is_collected = self.interaction_repo.is_user_collected_capsule(user_id, capsule_id)

            if is_collected:
                # 已收藏，执行取消收藏
                success = self.interaction_repo.delete_collect_interaction(user_id, capsule_id)
                if not success:
                    raise ValueError("取消收藏失败")
                return CapsuleCollect(
                    user_id=user_id,
                    capsule_id=capsule_id,
                    is_collected=False
                ).to_api_collect_response()
            else:
                # 未收藏，执行收藏
                self.interaction_repo.create_collect_interaction(user_id, capsule_id)
                return CapsuleCollect(
                    user_id=user_id,
                    capsule_id=capsule_id,
                    is_collected=True
                ).to_api_collect_response()
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"收藏操作失败: {str(e)}")

    def uncollect_capsule(self, user_id: int, capsule_id: int) -> CollectCapsuleResponse:
        """取消收藏胶囊"""
        try:
            # 检查是否已收藏
            is_collected = self.interaction_repo.is_user_collected_capsule(user_id, capsule_id)
            if not is_collected:
                # 未收藏，返回当前状态
                return CapsuleCollect(
                    user_id=user_id,
                    capsule_id=capsule_id,
                    is_collected=False
                ).to_api_collect_response()

            # 执行取消收藏
            success = self.interaction_repo.delete_collect_interaction(user_id, capsule_id)
            if not success:
                raise ValueError("取消收藏失败")

            return CapsuleCollect(
                user_id=user_id,
                capsule_id=capsule_id,
                is_collected=False
            ).to_api_collect_response()
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"取消收藏失败: {str(e)}")

    def get_capsule_interactions_count(self, capsule_id: int) -> dict:
        """获取胶囊的互动统计"""
        try:
            like_count = self.interaction_repo.get_like_count(capsule_id)

            # 获取评论数量（简化实现）
            comments = self.interaction_repo.get_comments_by_capsule(capsule_id, 1, 1)
            comment_count = len(comments)  # 这里简化处理，实际应该有专门的计数方法

            # 获取收藏数量（简化实现）
            # 这里可以添加专门的收藏统计方法，但暂时返回0

            return {
                "like_count": like_count,
                "comment_count": comment_count,
                "share_count": 0,  # 简化实现，暂不支持分享统计
                "collect_count": 0  # 简化实现，可以通过查询COLLECT类型的交互来获取
            }
        except Exception as e:
            raise ValueError(f"获取互动统计失败: {str(e)}")

    def get_user_interaction_status(self, user_id: int, capsule_id: int) -> dict:
        """获取用户对胶囊的互动状态"""
        try:
            is_liked = self.interaction_repo.get_like_interaction(user_id, capsule_id) is not None
            is_collected = self.interaction_repo.is_user_collected_capsule(user_id, capsule_id)
            can_interact = self.get_unlock_record(user_id, capsule_id) is not None

            return {
                "is_liked": is_liked,
                "is_collected": is_collected,
                "can_interact": can_interact
            }
        except Exception as e:
            raise ValueError(f"获取互动状态失败: {str(e)}")