
"""
Application configuration
"""
import os

# 多邮箱提供商配置
EMAIL_PROVIDERS = {
    # QQ邮箱配置
    "qq.com": {
        "smtp_server": "smtp.qq.com",
        "smtp_port": 465,
        "sender_email": os.getenv("QQ_SENDER_EMAIL", "1461963552@qq.com"),
        "sender_password": os.getenv("QQ_SENDER_PASSWORD", "mmfpltiuvljzghfh"),
        "display_name": "时光胶囊·校园"
    },
    # 163邮箱配置
    "163.com": {
        "smtp_server": "smtp.163.com",
        "smtp_port": 465,
        "sender_email": os.getenv("EMAIL163_SENDER_EMAIL", ""),
        "sender_password": os.getenv("EMAIL163_SENDER_PASSWORD", ""),
        "display_name": "时光胶囊·校园"
    },
    # Gmail配置
    "gmail.com": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": os.getenv("GMAIL_SENDER_EMAIL", ""),
        "sender_password": os.getenv("GMAIL_SENDER_PASSWORD", ""),
        "display_name": "时光胶囊·校园"
    },
    # 同济大学邮箱配置
    "tongji.edu.cn": {
        "smtp_server": "smtp.tongji.edu.cn",
        "smtp_port": 465,
        "sender_email": os.getenv("TONGJI_SENDER_EMAIL", ""),
        "sender_password": os.getenv("TONGJI_SENDER_PASSWORD", ""),
        "display_name": "时光胶囊·校园"
    }
}

# 默认邮箱配置（当无法匹配域名时使用）
DEFAULT_EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.qq.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "465")),
    "sender_email": os.getenv("SMTP_SENDER_EMAIL", "1461963552@qq.com"),
    "sender_password": os.getenv("SMTP_SENDER_PASSWORD", "mmfpltiuvljzghfh"),
    "display_name": "时光胶囊·校园"
}

# 兼容旧版本的SMTP配置
SMTP_CONFIG = DEFAULT_EMAIL_CONFIG

# Verification Code Configuration
VERIFY_CODE_CONFIG = {
    "expire_minutes": int(os.getenv("VERIFY_CODE_EXPIRE_MINUTES", "10")),
}

# Application Configuration
APP_CONFIG = {
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
}

def get_email_config_by_domain(email_domain: str) -> dict:
    """
    根据邮箱域名获取对应的SMTP配置

    Args:
        email_domain: 邮箱域名（如 qq.com, 163.com）

    Returns:
        dict: SMTP配置字典
    """
    return EMAIL_PROVIDERS.get(email_domain, DEFAULT_EMAIL_CONFIG)

def get_email_config_by_email(email: str) -> dict:
    """
    根据邮箱地址获取对应的SMTP配置

    Args:
        email: 邮箱地址

    Returns:
        dict: SMTP配置字典
    """
    try:
        domain = email.split('@')[1].lower()
        return get_email_config_by_domain(domain)
    except (IndexError, AttributeError):
        return DEFAULT_EMAIL_CONFIG