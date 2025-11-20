"""
登录服务测试模块
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Tuple, Optional

from app.services.login import LoginManager
from app.domain.user import RegisteredUser, AdminUser, GuestUser
from app.auth.jwt_handler import JWTHandler


class TestLoginManager:
    """登录管理器测试类"""

    @pytest.fixture
    def login_manager(self):
        """登录管理器fixture"""
        return LoginManager()

    @pytest.fixture
    def valid_login_data(self):
        """有效登录数据fixture"""
        return {
            "email_or_username": "test@example.com",
            "password_hash": "hashed_password"
        }

    @pytest.fixture
    def registered_user(self):
        """注册用户fixture"""
        user = Mock(spec=RegisteredUser)
        user.user_id = "user_001"
        user.email = "test@example.com"
        user.username = "testuser"
        user.nickname = "测试用户"
        user.password_hash = "hashed_password"
        user.is_active = True
        user.avatar_url = "/avatar.jpg"
        return user

    @pytest.fixture
    def admin_user(self):
        """管理员用户fixture"""
        user = Mock(spec=AdminUser)
        user.user_id = "admin_001"
        user.email = "admin@example.com"
        user.username = "admin"
        user.password_hash = "hashed_password"
        user.is_active = True
        user.avatar_url = "/admin_avatar.jpg"
        return user

    # @patch('app.services.login.JWTHandler')
    # def test_login_user_success(
    #     self,
    #     mock_jwt_handler,
    #     login_manager,
    #     valid_login_data,
    #     registered_user
    # ):
    #     """测试用户登录成功"""
    #     # 模拟用户查找成功
    #     login_manager.user_repository.get_user_by_email_or_username = Mock(return_value=registered_user)

    #     # 模拟更新最后登录时间
    #     login_manager.user_repository.update_user_last_login = Mock()

    #     # 模拟JWT令牌生成
    #     mock_jwt_handler.generate_access_token_from_user.return_value = "access_token"
    #     mock_jwt_handler.generate_refresh_token_from_user.return_value = "refresh_token"

    #     # 执行登录
    #     success, message, user_data = login_manager.login_user(**valid_login_data)

    #     # 验证结果
    #     assert success is True
    #     assert message == "登录成功"
    #     assert user_data is not None
    #     assert user_data["user_id"] == registered_user.user_id
    #     assert user_data["email"] == registered_user.email
    #     assert user_data["nickname"] == registered_user.nickname
    #     assert user_data["token"] == "access_token"
    #     assert user_data["refresh_token"] == "refresh_token"
    #     assert user_data["avatar"] == registered_user.avatar_url

    #     # 验证方法调用
    #     login_manager.user_repository.get_user_by_email_or_username.assert_called_once_with(
    #         valid_login_data["email_or_username"]
    #     )
    #     login_manager.user_repository.update_user_last_login.assert_called_once_with(
    #         registered_user.user_id
    #     )
    #     mock_jwt_handler.generate_access_token_from_user.assert_called_once_with(registered_user)
    #     mock_jwt_handler.generate_refresh_token_from_user.assert_called_once_with(registered_user)

    def test_login_user_not_found(
        self,
        login_manager,
        valid_login_data
    ):
        """测试用户不存在"""
        # 模拟用户不存在
        login_manager.user_repository.get_user_by_email_or_username = Mock(return_value=None)

        # 执行登录
        success, message, user_data = login_manager.login_user(**valid_login_data)

        # 验证结果
        assert success is False
        assert message == "用户不存在或密码错误"
        assert user_data is None

    def test_login_user_inactive_account(
        self,
        login_manager,
        valid_login_data,
        registered_user
    ):
        """测试用户账户未激活"""
        # 模拟用户账户未激活
        registered_user.is_active = False
        login_manager.user_repository.get_user_by_email_or_username = Mock(return_value=registered_user)

        # 执行登录
        success, message, user_data = login_manager.login_user(**valid_login_data)

        # 验证结果
        assert success is False
        assert message == "用户账户已被禁用或未激活"
        assert user_data is None

    def test_login_user_wrong_password(
        self,
        login_manager,
        valid_login_data,
        registered_user
    ):
        """测试密码错误"""
        # 模拟用户存在但密码不匹配
        login_manager.user_repository.get_user_by_email_or_username = Mock(return_value=registered_user)

        # 使用错误的密码哈希
        wrong_password_data = valid_login_data.copy()
        wrong_password_data["password_hash"] = "wrong_hashed_password"

        # 执行登录
        success, message, user_data = login_manager.login_user(**wrong_password_data)

        # 验证结果
        assert success is False
        assert message == "用户不存在或密码错误"
        assert user_data is None

    @patch('app.services.login.JWTHandler')
    def test_login_admin_user_success(
        self,
        mock_jwt_handler,
        login_manager,
        admin_user
    ):
        """测试管理员用户登录成功"""
        # 模拟管理员用户查找成功
        login_manager.user_repository.get_user_by_email_or_username = Mock(return_value=admin_user)

        # 模拟更新最后登录时间
        login_manager.user_repository.update_user_last_login = Mock()

        # 模拟JWT令牌生成
        mock_jwt_handler.generate_access_token_from_user.return_value = "access_token"
        mock_jwt_handler.generate_refresh_token_from_user.return_value = "refresh_token"

        # 执行登录
        login_data = {
            "email_or_username": admin_user.email,
            "password_hash": admin_user.password_hash
        }
        success, message, user_data = login_manager.login_user(**login_data)

        # 验证结果
        assert success is True
        assert message == "登录成功"
        assert user_data is not None
        assert user_data["user_id"] == admin_user.user_id
        assert user_data["email"] == admin_user.email
        assert user_data["nickname"] == admin_user.username  # 管理员使用username作为nickname
        assert user_data["token"] == "access_token"
        assert user_data["refresh_token"] == "refresh_token"
        assert user_data["avatar"] is None

    @patch('app.services.login.JWTHandler')
    def test_login_user_with_username(
        self,
        mock_jwt_handler,
        login_manager,
        registered_user
    ):
        """测试使用用户名登录"""
        # 模拟使用用户名查找用户
        login_manager.user_repository.get_user_by_email_or_username = Mock(return_value=registered_user)

        # 模拟更新最后登录时间
        login_manager.user_repository.update_user_last_login = Mock()

        # 模拟JWT令牌生成
        mock_jwt_handler.generate_access_token_from_user.return_value = "access_token"
        mock_jwt_handler.generate_refresh_token_from_user.return_value = "refresh_token"

        # 使用用户名登录
        login_data = {
            "email_or_username": registered_user.username,
            "password_hash": registered_user.password_hash
        }
        success, message, user_data = login_manager.login_user(**login_data)

        # 验证结果
        assert success is True
        assert message == "登录成功"
        assert user_data is not None

        # 验证使用用户名进行查找
        login_manager.user_repository.get_user_by_email_or_username.assert_called_once_with(
            registered_user.username
        )

    def test_login_user_exception_handling(
        self,
        login_manager,
        valid_login_data
    ):
        """测试登录过程中的异常处理"""
        # 模拟数据库异常
        login_manager.user_repository.get_user_by_email_or_username = Mock(
            side_effect=Exception("数据库连接失败")
        )

        # 执行登录
        success, message, user_data = login_manager.login_user(**valid_login_data)

        # 验证结果
        assert success is False
        assert "登录失败" in message
        assert user_data is None

    # @patch('app.services.login.JWTHandler')
    # def test_login_user_last_login_update_failure(
    #     self,
    #     mock_jwt_handler,
    #     login_manager,
    #     valid_login_data,
    #     registered_user
    # ):
    #     """测试最后登录时间更新失败"""
    #     # 模拟用户查找成功
    #     login_manager.user_repository.get_user_by_email_or_username = Mock(return_value=registered_user)

    #     # 模拟更新最后登录时间失败
    #     login_manager.user_repository.update_user_last_login = Mock(
    #         side_effect=Exception("更新失败")
    #     )

    #     # 模拟JWT令牌生成
    #     mock_jwt_handler.generate_access_token_from_user.return_value = "access_token"
    #     mock_jwt_handler.generate_refresh_token_from_user.return_value = "refresh_token"

    #     # 执行登录
    #     success, message, user_data = login_manager.login_user(**valid_login_data)

    #     # 验证结果 - 即使更新最后登录时间失败，登录仍然应该成功
    #     assert success is True
    #     assert message == "登录成功"
    #     assert user_data is not None

    @patch('app.services.login.JWTHandler')
    def test_login_user_jwt_generation_failure(
        self,
        mock_jwt_handler,
        login_manager,
        valid_login_data,
        registered_user
    ):
        """测试JWT令牌生成失败"""
        # 模拟用户查找成功
        login_manager.user_repository.get_user_by_email_or_username = Mock(return_value=registered_user)

        # 模拟更新最后登录时间
        login_manager.user_repository.update_user_last_login = Mock()

        # 模拟JWT令牌生成失败
        mock_jwt_handler.generate_access_token_from_user.side_effect = Exception("JWT生成失败")

        # 执行登录
        success, message, user_data = login_manager.login_user(**valid_login_data)

        # 验证结果
        assert success is False
        assert "登录失败" in message
        assert user_data is None

    def test_login_user_empty_credentials(
        self,
        login_manager
    ):
        """测试空凭据登录"""
        # 执行登录
        success, message, user_data = login_manager.login_user("", "")

        # 验证结果
        assert success is False
        assert "用户不存在或密码错误" in message
        assert user_data is None

    @patch('app.services.login.JWTHandler')
    def test_login_user_special_characters_in_username(
        self,
        mock_jwt_handler,
        login_manager,
        registered_user
    ):
        """测试用户名包含特殊字符的登录"""
        # 模拟用户查找成功
        login_manager.user_repository.get_user_by_email_or_username = Mock(return_value=registered_user)

        # 模拟更新最后登录时间
        login_manager.user_repository.update_user_last_login = Mock()

        # 模拟JWT令牌生成
        mock_jwt_handler.generate_access_token_from_user.return_value = "access_token"
        mock_jwt_handler.generate_refresh_token_from_user.return_value = "refresh_token"

        # 使用包含特殊字符的用户名登录
        special_username = "user.name-with_dots"
        login_data = {
            "email_or_username": special_username,
            "password_hash": registered_user.password_hash
        }
        success, message, user_data = login_manager.login_user(**login_data)

        # 验证结果
        assert success is True
        assert message == "登录成功"
        assert user_data is not None

        # 验证使用特殊用户名进行查找
        login_manager.user_repository.get_user_by_email_or_username.assert_called_once_with(
            special_username
        )