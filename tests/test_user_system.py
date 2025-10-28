"""
用户系统单元测试
"""
import pytest
from datetime import datetime, timedelta, timezone
from models.core.user import (
    UserRole, Permission, AccessUser, AuthenticatedUser, AdminUser,
    UserFactory, RolePermissionMap
)
from auth.permission_manager import PermissionManager


class TestUserModel:
    """用户模型测试"""
    
    def test_guest_user_creation(self):
        """测试访客用户创建"""
        guest = UserFactory.create_guest_user()
        assert guest.role == UserRole.GUEST
        assert guest.username == "访客"
        assert Permission.READ_CAPSULE in guest.permissions
        assert Permission.CREATE_CAPSULE not in guest.permissions
    
    def test_authenticated_user_creation(self):
        """测试认证用户创建"""
        user = UserFactory.create_authenticated_user(
            user_id="user_001",
            username="测试用户",
            email="test@test.com"
        )
        assert user.role == UserRole.USER
        assert user.username == "测试用户"
        assert user.email == "test@test.com"
        assert Permission.CREATE_CAPSULE in user.permissions
        assert Permission.READ_CAPSULE in user.permissions
    
    def test_admin_user_creation(self):
        """测试管理员用户创建"""
        admin = UserFactory.create_admin_user(
            user_id="admin_001",
            username="管理员"
        )
        assert admin.role == UserRole.ADMIN
        assert Permission.CREATE_CAPSULE in admin.permissions
        assert Permission.MANAGE_PERMISSIONS in admin.permissions
        assert Permission.DELETE_USER in admin.permissions
    
    def test_user_permission_check(self):
        """测试用户权限检查"""
        user = UserFactory.create_authenticated_user(
            user_id="user_001",
            username="测试用户"
        )
        
        assert user.has_permission(Permission.CREATE_CAPSULE)
        assert user.has_permission(Permission.READ_CAPSULE)
        assert not user.has_permission(Permission.MANAGE_PERMISSIONS)
        assert not user.has_permission(Permission.DELETE_USER)
    
    def test_authenticated_user_can_edit_own_capsule(self):
        """测试认证用户可以编辑自己的胶囊"""
        user = UserFactory.create_authenticated_user(
            user_id="user_001",
            username="测试用户"
        )
        
        # 可以编辑自己的胶囊
        assert user.can_edit_capsule("user_001")
        
        # 不能编辑他人的胶囊
        assert not user.can_edit_capsule("user_002")
    
    def test_admin_can_edit_any_capsule(self):
        """测试管理员可以编辑任何胶囊"""
        admin = UserFactory.create_admin_user(
            user_id="admin_001",
            username="管理员"
        )
        
        # 可以编辑任何胶囊
        assert admin.can_edit_capsule("user_001")
        assert admin.can_edit_capsule("user_002")


class TestPermissionManager:
    """权限管理器测试"""
    
    def test_check_permission(self):
        """测试权限检查"""
        user = UserFactory.create_authenticated_user(
            user_id="user_001",
            username="测试用户"
        )
        
        assert PermissionManager.check_permission(user, Permission.CREATE_CAPSULE)
        assert not PermissionManager.check_permission(user, Permission.DELETE_USER)
    
    def test_check_any_permission(self):
        """测试检查任意权限"""
        user = UserFactory.create_authenticated_user(
            user_id="user_001",
            username="测试用户"
        )
        
        perms = {Permission.CREATE_CAPSULE, Permission.DELETE_USER}
        assert PermissionManager.check_any_permission(user, perms)
        
        perms = {Permission.DELETE_USER, Permission.MANAGE_PERMISSIONS}
        assert not PermissionManager.check_any_permission(user, perms)
    
    def test_check_all_permissions(self):
        """测试检查全部权限"""
        admin = UserFactory.create_admin_user(
            user_id="admin_001",
            username="管理员"
        )
        
        perms = {Permission.CREATE_CAPSULE, Permission.DELETE_USER}
        assert PermissionManager.check_all_permissions(admin, perms)
        
        user = UserFactory.create_authenticated_user(
            user_id="user_001",
            username="测试用户"
        )
        perms = {Permission.CREATE_CAPSULE, Permission.DELETE_USER}
        assert not PermissionManager.check_all_permissions(user, perms)
    
    def test_can_create_capsule(self):
        """测试创建胶囊权限"""
        guest = UserFactory.create_guest_user()
        user = UserFactory.create_authenticated_user(
            user_id="user_001",
            username="测试用户"
        )
        
        assert not PermissionManager.can_create_capsule(guest)
        assert PermissionManager.can_create_capsule(user)
    
    def test_can_update_capsule(self):
        """测试更新胶囊权限"""
        user = UserFactory.create_authenticated_user(
            user_id="user_001",
            username="测试用户"
        )
        admin = UserFactory.create_admin_user(
            user_id="admin_001",
            username="管理员"
        )
        
        # 用户可以更新自己的胶囊
        assert PermissionManager.can_update_capsule(user, "user_001")
        assert not PermissionManager.can_update_capsule(user, "user_002")
        
        # 管理员可以更新任何胶囊
        assert PermissionManager.can_update_capsule(admin, "user_001")
        assert PermissionManager.can_update_capsule(admin, "user_002")
    
    def test_can_delete_capsule(self):
        """测试删除胶囊权限"""
        user = UserFactory.create_authenticated_user(
            user_id="user_001",
            username="测试用户"
        )
        admin = UserFactory.create_admin_user(
            user_id="admin_001",
            username="管理员"
        )
        
        # 用户可以删除自己的胶囊
        assert PermissionManager.can_delete_capsule(user, "user_001")
        assert not PermissionManager.can_delete_capsule(user, "user_002")
        
        # 管理员可以删除任何胶囊
        assert PermissionManager.can_delete_capsule(admin, "user_001")
        assert PermissionManager.can_delete_capsule(admin, "user_002")
    
    def test_is_admin(self):
        """测试管理员检查"""
        user = UserFactory.create_authenticated_user(
            user_id="user_001",
            username="测试用户"
        )
        admin = UserFactory.create_admin_user(
            user_id="admin_001",
            username="管理员"
        )
        
        assert not PermissionManager.is_admin(user)
        assert PermissionManager.is_admin(admin)


class TestRolePermissionMap:
    """角色权限映射测试"""
    
    def test_guest_permissions(self):
        """测试访客权限"""
        perms = RolePermissionMap.get_role_permissions(UserRole.GUEST)
        assert Permission.READ_CAPSULE in perms
        assert Permission.CREATE_CAPSULE not in perms
        assert len(perms) == 1
    
    def test_user_permissions(self):
        """测试普通用户权限"""
        perms = RolePermissionMap.get_role_permissions(UserRole.USER)
        assert Permission.READ_CAPSULE in perms
        assert Permission.CREATE_CAPSULE in perms
        assert Permission.UNLOCK_CAPSULE in perms
        assert Permission.DELETE_USER not in perms
    
    def test_admin_permissions(self):
        """测试管理员权限"""
        perms = RolePermissionMap.get_role_permissions(UserRole.ADMIN)
        assert Permission.READ_CAPSULE in perms
        assert Permission.CREATE_CAPSULE in perms
        assert Permission.DELETE_USER in perms
        assert Permission.MANAGE_PERMISSIONS in perms
        assert len(perms) > len(RolePermissionMap.get_role_permissions(UserRole.USER))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
