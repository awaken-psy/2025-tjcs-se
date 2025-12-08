import smtplib
import random
import time
import threading
from email.mime.text import MIMEText
from email.header import Header
from typing import Optional, Dict
import logging
from email.utils import formataddr
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# 导入邮箱配置
from app.services.config import get_email_config_by_email, DEFAULT_EMAIL_CONFIG

class VerifyCode:
    def __init__(self, email: str, code: str, expire_time: float):
        self.email = email
        self.code = code
        self.expire_time = expire_time


class EmailVerifyCodeManager:
    def __init__(self, expire_minutes: int = 10):
        self.expire_minutes = expire_minutes

        self.verify_codes = {}
        # 线程池用于异步发送邮件
        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="email_sender")
        # 发送锁，防止同一邮箱重复发送
        self.sending_locks = {}
        # 全局锁用于保护sending_locks字典
        self.locks_lock = threading.Lock()

    def _generate_code(self, length: int = 6) -> str:
        """生成指定长度的数字验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])

    def _send_email(self, recipient: str, subject: str, content: str, sender_config: Optional[Dict] = None) -> bool:
        """发送邮件"""
        try:
            # 如果没有指定发送配置，根据收件人域名选择最佳配置
            if sender_config is None:
                sender_config = get_email_config_by_email(recipient)

            # 检查发送配置是否完整
            if not sender_config.get("sender_email") or not sender_config.get("sender_password"):
                logger.warning(f"邮箱配置不完整，使用默认配置: {recipient}")
                sender_config = DEFAULT_EMAIL_CONFIG

            # 创建邮件内容
            message = MIMEText(content, 'plain', 'utf-8')
            message['Subject'] = Header(subject, 'utf-8') #type: ignore
            message['From'] = formataddr((str(Header(sender_config['display_name'], 'utf-8')), sender_config['sender_email']))
            message['To'] = recipient

            # 根据端口选择不同的SMTP连接方式
            smtp_port = sender_config['smtp_port']
            smtp_server = sender_config['smtp_server']

            if smtp_port == 465:
                # SSL连接
                with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
                    server.login(sender_config['sender_email'], sender_config['sender_password'])
                    server.sendmail(sender_config['sender_email'], [recipient], message.as_string())
            elif smtp_port == 587:
                # TLS连接
                with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                    server.starttls()
                    server.login(sender_config['sender_email'], sender_config['sender_password'])
                    server.sendmail(sender_config['sender_email'], [recipient], message.as_string())
            else:
                # 普通连接
                with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                    server.login(sender_config['sender_email'], sender_config['sender_password'])
                    server.sendmail(sender_config['sender_email'], [recipient], message.as_string())

            logger.info(f"验证码邮件发送成功: {recipient} (发件人: {sender_config['sender_email']})")
            return True
        except Exception as e:
            logger.error(f"发送验证码邮件失败: {recipient}, 错误: {e}")
            return False

    def _send_email_async(self, recipient: str, subject: str, content: str, email: str):
        """异步发送邮件"""
        def _send_and_cleanup():
            try:
                success = self._send_email(recipient, subject, content)
                if not success:
                    # 发送失败，清理验证码
                    with self.locks_lock:
                        if email in self.sending_locks:
                            del self.sending_locks[email]
                    if email in self.verify_codes:
                        del self.verify_codes[email]
                    logger.warning(f"邮件发送失败，已清理验证码: {email}")
                else:
                    # 发送成功，释放锁
                    with self.locks_lock:
                        if email in self.sending_locks:
                            del self.sending_locks[email]
                    logger.info(f"邮件异步发送完成: {email}")
            except Exception as e:
                logger.error(f"异步发送邮件异常: {e}")
                # 清理验证码和锁
                with self.locks_lock:
                    if email in self.sending_locks:
                        del self.sending_locks[email]
                if email in self.verify_codes:
                    del self.verify_codes[email]

        # 提交到线程池异步执行
        self.executor.submit(_send_and_cleanup)

    def send_verify_code(self, email: str) -> tuple[bool, str]:
        """
        发送验证码到指定邮箱

        Args:
            email: 目标邮箱地址

        Returns:
            (success, message): 发送是否成功和相关信息
        """
        # 检查是否正在发送中（防止重复发送）
        with self.locks_lock:
            if email in self.sending_locks:
                return False, "验证码正在发送中，请稍后再试"

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
            return True, f"开发模式：验证码是 {code}（有效期 {self.expire_minutes} 分钟）"
        else:
            # 生产模式：异步发送邮件，不阻塞API响应
            with self.locks_lock:
                self.sending_locks[email] = True  # 标记为正在发送

            subject = "时光胶囊·校园 - 验证码"
            content = f"""
亲爱的用户：

您正在注册时光胶囊·校园，验证码为：{code}

验证码有效期为 {self.expire_minutes} 分钟，请尽快使用。

如非本人操作，请忽略此邮件。

时光胶囊·校园团队
            """.strip()

            # 异步发送邮件
            self._send_email_async(email, subject, content, email)

            # 立即返回成功，不等待邮件发送完成
            return True, "验证码发送成功，请查收邮件（可能需要几分钟）"

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

    def shutdown(self):
        """关闭线程池，清理资源"""
        try:
            self.executor.shutdown(wait=True)
            logger.info("验证码管理器线程池已关闭")
        except Exception as e:
            logger.error(f"关闭验证码管理器线程池失败: {e}")


# 创建全局验证码管理器实例
from app.services.config import VERIFY_CODE_CONFIG

verify_code_manager = EmailVerifyCodeManager(
    expire_minutes=VERIFY_CODE_CONFIG["expire_minutes"]
)

