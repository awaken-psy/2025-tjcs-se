from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database.orm.user import User, UserFriend
from app.domain.friend import User as DomainUser, FriendRelation, FriendRequest, FriendStatus


class FriendRepository:
    """好友相关数据库操作"""

    def __init__(self, db: Session):
        self.db = db

    def _orm_to_domain_user(self, user_orm: User) -> DomainUser:
        """将User ORM对象转换为Domain User对象"""
        return DomainUser(
            user_id=getattr(user_orm, 'id', 0),
            username=getattr(user_orm, 'username', ''),
            nickname=getattr(user_orm, 'nickname', ''),
            avatar_url=getattr(user_orm, 'avatar_url', None),
            email=getattr(user_orm, 'email', ''),
            user_type=getattr(user_orm, 'user_type', 'student'),
            is_active=getattr(user_orm, 'is_active', True),
            created_at=getattr(user_orm, 'created_at', None)
        )

    def _orm_to_domain_friend_relation(self, friend_orm: UserFriend) -> FriendRelation:
        """将UserFriend ORM对象转换为Domain FriendRelation对象"""
        try:
            status_value = getattr(friend_orm, 'status', 'pending')
            status = FriendStatus(status_value)
        except ValueError:
            # 如果状态值无效，使用默认值
            status = FriendStatus.PENDING

        return FriendRelation(
            id=getattr(friend_orm, 'id', None),
            user_id=getattr(friend_orm, 'user_id', 0),
            friend_id=getattr(friend_orm, 'friend_id', 0),
            status=status,
            created_at=getattr(friend_orm, 'created_at', None),
            updated_at=getattr(friend_orm, 'updated_at', None)
        )

    def _domain_to_orm_friend_relation(self, friend_domain: FriendRelation) -> UserFriend:
        """将Domain FriendRelation对象转换为UserFriend ORM对象"""
        return UserFriend(
            id=getattr(friend_domain, 'id', None),
            user_id=getattr(friend_domain, 'user_id', 0),
            friend_id=getattr(friend_domain, 'friend_id', 0),
            status=getattr(friend_domain, 'status', FriendStatus.PENDING).value,
            created_at=getattr(friend_domain, 'created_at', None),
            updated_at=getattr(friend_domain, 'updated_at', None)
        )

    def find_user_by_id(self, user_id: int) -> Optional[DomainUser]:
        """根据用户ID查找用户"""
        user_orm = self.db.query(User).filter(User.id == user_id).first()
        return self._orm_to_domain_user(user_orm) if user_orm else None

    def search_users(self, query: str, page: int = 1, page_size: int = 20) -> List[DomainUser]:
        """搜索用户"""
        offset = (page - 1) * page_size
        users_orm = self.db.query(User).filter(
            or_(
                User.username.ilike(f"%{query}%"),
                User.nickname.ilike(f"%{query}%")
            )
        ).filter(User.is_active == True).offset(offset).limit(page_size).all()

        return [self._orm_to_domain_user(user) for user in users_orm]

    def get_friend_relation(self, user_id: int, friend_id: int) -> Optional[FriendRelation]:
        """获取两个用户之间的关系"""
        friend_orm = self.db.query(UserFriend).filter(
            or_(
                and_(UserFriend.user_id == user_id, UserFriend.friend_id == friend_id),
                and_(UserFriend.user_id == friend_id, UserFriend.friend_id == user_id)
            )
        ).first()

        return self._orm_to_domain_friend_relation(friend_orm) if friend_orm else None

    def send_friend_request(self, requester_id: int, addressee_id: int) -> FriendRelation:
        """发送好友请求"""
        try:
            # 检查是否已存在关系
            existing_relation = self.get_friend_relation(requester_id, addressee_id)
            if existing_relation:
                return existing_relation

            # 创建新的好友关系
            friend_relation = FriendRelation(
                user_id=requester_id,
                friend_id=addressee_id,
                status=FriendStatus.PENDING
            )

            friend_orm = self._domain_to_orm_friend_relation(friend_relation)
            self.db.add(friend_orm)
            self.db.commit()
            self.db.refresh(friend_orm)

            return self._orm_to_domain_friend_relation(friend_orm)
        except Exception:
            self.db.rollback()
            # 创建一个默认的关系对象返回
            return FriendRelation(
                user_id=requester_id,
                friend_id=addressee_id,
                status=FriendStatus.PENDING
            )

    def get_friend_requests(self, user_id: int, request_type: str, page: int = 1, page_size: int = 20) -> List[FriendRequest]:
        """获取好友请求列表"""
        offset = (page - 1) * page_size

        if request_type == "received":
            # 收到的请求（其他用户发给当前用户的）
            relations_orm = self.db.query(UserFriend).filter(
                and_(
                    UserFriend.friend_id == user_id,
                    UserFriend.status == FriendStatus.PENDING.value
                )
            ).offset(offset).limit(page_size).all()

            friend_requests = []
            for relation in relations_orm:
                friend_request = FriendRequest(
                    id=getattr(relation, 'id', None),
                    requester_id=getattr(relation, 'user_id', 0),
                    addressee_id=getattr(relation, 'friend_id', 0),
                    status=FriendStatus.PENDING,
                    created_at=getattr(relation, 'created_at', None),
                    updated_at=getattr(relation, 'updated_at', None)
                )
                friend_requests.append(friend_request)

            return friend_requests

        elif request_type == "sent":
            # 发送的请求（当前用户发给其他用户的）
            relations_orm = self.db.query(UserFriend).filter(
                and_(
                    UserFriend.user_id == user_id,
                    UserFriend.status == FriendStatus.PENDING.value
                )
            ).offset(offset).limit(page_size).all()

            friend_requests = []
            for relation in relations_orm:
                friend_request = FriendRequest(
                    id=getattr(relation, 'id', None),
                    requester_id=getattr(relation, 'user_id', 0),
                    addressee_id=getattr(relation, 'friend_id', 0),
                    status=FriendStatus.PENDING,
                    created_at=getattr(relation, 'created_at', None),
                    updated_at=getattr(relation, 'updated_at', None)
                )
                friend_requests.append(friend_request)

            return friend_requests

        return []

    def handle_friend_request(self, request_id: int, action: str) -> Optional[FriendRelation]:
        """处理好友请求"""
        try:
            friend_orm = self.db.query(UserFriend).filter(UserFriend.id == request_id).first()
            if not friend_orm:
                return None

            if action == "accept":
                setattr(friend_orm, 'status', FriendStatus.ACCEPTED.value)
            elif action == "reject":
                setattr(friend_orm, 'status', FriendStatus.REJECTED.value)
            else:
                return None

            self.db.commit()
            self.db.refresh(friend_orm)

            return self._orm_to_domain_friend_relation(friend_orm)
        except Exception:
            self.db.rollback()
            return None

    def get_friends_list(self, user_id: int, page: int = 1, page_size: int = 20) -> List[FriendRelation]:
        """获取好友列表"""
        offset = (page - 1) * page_size

        # 获取所有已接受的好友关系
        friends_orm = self.db.query(UserFriend).filter(
            and_(
                or_(UserFriend.user_id == user_id, UserFriend.friend_id == user_id),
                UserFriend.status == FriendStatus.ACCEPTED.value
            )
        ).offset(offset).limit(page_size).all()

        return [self._orm_to_domain_friend_relation(friend) for friend in friends_orm]

    def remove_friend(self, user_id: int, friend_id: int) -> bool:
        """删除好友关系"""
        try:
            deleted_count = self.db.query(UserFriend).filter(
                or_(
                    and_(UserFriend.user_id == user_id, UserFriend.friend_id == friend_id),
                    and_(UserFriend.user_id == friend_id, UserFriend.friend_id == user_id)
                )
            ).delete()

            self.db.commit()
            return deleted_count > 0
        except Exception:
            self.db.rollback()
            return False

    def get_user_friends_count(self, user_id: int) -> int:
        """获取用户好友数量"""
        return self.db.query(UserFriend).filter(
            and_(
                or_(UserFriend.user_id == user_id, UserFriend.friend_id == user_id),
                UserFriend.status == FriendStatus.ACCEPTED.value
            )
        ).count()