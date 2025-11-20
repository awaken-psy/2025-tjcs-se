"""
验证码服务测试模块
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Tuple, Optional

from app.services.verifycode import EmailVerifyCodeManager, VerifyCode


class TestEmailVerifyCodeManager:
    """邮箱验证码管理器测试类"""

    @pytest.fixture
    def verify_code_manager(self):
        """验证码管理器fixture"""
        return EmailVerifyCodeManager(
            smtp_server="smtp.test.com",
            smtp_port=465,
            sender_email="test@test.com",
            sender_password="test_password",
            expire_minutes=10
        )

    @pytest.fixture
    def test_email(self):
        """测试邮箱fixture"""
        return "test@example.com"

    @pytest.fixture
    def test_verify_code(self):
        """测试验证码fixture"""
        return "123456"

    def test_generate_code(self, verify_code_manager):
        """测试验证码生成"""
        # 生成验证码
        code = verify_code_manager._generate_code()

        # 验证结果
        assert len(code) == 6
        assert code.isdigit()

        # 测试不同长度的验证码
        code_4 = verify_code_manager._generate_code(4)
        assert len(code_4) == 4
        assert code_4.isdigit()

        code_8 = verify_code_manager._generate_code(8)
        assert len(code_8) == 8
        assert code_8.isdigit()

    @patch('app.services.verifycode.smtplib.SMTP_SSL')
    def test_send_email_success(
        self,
        mock_smtp,
        verify_code_manager
    ):
        """测试邮件发送成功"""
        # 模拟SMTP连接和登录
        mock_server = Mock()
        mock_smtp.return_value.__enter__ = Mock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = Mock()

        # 执行邮件发送
        success = verify_code_manager._send_email(
            recipient="test@example.com",
            subject="测试主题",
            content="测试内容"
        )

        # 验证结果
        assert success is True
        mock_server.login.assert_called_once_with(
            verify_code_manager.sender,
            verify_code_manager.sender_password
        )
        mock_server.sendmail.assert_called_once()

    @patch('app.services.verifycode.smtplib.SMTP_SSL')
    def test_send_email_failure(
        self,
        mock_smtp,
        verify_code_manager
    ):
        """测试邮件发送失败"""
        # 模拟SMTP连接失败
        mock_smtp.side_effect = Exception("SMTP连接失败")

        # 执行邮件发送
        success = verify_code_manager._send_email(
            recipient="test@example.com",
            subject="测试主题",
            content="测试内容"
        )

        # 验证结果
        assert success is False

    @patch('app.services.verifycode.EmailVerifyCodeManager._send_email')
    def test_send_verify_code_success(
        self,
        mock_send_email,
        verify_code_manager,
        test_email
    ):
        """测试验证码发送成功"""
        # 模拟邮件发送成功
        mock_send_email.return_value = True

        # 执行验证码发送
        success, message = verify_code_manager.send_verify_code(test_email)

        # 验证结果
        assert success is True
        assert message == "验证码发送成功"
        assert test_email in verify_code_manager.verify_codes

        # 验证验证码格式
        verify_code = verify_code_manager.verify_codes[test_email]
        assert verify_code.email == test_email
        assert len(verify_code.code) == 6
        assert verify_code.code.isdigit()
        assert verify_code.expire_time > time.time()

        # 验证邮件发送被调用
        mock_send_email.assert_called_once()

    @patch('app.services.verifycode.EmailVerifyCodeManager._send_email')
    def test_send_verify_code_email_failure(
        self,
        mock_send_email,
        verify_code_manager,
        test_email
    ):
        """测试验证码邮件发送失败"""
        # 模拟邮件发送失败
        mock_send_email.return_value = False

        # 执行验证码发送
        success, message = verify_code_manager.send_verify_code(test_email)

        # 验证结果
        assert success is False
        assert message == "验证码发送失败，请检查邮箱地址或稍后重试"
        assert test_email not in verify_code_manager.verify_codes

    @patch('app.services.verifycode.EmailVerifyCodeManager._send_email')
    def test_send_verify_code_cooldown(
        self,
        mock_send_email,
        verify_code_manager,
        test_email
    ):
        """测试验证码发送冷却时间"""
        # 模拟第一次发送成功
        mock_send_email.return_value = True

        # 第一次发送
        success1, message1 = verify_code_manager.send_verify_code(test_email)
        assert success1 is True

        # 立即尝试第二次发送（在冷却时间内）
        success2, message2 = verify_code_manager.send_verify_code(test_email)

        # 验证第二次发送被阻止
        assert success2 is False
        assert message2 == "验证码发送过于频繁，请稍后再试"

        # 验证邮件发送只被调用了一次
        assert mock_send_email.call_count == 1

    @patch('app.services.verifycode.EmailVerifyCodeManager._send_email')
    @patch('app.services.verifycode.time')
    def test_send_verify_code_after_cooldown(
        self,
        mock_time,
        mock_send_email,
        verify_code_manager,
        test_email
    ):
        """测试冷却时间后可以重新发送验证码"""
        # 模拟邮件发送成功
        mock_send_email.return_value = True

        # 模拟时间流逝
        current_time = 1000.0
        mock_time.time.return_value = current_time

        # 第一次发送
        success1, message1 = verify_code_manager.send_verify_code(test_email)
        assert success1 is True

        # 模拟时间过去61秒（超过60秒冷却时间）
        mock_time.time.return_value = current_time + 61

        # 第二次发送
        success2, message2 = verify_code_manager.send_verify_code(test_email)

        # 验证第二次发送成功
        assert success2 is True
        assert message2 == "验证码发送成功"

        # 验证邮件发送被调用了两次
        assert mock_send_email.call_count == 2

    def test_verify_code_success(
        self,
        verify_code_manager,
        test_email,
        test_verify_code
    ):
        """测试验证码验证成功"""
        # 手动添加验证码记录
        expire_time = time.time() + 600  # 10分钟后过期
        verify_code = VerifyCode(test_email, test_verify_code, expire_time)
        verify_code_manager.verify_codes[test_email] = verify_code

        # 执行验证
        success, message = verify_code_manager.verify_code(test_email, test_verify_code)

        # 验证结果
        assert success is True
        assert message == "验证成功"
        assert test_email not in verify_code_manager.verify_codes  # 验证成功后应删除记录

    def test_verify_code_not_exists(
        self,
        verify_code_manager,
        test_email,
        test_verify_code
    ):
        """测试验证码不存在"""
        # 执行验证
        success, message = verify_code_manager.verify_code(test_email, test_verify_code)

        # 验证结果
        assert success is False
        assert message == "验证码不存在或已过期"

    def test_verify_code_expired(
        self,
        verify_code_manager,
        test_email,
        test_verify_code
    ):
        """测试验证码已过期"""
        # 手动添加已过期的验证码记录
        expire_time = time.time() - 1  # 1秒前过期
        verify_code = VerifyCode(test_email, test_verify_code, expire_time)
        verify_code_manager.verify_codes[test_email] = verify_code

        # 执行验证
        success, message = verify_code_manager.verify_code(test_email, test_verify_code)

        # 验证结果
        assert success is False
        assert message == "验证码不存在或已过期"
        assert test_email not in verify_code_manager.verify_codes  # 过期验证码应被清理

    def test_verify_code_wrong_code(
        self,
        verify_code_manager,
        test_email,
        test_verify_code
    ):
        """测试验证码错误"""
        # 手动添加验证码记录
        expire_time = time.time() + 600  # 10分钟后过期
        verify_code = VerifyCode(test_email, test_verify_code, expire_time)
        verify_code_manager.verify_codes[test_email] = verify_code

        # 使用错误的验证码执行验证
        success, message = verify_code_manager.verify_code(test_email, "wrong_code")

        # 验证结果
        assert success is False
        assert message == "验证码错误"
        assert test_email in verify_code_manager.verify_codes  # 验证失败不应删除记录

    def test_clean_expired_codes(
        self,
        verify_code_manager
    ):
        """测试清理过期验证码"""
        # 添加一些验证码记录
        current_time = time.time()

        # 未过期的验证码
        valid_code = VerifyCode("valid@example.com", "123456", current_time + 600)
        verify_code_manager.verify_codes["valid@example.com"] = valid_code

        # 已过期的验证码
        expired_code1 = VerifyCode("expired1@example.com", "111111", current_time - 1)
        expired_code2 = VerifyCode("expired2@example.com", "222222", current_time - 60)
        verify_code_manager.verify_codes["expired1@example.com"] = expired_code1
        verify_code_manager.verify_codes["expired2@example.com"] = expired_code2

        # 执行清理
        verify_code_manager._clean_expired_codes()

        # 验证结果
        assert "valid@example.com" in verify_code_manager.verify_codes
        assert "expired1@example.com" not in verify_code_manager.verify_codes
        assert "expired2@example.com" not in verify_code_manager.verify_codes

    def test_verify_code_auto_clean_expired(
        self,
        verify_code_manager,
        test_email,
        test_verify_code
    ):
        """测试验证码验证时自动清理过期验证码"""
        # 添加一些验证码记录
        current_time = time.time()

        # 未过期的验证码
        valid_code = VerifyCode("valid@example.com", "123456", current_time + 600)
        verify_code_manager.verify_codes["valid@example.com"] = valid_code

        # 已过期的验证码
        expired_code = VerifyCode("expired@example.com", "111111", current_time - 1)
        verify_code_manager.verify_codes["expired@example.com"] = expired_code

        # 执行验证（会触发自动清理）
        verify_code_manager.verify_code("valid@example.com", "123456")

        # 验证过期验证码已被清理
        assert "expired@example.com" not in verify_code_manager.verify_codes

    @patch('app.services.verifycode.EmailVerifyCodeManager._send_email')
    def test_send_verify_code_multiple_emails(
        self,
        mock_send_email,
        verify_code_manager
    ):
        """测试向多个邮箱发送验证码"""
        # 模拟邮件发送成功
        mock_send_email.return_value = True

        emails = ["user1@example.com", "user2@example.com", "user3@example.com"]

        # 向多个邮箱发送验证码
        for email in emails:
            success, message = verify_code_manager.send_verify_code(email)
            assert success is True

        # 验证所有邮箱都有验证码记录
        for email in emails:
            assert email in verify_code_manager.verify_codes

        # 验证邮件发送被调用了三次
        assert mock_send_email.call_count == 3

    def test_verify_code_case_sensitive(
        self,
        verify_code_manager,
        test_email
    ):
        """测试验证码大小写敏感"""
        # 手动添加验证码记录
        expire_time = time.time() + 600
        verify_code = VerifyCode(test_email, "AbCdEf", expire_time)
        verify_code_manager.verify_codes[test_email] = verify_code

        # 使用正确的大小写验证
        success1, message1 = verify_code_manager.verify_code(test_email, "AbCdEf")
        assert success1 is True

        # 重新添加验证码记录
        verify_code_manager.verify_codes[test_email] = VerifyCode(test_email, "AbCdEf", expire_time)

        # 使用不同大小写验证
        success2, message2 = verify_code_manager.verify_code(test_email, "abcdef")
        assert success2 is False
        assert message2 == "验证码错误"

    def test_verify_code_whitespace_handling(
        self,
        verify_code_manager,
        test_email
    ):
        """测试验证码空格处理"""
        # 手动添加验证码记录
        expire_time = time.time() + 600
        verify_code = VerifyCode(test_email, "123456", expire_time)
        verify_code_manager.verify_codes[test_email] = verify_code

        # 使用带空格的验证码验证
        success, message = verify_code_manager.verify_code(test_email, " 123456 ")

        # 验证结果 - 应该失败，因为验证码是精确匹配的
        assert success is False
        assert message == "验证码错误"

    @patch('app.services.verifycode.EmailVerifyCodeManager._send_email')
    def test_send_verify_code_invalid_email(
        self,
        mock_send_email,
        verify_code_manager
    ):
        """测试向无效邮箱发送验证码"""
        # 模拟邮件发送失败
        mock_send_email.return_value = False

        # 执行验证码发送
        success, message = verify_code_manager.send_verify_code("invalid-email")

        # 验证结果
        assert success is False
        assert "验证码发送失败" in message

    def test_verify_code_manager_initialization(self):
        """测试验证码管理器初始化"""
        manager = EmailVerifyCodeManager(
            smtp_server="smtp.example.com",
            smtp_port=587,
            sender_email="sender@example.com",
            sender_password="password",
            expire_minutes=5
        )

        # 验证初始化参数
        assert manager.smtp_server == "smtp.example.com"
        assert manager.smtp_port == 587
        assert manager.sender == "sender@example.com"
        assert manager.sender_password == "password"
        assert manager.expire_minutes == 5
        assert isinstance(manager.verify_codes, dict)
        assert len(manager.verify_codes) == 0