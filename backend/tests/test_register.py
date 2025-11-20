"""
注册服务测试模块
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Tuple, Optional

from app.services.register import RegisterManager
from app.domain.user import RegisteredUser, AdminUser
from app.auth.password import PasswordManager
from app.auth.jwt_handler import JWTHandler


class TestRegisterManager:
    """注册管理器测试类"""

    @pytest.fixture
    def register_manager(self):
        """注册管理器fixture"""
        return RegisterManager()

    @pytest.fixture
    def valid_user_data(self):
        """有效用户数据fixture"""
        return {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "nickname": "测试用户",
            "verify_code": "123456",
            "campus_id": "20230001"
        }

    @patch('app.services.register.verify_code_manager')
    @patch('app.services.register.PasswordManager')
    @patch('app.services.register.JWTHandler')
    def test_register_user_success(
        self,
        mock_jwt_handler,
        mock_password_manager,
        mock_verify_code_manager,
        register_manager,
        valid_user_data
    ):
        """测试用户注册成功"""
        # 模拟验证码验证成功
        mock_verify_code_manager.verify_code.return_value = (True, "验证成功")

        # 模拟密码哈希成功
        mock_password_manager.hash_password.return_value = (True, "hashed_password")

        # 模拟用户仓库
        mock_user = Mock(spec=RegisteredUser)
        mock_user.user_id = "user_001"
        mock_user.email = valid_user_data["email"]
        mock_user.nickname = valid_user_data["nickname"]
        mock_user.avatar_url = None

        register_manager.user_repository.get_user_by_email_or_username = Mock(return_value=None)
        register_manager.user_repository.get_user_by_student_id = Mock(return_value=None)
        register_manager.user_repository.create_user = Mock(return_value=mock_user)

        # 模拟JWT令牌生成
        mock_jwt_handler.generate_access_token_from_user.return_value = "access_token"
        mock_jwt_handler.generate_refresh_token_from_user.return_value = "refresh_token"

        # 执行注册
        success, message, user_data = register_manager.register_user(**valid_user_data)

        # 验证结果
        assert success is True
        assert message == "注册成功"
        assert user_data is not None
        assert user_data["user_id"] == "user_001"
        assert user_data["email"] == valid_user_data["email"]
        assert user_data["nickname"] == valid_user_data["nickname"]
        assert user_data["token"] == "access_token"
        assert user_data["refresh_token"] == "refresh_token"

        # 验证方法调用
        mock_verify_code_manager.verify_code.assert_called_once_with(
            valid_user_data["email"],
            valid_user_data["verify_code"]
        )
        mock_password_manager.hash_password.assert_called_once_with(valid_user_data["password"])
        register_manager.user_repository.create_user.assert_called_once()

    @patch('app.services.register.verify_code_manager')
    def test_register_user_verify_code_failure(
        self,
        mock_verify_code_manager,
        register_manager,
        valid_user_data
    ):
        """测试验证码验证失败"""
        # 模拟验证码验证失败
        mock_verify_code_manager.verify_code.return_value = (False, "验证码错误")

        # 执行注册
        success, message, user_data = register_manager.register_user(**valid_user_data)

        # 验证结果
        assert success is False
        assert message == "验证码错误"
        assert user_data is None

        # 验证邮箱检查未被调用
        # register_manager.user_repository.get_user_by_email_or_username.assert_not_called()

    @patch('app.services.register.verify_code_manager')
    def test_register_user_email_already_exists(
        self,
        mock_verify_code_manager,
        register_manager,
        valid_user_data
    ):
        """测试邮箱已存在"""
        # 模拟验证码验证成功
        mock_verify_code_manager.verify_code.return_value = (True, "验证成功")

        # 模拟邮箱已存在
        existing_user = Mock(spec=RegisteredUser)
        register_manager.user_repository.get_user_by_email_or_username = Mock(return_value=existing_user)

        # 执行注册
        success, message, user_data = register_manager.register_user(**valid_user_data)

        # 验证结果
        assert success is False
        assert message == "该邮箱或用户名已被注册"
        assert user_data is None

        # 验证学号检查未被调用
        # register_manager.user_repository.get_user_by_student_id.assert_not_called()

    @patch('app.services.register.verify_code_manager')
    def test_register_user_student_id_already_exists(
        self,
        mock_verify_code_manager,
        register_manager,
        valid_user_data
    ):
        """测试学号已存在"""
        # 模拟验证码验证成功
        mock_verify_code_manager.verify_code.return_value = (True, "验证成功")

        # 模拟邮箱不存在但学号已存在
        register_manager.user_repository.get_user_by_email_or_username = Mock(return_value=None)
        existing_student = Mock(spec=RegisteredUser)
        register_manager.user_repository.get_user_by_student_id = Mock(return_value=existing_student)

        # 执行注册
        success, message, user_data = register_manager.register_user(**valid_user_data)

        # 验证结果
        assert success is False
        assert message == "该id已被注册"
        assert user_data is None

    @patch('app.services.register.verify_code_manager')
    @patch('app.services.register.PasswordManager')
    def test_register_user_password_hash_failure(
        self,
        mock_password_manager,
        mock_verify_code_manager,
        register_manager,
        valid_user_data
    ):
        """测试密码哈希失败"""
        # 模拟验证码验证成功
        mock_verify_code_manager.verify_code.return_value = (True, "验证成功")

        # 模拟密码哈希失败
        mock_password_manager.hash_password.return_value = (False, "密码哈希失败")

        # 模拟邮箱和学号都不存在
        register_manager.user_repository.get_user_by_email_or_username = Mock(return_value=None)
        register_manager.user_repository.get_user_by_student_id = Mock(return_value=None)

        # 执行注册
        success, message, user_data = register_manager.register_user(**valid_user_data)

        # 验证结果
        assert success is False
        assert message == "密码哈希失败"
        assert user_data is None

    @patch('app.services.register.verify_code_manager')
    @patch('app.services.register.PasswordManager')
    def test_register_user_creation_failure(
        self,
        mock_password_manager,
        mock_verify_code_manager,
        register_manager,
        valid_user_data
    ):
        """测试用户创建失败"""
        # 模拟验证码验证成功
        mock_verify_code_manager.verify_code.return_value = (True, "验证成功")

        # 模拟密码哈希成功
        mock_password_manager.hash_password.return_value = (True, "hashed_password")

        # 模拟邮箱和学号都不存在
        register_manager.user_repository.get_user_by_email_or_username = Mock(return_value=None)
        register_manager.user_repository.get_user_by_student_id = Mock(return_value=None)

        # 模拟用户创建失败
        register_manager.user_repository.create_user = Mock(side_effect=Exception("数据库错误"))

        # 执行注册
        success, message, user_data = register_manager.register_user(**valid_user_data)

        # 验证结果
        assert success is False
        assert message == "用户创建失败: 数据库错误"
        assert user_data is None

    @patch('app.services.register.verify_code_manager')
    @patch('app.services.register.PasswordManager')
    def test_register_user_admin_user_creation_blocked(
        self,
        mock_password_manager,
        mock_verify_code_manager,
        register_manager,
        valid_user_data
    ):
        """测试阻止管理员用户注册"""
        # 模拟验证码验证成功
        mock_verify_code_manager.verify_code.return_value = (True, "验证成功")

        # 模拟密码哈希成功
        mock_password_manager.hash_password.return_value = (True, "hashed_password")

        # 模拟邮箱和学号都不存在
        register_manager.user_repository.get_user_by_email_or_username = Mock(return_value=None)
        register_manager.user_repository.get_user_by_student_id = Mock(return_value=None)

        # 模拟创建管理员用户（应该被阻止）
        mock_admin_user = Mock(spec=AdminUser)
        register_manager.user_repository.create_user = Mock(return_value=mock_admin_user)

        # 执行注册
        success, message, user_data = register_manager.register_user(**valid_user_data)

        # 验证结果
        assert success is False
        assert "无法注册管理员用户" in message
        assert user_data is None

    def test_register_user_without_campus_id(
        self,
        register_manager,
        valid_user_data
    ):
        """测试不带学号的用户注册"""
        # 移除学号
        valid_user_data["campus_id"] = None

        # 模拟验证码验证成功
        with patch('app.services.register.verify_code_manager') as mock_verify_code_manager:
            mock_verify_code_manager.verify_code.return_value = (True, "验证成功")

            # 模拟密码哈希成功
            with patch('app.services.register.PasswordManager') as mock_password_manager:
                mock_password_manager.hash_password.return_value = (True, "hashed_password")

                # 模拟用户创建成功
                mock_user = Mock(spec=RegisteredUser)
                mock_user.user_id = "user_001"
                mock_user.email = valid_user_data["email"]
                mock_user.nickname = valid_user_data["nickname"]
                mock_user.avatar_url = None

                register_manager.user_repository.get_user_by_email_or_username = Mock(return_value=None)
                register_manager.user_repository.create_user = Mock(return_value=mock_user)

                # 模拟JWT令牌生成
                with patch('app.services.register.JWTHandler') as mock_jwt_handler:
                    mock_jwt_handler.generate_access_token_from_user.return_value = "access_token"
                    mock_jwt_handler.generate_refresh_token_from_user.return_value = "refresh_token"

                    # 执行注册
                    success, message, user_data = register_manager.register_user(**valid_user_data)

                    # 验证结果
                    assert success is True
                    assert user_data is not None

                    # 验证学号检查未被调用
                    # register_manager.user_repository.get_user_by_student_id.assert_not_called()

    def test_check_email_availability_available(self, register_manager):
        """测试邮箱可用性检查 - 邮箱可用"""
        # 模拟邮箱不存在
        register_manager.user_repository.get_user_by_email_or_username = Mock(return_value=None)

        # 执行检查
        is_available, message = register_manager.check_email_availability("new@example.com")

        # 验证结果
        assert is_available is True
        assert message == "邮箱可用"

    def test_check_email_availability_unavailable(self, register_manager):
        """测试邮箱可用性检查 - 邮箱不可用"""
        # 模拟邮箱已存在
        existing_user = Mock(spec=RegisteredUser)
        register_manager.user_repository.get_user_by_email_or_username = Mock(return_value=existing_user)

        # 执行检查
        is_available, message = register_manager.check_email_availability("existing@example.com")

        # 验证结果
        assert is_available is False
        assert message == "该邮箱或用户名已被注册"

    def test_check_email_availability_error(self, register_manager):
        """测试邮箱可用性检查 - 发生错误"""
        # 模拟数据库错误
        register_manager.user_repository.get_user_by_email_or_username = Mock(side_effect=Exception("数据库连接失败"))

        # 执行检查
        is_available, message = register_manager.check_email_availability("test@example.com")

        # 验证结果
        assert is_available is False
        assert "检查邮箱可用性失败" in message

    def test_check_student_id_availability_available(self, register_manager):
        """测试学号可用性检查 - 学号可用"""
        # 模拟学号不存在
        register_manager.user_repository.get_user_by_student_id = Mock(return_value=None)

        # 执行检查
        is_available, message = register_manager.check_student_id_availability("20230001")

        # 验证结果
        assert is_available is True
        assert message == "学号可用"

    def test_check_student_id_availability_unavailable(self, register_manager):
        """测试学号可用性检查 - 学号不可用"""
        # 模拟学号已存在
        existing_user = Mock(spec=RegisteredUser)
        register_manager.user_repository.get_user_by_student_id = Mock(return_value=existing_user)

        # 执行检查
        is_available, message = register_manager.check_student_id_availability("20230001")

        # 验证结果
        assert is_available is False
        assert message == "该学号已被注册"

    def test_check_student_id_availability_error(self, register_manager):
        """测试学号可用性检查 - 发生错误"""
        # 模拟数据库错误
        register_manager.user_repository.get_user_by_student_id = Mock(side_effect=Exception("数据库连接失败"))

        # 执行检查
        is_available, message = register_manager.check_student_id_availability("20230001")

        # 验证结果
        assert is_available is False
        assert "检查学号可用性失败" in message