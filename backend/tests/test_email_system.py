#!/usr/bin/env python3
"""
邮件系统测试
测试多邮箱配置和发送功能
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.config import (
    get_email_config_by_domain,
    get_email_config_by_email,
    EMAIL_PROVIDERS,
    DEFAULT_EMAIL_CONFIG
)
from app.services.verifycode import EmailVerifyCodeManager


class TestEmailConfig:
    """测试邮箱配置功能"""

    def test_qq_email_config(self):
        """测试QQ邮箱配置"""
        config = get_email_config_by_domain("qq.com")

        assert config["smtp_server"] == "smtp.qq.com"
        assert config["smtp_port"] == 465
        assert config["sender_email"] == os.getenv("QQ_SENDER_EMAIL", "1461963552@qq.com")
        assert config["sender_password"] == os.getenv("QQ_SENDER_PASSWORD", "mmfpltiuvljzghfh")
        assert config["display_name"] == "时光胶囊·校园"

    def test_163_email_config(self):
        """测试163邮箱配置"""
        config = get_email_config_by_domain("163.com")

        assert config["smtp_server"] == "smtp.163.com"
        assert config["smtp_port"] == 465
        assert config["display_name"] == "时光胶囊·校园"

    def test_gmail_config(self):
        """测试Gmail配置"""
        config = get_email_config_by_domain("gmail.com")

        assert config["smtp_server"] == "smtp.gmail.com"
        assert config["smtp_port"] == 587
        assert config["display_name"] == "时光胶囊·校园"

    def test_tongji_email_config(self):
        """测试同济大学邮箱配置"""
        config = get_email_config_by_domain("tongji.edu.cn")

        assert config["smtp_server"] == "smtp.tongji.edu.cn"
        assert config["smtp_port"] == 465
        assert config["display_name"] == "时光胶囊·校园"

    def test_unknown_domain_config(self):
        """测试未知域名返回默认配置"""
        config = get_email_config_by_domain("unknown.com")

        assert config == DEFAULT_EMAIL_CONFIG

    def test_email_address_routing(self):
        """测试完整邮箱地址路由"""
        test_cases = [
            ("user@qq.com", "smtp.qq.com"),
            ("admin@163.com", "smtp.163.com"),
            ("student@tongji.edu.cn", "smtp.tongji.edu.cn"),
            ("user@gmail.com", "smtp.gmail.com"),
            ("test@unknown.com", DEFAULT_EMAIL_CONFIG["smtp_server"])
        ]

        for email, expected_smtp in test_cases:
            config = get_email_config_by_email(email)
            assert config["smtp_server"] == expected_smtp

    def test_invalid_email_address(self):
        """测试无效邮箱地址"""
        # 测试各种无效邮箱格式
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "",
            None
        ]

        for email in invalid_emails:
            config = get_email_config_by_email(email)
            assert config == DEFAULT_EMAIL_CONFIG


class TestEmailVerifyCodeManager:
    """测试验证码管理器"""

    @pytest.fixture
    def manager(self):
        """创建验证码管理器实例"""
        return EmailVerifyCodeManager(expire_minutes=1)

    def test_manager_initialization(self, manager):
        """测试管理器初始化"""
        assert manager.expire_minutes == 1
        assert manager.verify_codes == {}
        assert manager.executor._max_workers == 3
        assert manager.sending_locks == {}

    def test_generate_code(self, manager):
        """测试验证码生成"""
        code = manager._generate_code()
        assert len(code) == 6
        assert code.isdigit()

        code_custom = manager._generate_code(length=8)
        assert len(code_custom) == 8
        assert code_custom.isdigit()

    @patch('os.getenv')
    def test_send_verify_code_development_mode(self, mock_getenv, manager):
        """测试开发模式发送验证码"""
        # 设置开发模式
        mock_getenv.return_value = "development"

        success, message = manager.send_verify_code("test@example.com")

        assert success is True
        assert "开发模式" in message
        assert "123456" in message
        assert "test@example.com" in manager.verify_codes

    @patch('app.services.verifycode.get_email_config_by_email')
    @patch('app.services.verifycode.smtplib.SMTP_SSL')
    def test_send_email_success(self, mock_smtp, mock_config, manager):
        """测试邮件发送成功"""
        # 模拟邮箱配置
        mock_config.return_value = {
            "smtp_server": "smtp.qq.com",
            "smtp_port": 465,
            "sender_email": "test@qq.com",
            "sender_password": "test_password",
            "display_name": "时光胶囊·校园"
        }

        # 模拟SMTP服务器
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        success = manager._send_email("recipient@qq.com", "测试主题", "测试内容")

        assert success is True
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch('app.services.verifycode.get_email_config_by_email')
    @patch('app.services.verifycode.smtplib.SMTP_SSL')
    def test_send_email_failure(self, mock_smtp, mock_config, manager):
        """测试邮件发送失败"""
        # 模拟邮箱配置
        mock_config.return_value = {
            "smtp_server": "smtp.qq.com",
            "smtp_port": 465,
            "sender_email": "test@qq.com",
            "sender_password": "wrong_password",
            "display_name": "时光胶囊·校园"
        }

        # 模拟SMTP登录失败
        mock_smtp.return_value.__enter__.return_value.login.side_effect = Exception("认证失败")

        success = manager._send_email("recipient@qq.com", "测试主题", "测试内容")

        assert success is False

    def test_rate_limiting(self, manager):
        """测试发送频率限制"""
        with patch('os.getenv', return_value="development"):
            # 第一次发送
            success1, message1 = manager.send_verify_code("test@example.com")
            assert success1 is True

            # 立即再次发送（应该被限制）
            success2, message2 = manager.send_verify_code("test@example.com")
            assert success2 is False
            assert "频繁" in message2

    def test_code_verification(self, manager):
        """测试验证码验证"""
        with patch('os.getenv', return_value="development"):
            # 发送验证码
            manager.send_verify_code("test@example.com")

            # 验证正确验证码
            success1, message1 = manager.verify_code("test@example.com", "123456")
            assert success1 is True
            assert "验证成功" in message1

            # 验证错误验证码
            manager.send_verify_code("test@example.com")
            success2, message2 = manager.verify_code("test@example.com", "000000")
            assert success2 is False
            assert "错误" in message2

            # 验证不存在的邮箱
            success3, message3 = manager.verify_code("nonexistent@example.com", "123456")
            assert success3 is False
            assert "不存在" in message3 or "过期" in message3

    def test_concurrent_sending_lock(self, manager):
        """测试并发发送锁"""
        with patch('os.getenv', return_value="production"):
            # 开始发送
            with manager.locks_lock:
                manager.sending_locks["test@example.com"] = True

            # 尝试再次发送（应该被锁住）
            success, message = manager.send_verify_code("test@example.com")
            assert success is False
            assert "正在发送" in message


class TestMultiEmailIntegration:
    """测试多邮箱集成功能"""

    def test_different_domain_routing(self):
        """测试不同域名邮箱路由"""
        domains_and_servers = [
            ("qq.com", "smtp.qq.com"),
            ("163.com", "smtp.163.com"),
            ("gmail.com", "smtp.gmail.com"),
            ("tongji.edu.cn", "smtp.tongji.edu.cn"),
            ("unknown.com", "smtp.qq.com")  # 默认配置
        ]

        for domain, expected_server in domains_and_servers:
            config = get_email_config_by_domain(domain)
            assert config["smtp_server"] == expected_server

    @pytest.fixture
    def manager(self):
        """创建验证码管理器实例"""
        return EmailVerifyCodeManager(expire_minutes=1)

    @patch('smtplib.SMTP_SSL')
    @patch('smtplib.SMTP')
    def test_different_port_handling(self, mock_smtp, mock_smtp_ssl, manager):
        """测试不同端口的处理方式"""
        # 测试465端口（SSL）
        config_ssl = {
            "smtp_server": "smtp.qq.com",
            "smtp_port": 465,
            "sender_email": "test@qq.com",
            "sender_password": "password",
            "display_name": "测试"
        }

        manager._send_email("test@qq.com", "主题", "内容", config_ssl)
        mock_smtp_ssl.assert_called_once()

        # 重置mock
        mock_smtp_ssl.reset_mock()
        mock_smtp.reset_mock()

        # 测试587端口（TLS）
        config_tls = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "test@gmail.com",
            "sender_password": "password",
            "display_name": "测试"
        }

        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        manager._send_email("test@gmail.com", "主题", "内容", config_tls)
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()

    @patch('smtplib.SMTP_SSL')
    def test_incomplete_config_fallback(self, mock_smtp):
        """测试配置不完整时回退到默认配置"""
        # 模拟不完整的配置
        incomplete_config = {
            "smtp_server": "smtp.test.com",
            "smtp_port": 465,
            "sender_email": "",  # 空邮箱
            "sender_password": "",  # 空密码
            "display_name": "测试"
        }

        with patch('app.services.verifycode.get_email_config_by_email', return_value=incomplete_config):
            manager = EmailVerifyCodeManager()

            # 应该回退到默认配置
            manager._send_email("test@example.com", "主题", "内容")

            # 验证使用的是默认配置的QQ邮箱
            assert mock_smtp.called
            call_args = mock_smtp.call_args
            assert call_args[0][0] == DEFAULT_EMAIL_CONFIG["smtp_server"]


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])