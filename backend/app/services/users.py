from typing import Optional
from sqlalchemy.orm import Session

from app.database.repositories.user_repository import UserRepository
from app.domain.user import SimpleUser, UserHistory, UserCapsule
from app.model.user import UserProfile, UserStats, UserHistoryResponse, UserHistoryItem


class UserService:
    """用户相关业务逻辑"""

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db = db

    def get_my_profile(self, user_id: int) -> UserProfile:
        """获取我的资料"""
        try:
            # 获取用户基本信息
            user = self.user_repo.get_user_profile_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")

            # 获取用户统计信息
            stats = self.user_repo.get_user_statistics(user_id)

            return user.to_api_user_profile(
                include_stats=True,
                created_capsules=stats['created_capsules'],
                unlocked_capsules=stats['unlocked_capsules'],
                collected_capsules=stats['collected_capsules'],
                friends_count=stats['friends_count']
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"获取用户资料失败: {str(e)}")

    def update_my_profile(self, user_id: int, nickname: Optional[str] = None,
                         avatar: Optional[str] = None, bio: Optional[str] = None) -> UserProfile:
        """更新我的资料"""
        try:
            # 验证昵称长度
            if nickname is not None and len(nickname.strip()) == 0:
                raise ValueError("昵称不能为空")
            if nickname is not None and len(nickname) > 20:
                raise ValueError("昵称长度不能超过20个字符")

            # 验证个人简介长度
            if bio is not None and len(bio) > 200:
                raise ValueError("个人简介长度不能超过200个字符")

            # 更新用户资料
            user = self.user_repo.update_user_profile(
                user_id=user_id,
                nickname=nickname.strip() if nickname else None,
                avatar_url=avatar,
                bio=bio.strip() if bio else None
            )

            if not user:
                raise ValueError("用户不存在")

            # 获取更新后的统计信息
            stats = self.user_repo.get_user_statistics(user_id)

            return user.to_api_user_profile(
                include_stats=True,
                created_capsules=stats['created_capsules'],
                unlocked_capsules=stats['unlocked_capsules'],
                collected_capsules=stats['collected_capsules'],
                friends_count=stats['friends_count']
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"更新用户资料失败: {str(e)}")

    def get_my_history(self, user_id: int, page: int = 1, page_size: int = 20,
                      sort: str = "latest", type: str = "unlocked") -> UserHistoryResponse:
        """获取我的历史记录"""
        try:
            # 验证排序类型
            if sort not in ["latest", "oldest"]:
                raise ValueError("无效的排序类型")

            # 验证历史记录类型
            if type not in ["unlocked", "created", "collected"]:
                raise ValueError("无效的历史记录类型")

            # 获取历史记录
            history_records = self.user_repo.get_user_history_records(
                user_id=user_id,
                page=page,
                page_size=page_size,
                sort=sort,
                history_type=type
            )

            # 转换为API格式
            history_items = []
            for record in history_records:
                history_items.append(record.to_api_history_item())

            return UserHistoryResponse(history=history_items)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"获取历史记录失败: {str(e)}")

    def get_user_profile(self, user_id: int) -> UserProfile:
        """获取用户资料（公开信息）"""
        try:
            # 获取用户基本信息
            user = self.user_repo.get_user_profile_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")

            # 公开信息不包含统计信息
            return user.to_api_user_profile(include_stats=False)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"获取用户资料失败: {str(e)}")

    def get_user_capsules(self, user_id: int, page: int = 1, page_size: int = 20) -> dict:
        """获取用户胶囊"""
        try:
            # 获取用户创建的胶囊
            user_capsules = self.user_repo.get_user_created_capsules(
                user_id=user_id,
                page=page,
                page_size=page_size
            )

            # 转换为API格式
            capsules_data = []
            for capsule in user_capsules:
                capsules_data.append({
                    "capsule_id": capsule.capsule_id,
                    "title": capsule.title,
                    "created_at": capsule.created_at,
                    "unlock_count": capsule.unlock_count
                })

            return {
                "capsules": capsules_data,
                "page": page,
                "page_size": page_size
            }
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"获取用户胶囊失败: {str(e)}")