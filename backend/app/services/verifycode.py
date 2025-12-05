import smtplib
import random
import time
from email.mime.text import MIMEText
from email.header import Header
from typing import Optional
import logging
from email.utils import formataddr
from app.logger import get_logger

logger = get_logger("verifycode_manager")

"""
!!!目前是单线程版本!!!
"""

class VerifyCode:
    def __init__(self, email: str, code: str, expire_time: float):
        self.email = email
        self.code = code
        self.expire_time = expire_time


class EmailVerifyCodeManager:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str, expire_minutes: int = 10):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender = sender_email
        self.sender_password = sender_password
        self.expire_minutes = expire_minutes

        self.verify_codes = {}

    def _generate_code(self, length: int = 6) -> str:
        """生成指定长度的数字验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])

    def _send_email(self, recipient: str, subject: str, content: str) -> bool:
        """发送邮件"""
        try:
            # 创建邮件内容
            message = MIMEText(content, 'plain', 'utf-8')
            message['Subject'] = Header(subject, 'utf-8') #type: ignore
            message['From'] = formataddr((str(Header('时光胶囊·校园','utf-8')), self.sender))
            message['To'] = recipient

            # 连接SMTP服务器并发送邮件
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender, self.sender_password)
                server.sendmail(self.sender, [recipient], message.as_string())

            logger.info(f"验证码邮件发送成功: {recipient}")
            return True
        except Exception as e:
            logger.error(f"发送验证码邮件失败: {e}")
            return False

    def send_verify_code(self, email: str) -> tuple[bool, str]:
        """
        发送验证码到指定邮箱

        Args:
            email: 目标邮箱地址

        Returns:
            (success, message): 发送是否成功和相关信息
        """
        # 检查是否在冷却期内（60秒内只能发送一次）
        if email in self.verify_codes:
            existing_code = self.verify_codes[email]
            current_time = time.time()
            if current_time < existing_code.expire_time - (self.expire_minutes - 1) * 60:
                return False, "验证码发送过于频繁，请稍后再试"

        # 开发模式：使用固定验证码123456，避免SMTP配置问题
        import os
        is_dev_mode = os.getenv("APP_ENV", "production") == "development"

        if is_dev_mode:
            # 开发模式：固定验证码
            code = "123456"
            logger.info(f"开发模式：为邮箱 {email} 生成固定验证码: {code}")
        else:
            # 生产模式：随机验证码
            code = self._generate_code()

        expire_time = time.time() + self.expire_minutes * 60

        # 创建验证码对象
        verify_code = VerifyCode(email, code, expire_time)

        # 保存验证码
        self.verify_codes[email] = verify_code

        if is_dev_mode:
            # 开发模式：跳过邮件发送
            logger.info(f"开发模式：跳过邮件发送，验证码已保存: {email} -> {code}")
            return True, f"开发模式：验证码是 123456（有效期 {self.expire_minutes} 分钟）"
        else:
            # 生产模式：发送邮件
            subject = "时光胶囊·校园 - 验证码"
            content = f"""
亲爱的用户：

您正在注册时光胶囊·校园，验证码为：{code}

验证码有效期为 {self.expire_minutes} 分钟，请尽快使用。

如非本人操作，请忽略此邮件。

时光胶囊·校园团队
            """.strip()

            success = self._send_email(email, subject, content)

            if success:
                return True, "验证码发送成功"
            else:
                # 如果发送失败，移除验证码记录
                if email in self.verify_codes:
                    del self.verify_codes[email]
                return False, "验证码发送失败，请检查邮箱地址或稍后重试"

    def verify_code(self, email: str, code: str) -> tuple[bool, str]:
        """
        验证验证码

        Args:
            email: 邮箱地址
            code: 验证码

        Returns:
            (success, message): 验证是否成功和相关信息
        """
        # 清理过期验证码
        self._clean_expired_codes()

        # 检查验证码是否存在
        if email not in self.verify_codes:
            return False, "验证码不存在或已过期"

        verify_code = self.verify_codes[email]

        # 检查验证码是否过期
        current_time = time.time()
        if current_time > verify_code.expire_time:
            del self.verify_codes[email]
            return False, "验证码不存在或已过期"

        # 验证验证码
        if verify_code.code != code:
            return False, "验证码错误"

        # 验证成功后删除验证码记录
        del self.verify_codes[email]
        return True, "验证成功"

    def _clean_expired_codes(self):
        """清理过期的验证码"""
        current_time = time.time()
        expired_emails = [
            email for email, code in self.verify_codes.items()
            if current_time > code.expire_time
        ]

        for email in expired_emails:
            del self.verify_codes[email]

        if expired_emails:
            logger.info(f"清理了 {len(expired_emails)} 个过期验证码")


# 创建全局验证码管理器实例
from app.services.config import SMTP_CONFIG, VERIFY_CODE_CONFIG

verify_code_manager = EmailVerifyCodeManager(
    smtp_server=SMTP_CONFIG["server"],
    smtp_port=SMTP_CONFIG["port"],
    sender_email=SMTP_CONFIG["sender_email"],
    sender_password=SMTP_CONFIG["sender_password"],
    expire_minutes=VERIFY_CODE_CONFIG["expire_minutes"]
)

