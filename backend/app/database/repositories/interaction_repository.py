from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

if TYPE_CHECKING:
    from ..orm.capsule_interaction import CapsuleInteraction
    from ..orm.unlock_record import UnlockRecord
    from ..orm.user import User

from ...domain.interaction import (
    User as DomainUser, Interaction, CapsuleLike,
    CapsuleCollect, Comment, InteractionType
)


class InteractionRepository:
    """交互相关数据库操作"""

    def __init__(self, db: Session):
        self.db = db

    def _orm_to_domain_user(self, user_orm) -> DomainUser:
        """将User ORM对象转换为Domain User对象"""
        return DomainUser(
            user_id=user_orm.id,
            username=user_orm.username,
            nickname=user_orm.nickname,
            avatar_url=user_orm.avatar_url
        )

    def _orm_to_domain_interaction(self, interaction_orm) -> Interaction:
        """将CapsuleInteraction ORM对象转换为Domain Interaction对象"""
        # 通过unlock_record获取user_id和capsule_id
        user_id = interaction_orm.unlock_record.user_id if interaction_orm.unlock_record else 0
        capsule_id = interaction_orm.unlock_record.capsule_id if interaction_orm.unlock_record else 0

        return Interaction(
            id=interaction_orm.id,
            unlock_record_id=interaction_orm.unlock_record_id,
            user_id=user_id,
            capsule_id=capsule_id,
            interaction_type=InteractionType(interaction_orm.interaction_type),
            comment_content=interaction_orm.comment_content,
            comment_rating=interaction_orm.comment_rating,
            share_platform=interaction_orm.share_platform,
            share_url=interaction_orm.share_url,
            interaction_latitude=interaction_orm.interaction_latitude,
            interaction_longitude=interaction_orm.interaction_longitude,
            created_at=interaction_orm.created_at,
            updated_at=interaction_orm.updated_at
        )

    def _domain_to_orm_interaction(self, interaction_domain: Interaction):
        """将Domain Interaction对象转换为CapsuleInteraction ORM对象"""
        # 动态导入以避免类型检查问题
        from ..orm.capsule_interaction import CapsuleInteraction

        return CapsuleInteraction(
            id=interaction_domain.id,
            unlock_record_id=interaction_domain.unlock_record_id,
            interaction_type=interaction_domain.interaction_type.value,
            comment_content=interaction_domain.comment_content,
            comment_rating=interaction_domain.comment_rating,
            share_platform=interaction_domain.share_platform,
            share_url=interaction_domain.share_url,
            interaction_latitude=interaction_domain.interaction_latitude,
            interaction_longitude=interaction_domain.interaction_longitude,
            created_at=interaction_domain.created_at,
            updated_at=interaction_domain.updated_at
        )

    def get_user_by_id(self, user_id: int) -> Optional[DomainUser]:
        """根据用户ID获取用户"""
        from ..orm.user import User
        user_orm = self.db.query(User).filter(User.id == user_id).first()
        return self._orm_to_domain_user(user_orm) if user_orm else None

    def get_unlock_record(self, user_id: int, capsule_id: int):
        """获取用户的解锁记录"""
        from ..orm.unlock_record import UnlockRecord
        return self.db.query(UnlockRecord).filter(
            and_(
                UnlockRecord.user_id == user_id,
                UnlockRecord.capsule_id == capsule_id
            )
        ).first()

    def get_like_interaction(self, user_id: int, capsule_id: int) -> Optional[Interaction]:
        """获取用户的点赞交互记录"""
        unlock_record = self.get_unlock_record(user_id, capsule_id)
        if not unlock_record:
            return None

        from ..orm.capsule_interaction import CapsuleInteraction
        interaction_orm = self.db.query(CapsuleInteraction).filter(
            and_(
                CapsuleInteraction.unlock_record_id == getattr(unlock_record, 'id', 0),
                CapsuleInteraction.interaction_type == InteractionType.LIKE.value
            )
        ).first()

        return self._orm_to_domain_interaction(interaction_orm) if interaction_orm else None

    def get_like_count(self, capsule_id: int) -> int:
        """获取胶囊的点赞总数"""
        from ..orm.capsule_interaction import CapsuleInteraction
        from ..orm.unlock_record import UnlockRecord
        return self.db.query(CapsuleInteraction).join(UnlockRecord).filter(
            and_(
                UnlockRecord.capsule_id == capsule_id,
                CapsuleInteraction.interaction_type == InteractionType.LIKE.value
            )
        ).count()

    def create_like_interaction(self, user_id: int, capsule_id: int) -> Interaction:
        """创建点赞交互记录"""
        unlock_record = self.get_unlock_record(user_id, capsule_id)
        if not unlock_record:
            raise ValueError("用户未解锁此胶囊，无法进行交互")

        interaction = Interaction(
            unlock_record_id=getattr(unlock_record, 'id', 0),
            user_id=user_id,
            capsule_id=capsule_id,
            interaction_type=InteractionType.LIKE
        )

        interaction_orm = self._domain_to_orm_interaction(interaction)
        self.db.add(interaction_orm)
        self.db.commit()
        self.db.refresh(interaction_orm)

        return self._orm_to_domain_interaction(interaction_orm)

    def delete_like_interaction(self, user_id: int, capsule_id: int) -> bool:
        """删除点赞交互记录"""
        unlock_record = self.get_unlock_record(user_id, capsule_id)
        if not unlock_record:
            return False

        from ..orm.capsule_interaction import CapsuleInteraction
        deleted_count = self.db.query(CapsuleInteraction).filter(
            and_(
                CapsuleInteraction.unlock_record_id == getattr(unlock_record, 'id', 0),
                CapsuleInteraction.interaction_type == InteractionType.LIKE.value
            )
        ).delete()

        self.db.commit()
        return deleted_count > 0

    def get_comment_by_id(self, comment_id: int) -> Optional[Interaction]:
        """根据评论ID获取评论"""
        from ..orm.capsule_interaction import CapsuleInteraction
        interaction_orm = self.db.query(CapsuleInteraction).filter(
            and_(
                CapsuleInteraction.id == comment_id,
                CapsuleInteraction.interaction_type == InteractionType.COMMENT.value
            )
        ).first()

        return self._orm_to_domain_interaction(interaction_orm) if interaction_orm else None

    def get_comments_by_capsule(self, capsule_id: int, page: int = 1, page_size: int = 20,
                               sort: str = "latest") -> List[Interaction]:
        """获取胶囊的评论列表"""
        offset = (page - 1) * page_size

        from ..orm.capsule_interaction import CapsuleInteraction
        from ..orm.unlock_record import UnlockRecord
        query = self.db.query(CapsuleInteraction).join(UnlockRecord).filter(
            and_(
                UnlockRecord.capsule_id == capsule_id,
                CapsuleInteraction.interaction_type == InteractionType.COMMENT.value,
                CapsuleInteraction.comment_content.isnot(None)
            )
        )

        if sort == "latest":
            query = query.order_by(desc(CapsuleInteraction.created_at))
        elif sort == "hottest":
            # 简化实现：按创建时间排序，实际应该按点赞数排序
            query = query.order_by(desc(CapsuleInteraction.created_at))

        interactions_orm = query.offset(offset).limit(page_size).all()

        return [self._orm_to_domain_interaction(interaction) for interaction in interactions_orm]

    def create_comment(self, user_id: int, capsule_id: int, content: str,
                      parent_id: Optional[int] = None) -> Interaction:
        """创建评论"""
        unlock_record = self.get_unlock_record(user_id, capsule_id)
        if not unlock_record:
            raise ValueError("用户未解锁此胶囊，无法进行评论")

        interaction = Interaction(
            unlock_record_id=getattr(unlock_record, 'id', 0),
            user_id=user_id,
            capsule_id=capsule_id,
            interaction_type=InteractionType.COMMENT,
            comment_content=content,
            parent_id=parent_id  # 在domain层保留parent_id，但不存储到数据库
        )

        interaction_orm = self._domain_to_orm_interaction(interaction)
        self.db.add(interaction_orm)
        self.db.commit()
        self.db.refresh(interaction_orm)

        return self._orm_to_domain_interaction(interaction_orm)

    def delete_comment(self, comment_id: int, user_id: int) -> bool:
        """删除评论（只能删除自己的评论）"""
        # 获取评论对应的解锁记录
        from ..orm.capsule_interaction import CapsuleInteraction
        from ..orm.unlock_record import UnlockRecord
        interaction_orm = self.db.query(CapsuleInteraction).join(UnlockRecord).filter(
            and_(
                CapsuleInteraction.id == comment_id,
                CapsuleInteraction.interaction_type == InteractionType.COMMENT.value,
                UnlockRecord.user_id == user_id
            )
        ).first()

        if not interaction_orm:
            return False

        self.db.delete(interaction_orm)
        self.db.commit()
        return True

    def get_comment_like_count(self, comment_id: int) -> int:
        """获取评论的点赞数（简化实现，实际可能需要单独的评论点赞表）"""
        # 这里简化处理，返回0，实际实现可能需要额外的评论点赞表
        return 0

    def is_user_collected_capsule(self, user_id: int, capsule_id: int) -> bool:
        """检查用户是否收藏了胶囊（使用COLLECT类型交互）"""
        unlock_record = self.get_unlock_record(user_id, capsule_id)
        if not unlock_record:
            return False

        from ..orm.capsule_interaction import CapsuleInteraction
        interaction_orm = self.db.query(CapsuleInteraction).filter(
            and_(
                CapsuleInteraction.unlock_record_id == getattr(unlock_record, 'id', 0),
                CapsuleInteraction.interaction_type == InteractionType.COLLECT.value
            )
        ).first()

        return interaction_orm is not None

    def create_collect_interaction(self, user_id: int, capsule_id: int) -> Interaction:
        """创建收藏交互记录"""
        unlock_record = self.get_unlock_record(user_id, capsule_id)
        if not unlock_record:
            raise ValueError("用户未解锁此胶囊，无法收藏")

        # 检查是否已经收藏
        from ..orm.capsule_interaction import CapsuleInteraction
        existing_interaction = self.db.query(CapsuleInteraction).filter(
            and_(
                CapsuleInteraction.unlock_record_id == getattr(unlock_record, 'id', 0),
                CapsuleInteraction.interaction_type == InteractionType.COLLECT.value
            )
        ).first()

        if existing_interaction:
            raise ValueError("已经收藏过此胶囊")

        interaction = Interaction(
            unlock_record_id=getattr(unlock_record, 'id', 0),
            user_id=user_id,
            capsule_id=capsule_id,
            interaction_type=InteractionType.COLLECT
        )

        interaction_orm = self._domain_to_orm_interaction(interaction)
        self.db.add(interaction_orm)
        self.db.commit()
        self.db.refresh(interaction_orm)

        return self._orm_to_domain_interaction(interaction_orm)

    def delete_collect_interaction(self, user_id: int, capsule_id: int) -> bool:
        """删除收藏交互记录"""
        unlock_record = self.get_unlock_record(user_id, capsule_id)
        if not unlock_record:
            return False

        from ..orm.capsule_interaction import CapsuleInteraction
        deleted_count = self.db.query(CapsuleInteraction).filter(
            and_(
                CapsuleInteraction.unlock_record_id == getattr(unlock_record, 'id', 0),
                CapsuleInteraction.interaction_type == InteractionType.COLLECT.value
            )
        ).delete()

        self.db.commit()
        return deleted_count > 0
    def get_comments_by_capsule_with_tree(self, capsule_id: int, page: int = 1, page_size: int = 20,
                                         sort: str = "latest") -> List[Interaction]:
        """获取胶囊的评论列表（简化实现，不依赖数据库parent_id字段）"""
        # 由于数据库表中没有parent_id字段，暂时使用普通评论列表
        # 在domain层构建虚拟的评论树结构
        comments = self.get_comments_by_capsule(capsule_id, page, page_size, sort)

        # 为每个评论添加空的回复列表，保持API兼容性
        for comment in comments:
            comment.replies = []
            comment.like_count = 0  # 简化处理，实际需要查询点赞数

        return comments

