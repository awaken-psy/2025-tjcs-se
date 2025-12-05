"""
用户服务层 - 处理用户相关的业务逻辑
"""
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from app.database.repositories.user_repository import UserRepository
from app.domain.user import AuthorizedUser, RegisteredUser, AdminUser
from app.model.user import UserProfile, UpdateUserRequest, UserStats


class UserService:
    """用户服务类 - 处理用户相关的业务逻辑"""

    def __init__(self):
        """初始化用户服务"""
        self.user_repository = UserRepository()

    def get_user_profile(self, user_id: int) -> Tuple[bool, Optional[UserProfile], str]:
        """
        获取用户资料

        Args:
            user_id: 用户ID

        Returns:
            (是否成功, 用户资料, 错误信息)
        """
        try:
            # 从数据库获取用户信息
            user = self.user_repository.get_user_by_id(user_id)
            if not user:
                return False, None, "用户不存在"

            # 构建用户统计信息（临时数据，后续可以从数据库统计）
            stats = UserStats(
                created_capsules=0,  # TODO: 从胶囊表统计
                unlocked_capsules=0,  # TODO: 从解锁记录表统计
                collected_capsules=0,  # TODO: 从收集表统计
                friends_count=0  # TODO: 从好友关系表统计
            )

            # 构建用户资料响应
            user_profile = UserProfile(
                user_id=user.user_id,
                email=user.email,
                nickname=user.nickname,
                created_at=user.created_at,
                avatar=getattr(user, 'avatar_url', None),
                bio=getattr(user, 'bio', None),
                stats=stats
            )

            return True, user_profile, "获取用户资料成功"

        except Exception as e:
            return False, None, f"获取用户资料失败: {str(e)}"

    def update_user_profile(
        self,
        user_id: int,
        update_request: UpdateUserRequest
    ) -> Tuple[bool, Optional[UserProfile], str]:
        """
        更新用户资料

        Args:
            user_id: 用户ID
            update_request: 更新请求

        Returns:
            (是否成功, 更新后的用户资料, 错误信息)
        """
        try:
            # 获取当前用户信息
            current_user = self.user_repository.get_user_by_id(user_id)
            if not current_user:
                return False, None, "用户不存在"

            # 准备更新数据
            update_data = {}
            if update_request.nickname is not None:
                if not update_request.nickname.strip():
                    return False, None, "昵称不能为空"
                update_data['nickname'] = update_request.nickname.strip()

            if update_request.avatar is not None:
                update_data['avatar_url'] = update_request.avatar

            if update_request.bio is not None:
                update_data['bio'] = update_request.bio.strip() if update_request.bio else None

            if not update_data:
                return False, None, "没有需要更新的字段"

            # 执行更新
            success = self.user_repository.update_user(user_id, update_data)
            if not success:
                return False, None, "更新用户资料失败"

            # 获取更新后的用户信息
            updated_user = self.user_repository.get_user_by_id(user_id)
            if not updated_user:
                return False, None, "更新后获取用户信息失败"

            # 构建用户统计信息
            stats = UserStats(
                created_capsules=0,  # TODO: 从胶囊表统计
                unlocked_capsules=0,  # TODO: 从解锁记录表统计
                collected_capsules=0,  # TODO: 从收集表统计
                friends_count=0  # TODO: 从好友关系表统计
            )

            # 构建更新后的用户资料响应
            user_profile = UserProfile(
                user_id=updated_user.user_id,
                email=updated_user.email,
                nickname=updated_user.nickname,
                created_at=updated_user.created_at,
                avatar=getattr(updated_user, 'avatar_url', None),
                bio=getattr(updated_user, 'bio', None),
                stats=stats
            )

            return True, user_profile, "更新用户资料成功"

        except Exception as e:
            return False, None, f"更新用户资料失败: {str(e)}"

    def get_user_by_id(self, user_id: int) -> Optional[AuthorizedUser]:
        """
        根据用户ID获取用户领域模型

        Args:
            user_id: 用户ID

        Returns:
            用户领域模型或None
        """
        return self.user_repository.get_user_by_id(user_id)

    def validate_user_permission(self, user: AuthorizedUser, required_permission: str) -> bool:
        """
        验证用户权限

        Args:
            user: 用户领域模型
            required_permission: 需要的权限

        Returns:
            是否有权限
        """
        from app.domain.user import Permission

        # 检查用户是否有指定权限
        if hasattr(user, 'has_permission'):
            return user.has_permission(Permission(required_permission))

        return False