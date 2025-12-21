"""
时间处理辅助函数
"""
from datetime import datetime, timedelta

def beijing_now():
    """获取当前北京时间（UTC+8）"""
    return datetime.utcnow() + timedelta(hours=8)