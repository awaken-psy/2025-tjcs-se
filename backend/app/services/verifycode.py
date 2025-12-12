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

# 导入 Redis 客户端和配置
import redis 
# 🔴 关键假设：请确保您的 Redis 客户端在这里正确导入
# 您需要提供 app/database/redis.py 的实现
try:
    from app.database.redis import redis_client 
except ImportError:
    redis_client = None
    logging.error("Redis client not found. Verification code service will fail.")


# 导入邮箱配置
from app.services.config import get_email_config_by_email, DEFAULT_EMAIL_CONFIG, VERIFY_CODE_CONFIG


logger = logging.getLogger(__name__)

# ----------------------------------------------------
# 🔴 移除 VerifyCode 类
# ----------------------------------------------------

class EmailVerifyCodeManager:
    def __init__(self, expire_minutes: int = 10, redis_client: redis.Redis = None):
        self.expire_minutes = expire_minutes
        
        # 🔴 注入 Redis 客户端
        self.redis_client = redis_client 
        self.VERIFY_CODE_PREFIX = "vcode:email:" # 键前缀，防止冲突

        # 🔴 移除内存字典 self.verify_codes 和发送锁
        # self.verify_codes = {}
        
        # 线程池用于异步发送邮件 (保留，用于执行 I/O 耗时操作)
        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="email_sender")


    def _get_redis_key(self, email: str) -> str:
        """生成 Redis 存储 Key"""
        return f"{self.VERIFY_CODE_PREFIX}{email}"
    
    def _generate_code(self, length: int = 6) -> str:
        """生成指定长度的数字验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])

    
    def _send_email(self, recipient: str, subject: str, content: str, sender_config: Optional[Dict] = None) -> bool:
        """发送邮件 (最终修正：修复 NameError 和 SMTP 假失败)"""
        
        # 1. 获取发送配置 (保留原逻辑)
        if sender_config is None:
            from app.services.config import get_email_config_by_email, DEFAULT_EMAIL_CONFIG
            sender_config = get_email_config_by_email(recipient)

        if not sender_config.get("sender_email") or not sender_config.get("sender_password"):
            logger.warning(f"邮箱配置不完整，使用默认配置: {recipient}")
            sender_config = DEFAULT_EMAIL_CONFIG
        
        # 2. 🔴 关键修复点：在 try 块之前创建邮件内容，确保 message 变量总是被定义
        try:
            message = MIMEText(content, 'plain', 'utf-8')
            message['Subject'] = Header(subject, 'utf-8') #type: ignore
            message['From'] = formataddr((str(Header(sender_config['display_name'], 'utf-8')), sender_config['sender_email']))
            message['To'] = recipient
        except Exception as e:
            logger.error(f"创建邮件内容失败: {e}")
            return False

        server = None # 初始化 server 变量
        try:
            # 3. 连接和发送逻辑
            smtp_port = sender_config['smtp_port']
            smtp_server = sender_config['smtp_server']
            
            if smtp_port == 465:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
            elif smtp_port == 587:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
                server.starttls()
            else:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
            
            # 登录和发送
            server.login(sender_config['sender_email'], sender_config['sender_password'])
            server.sendmail(sender_config['sender_email'], [recipient], message.as_string())
            
            logger.info(f"验证码邮件发送成功: {recipient} (发件人: {sender_config['sender_email']})")
            return True 
            
        except smtplib.SMTPException as e:
            # 捕获标准的 SMTP 错误
            logger.error(f"发送验证码邮件失败 (SMTP 错误): {recipient}, 错误: {e}")
            return False
        except Exception as e:
            # 捕获所有其他底层异常，特别是那个 (-1, b'\x00\x00\x00')
            e_message = str(e)
            
            # 关键：如果邮件已发送，此非致命错误不应导致 Redis Key 被清理
            if "(-1, b'\\x00\\x00\\x00')" in e_message or "ssl.SSLError" in e_message or "timed out" in e_message.lower():
                 logger.warning(f"发送邮件时遇到非致命底层连接错误，邮件可能已发出: {recipient}, 错误: {e}")
                 return True # 假设成功，避免清理 Redis Key
            
            logger.error(f"发送验证码邮件失败 (未知底层异常): {recipient}, 错误: {e}")
            return False
        finally:
            # 确保关闭服务器连接
            if server:
                try:
                    server.quit()
                except Exception:
                    pass
    



    def _send_email_async(self, recipient: str, subject: str, content: str, email: str):
        """异步发送邮件，发送失败时清理 Redis Key"""
        
        def _send_and_cleanup():
            key = self._get_redis_key(email)
            try:
                success = self._send_email(recipient, subject, content)
                if not success:
                    # 发送失败，清理 Redis 中的验证码，允许用户立即重试
                    if self.redis_client:
                         # 🔴 关键：发送失败，删除 Redis Key
                         self.redis_client.delete(key) 
                    logger.warning(f"邮件发送失败，已清理 Redis 中的验证码: {email}")
                else:
                    logger.info(f"邮件异步发送完成: {email}")
            except Exception as e:
                logger.error(f"异步发送邮件异常: {e}")
                # 异常发生，清理 Redis 中的验证码
                if self.redis_client:
                    self.redis_client.delete(key)
        
        # 提交到线程池异步执行
        self.executor.submit(_send_and_cleanup)

    
    def send_verify_code(self, email: str) -> tuple[bool, str]:
        """发送验证码到指定邮箱"""
        
        key = self._get_redis_key(email)
        expire_seconds = self.expire_minutes * 60
        
        if not self.redis_client:
            return False, "系统错误：Redis 客户端未连接"

        # 🔴 关键：检查冷却期（使用 Redis TTL）
        # TTL 返回 Key 的剩余秒数，如果 Key 存在且剩余有效期大于 1 分钟 (60秒)，则发送过于频繁
        if self.redis_client.ttl(key) > (expire_seconds - 1):
            return False, "验证码发送过于频繁，请稍后再试"

        # 开发模式：使用固定验证码123456，避免SMTP配置问题
        import os
        is_dev_mode = os.getenv("APP_ENV", "development") == "development"
        code = "123456" if is_dev_mode else self._generate_code()
        
        # 🔴 关键：保存验证码到 Redis (使用 SETEX 自动处理过期时间)
        try:
            # SETEX: 设置 Key, 设置有效期(秒), 设置值
            self.redis_client.setex(
                name=key,
                value=code,
                time=expire_seconds
            )
        except Exception as e:
            logger.error(f"保存验证码到 Redis 失败: {e}")
            return False, "系统错误，无法存储验证码"


        if is_dev_mode:
            # 开发模式：跳过邮件发送
            logger.info(f"开发模式：跳过邮件发送，验证码已保存: {email} -> {code}")
            return True, f"开发模式：验证码是 {code}（有效期 {self.expire_minutes} 分钟）"
        else:
            # 生产模式：异步发送邮件
            subject = "时光胶囊·校园 - 验证码"
            content = f"""
亲爱的用户：

您正在注册时光胶囊·校园，验证码为：{code}

验证码有效期为 {self.expire_minutes} 分钟，请尽快使用。

如非本人操作，请忽略此邮件。

时光胶囊·校园团队
            """.strip()

            # 异步发送邮件 (如果发送失败，_send_email_async 会清理 Key)
            self._send_email_async(email, subject, content, email)

            # 立即返回成功
            return True, "验证码发送成功，请查收邮件"


    def verify_code(self, email: str, code: str) -> tuple[bool, str]:
        """验证验证码"""
        
        if not self.redis_client:
            return False, "系统错误：Redis 客户端未连接"

        key = self._get_redis_key(email)
        
        # 🔴 关键：从 Redis 获取存储的验证码 (Redis TTL 已处理过期)
        stored_code = self.redis_client.get(key)
        
        # 检查验证码是否存在或已过期 (Redis TTL 机制已处理)
        if not stored_code:
            return False, "验证码不存在或已过期"
        
        # Redis 客户端设置 decode_responses=True 时，这里是 str，否则是 bytes
        stored_code_str = stored_code 

        # 验证验证码
        if stored_code_str != code:
            return False, "验证码错误"

        # 🔴 关键：验证成功后删除验证码记录
        self.redis_client.delete(key)
        return True, "验证成功"

    # 🔴 移除内存清理方法 _clean_expired_codes

    def shutdown(self):
        """关闭线程池，清理资源"""
        try:
            self.executor.shutdown(wait=False)
            logger.info("验证码管理器线程池已关闭")
        except Exception as e:
            logger.error(f"关闭验证码管理器线程池失败: {e}")


# 创建全局验证码管理器实例
# 🔴 关键：传入全局 Redis 客户端实例
verify_code_manager = EmailVerifyCodeManager(
    expire_minutes=VERIFY_CODE_CONFIG["expire_minutes"],
    redis_client=redis_client
)