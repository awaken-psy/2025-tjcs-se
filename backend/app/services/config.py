
"""
Application configuration
"""
import os

# SMTP Configuration
SMTP_CONFIG = {
    "server": os.getenv("SMTP_SERVER", "smtp.qq.com"),
    "port": int(os.getenv("SMTP_PORT", "465")),
    "sender_email": os.getenv("SMTP_SENDER_EMAIL", ""),
    "sender_password": os.getenv("SMTP_SENDER_PASSWORD", ""),
}

# Verification Code Configuration
VERIFY_CODE_CONFIG = {
    "expire_minutes": int(os.getenv("VERIFY_CODE_EXPIRE_MINUTES", "10")),
}

# Application Configuration
APP_CONFIG = {
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
}