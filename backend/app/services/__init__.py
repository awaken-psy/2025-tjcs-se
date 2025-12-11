"""
服务模块
"""
from .register import RegisterManager

if not RegisterManager.admin_user_added:
    RegisterManager.init_admin_user = RegisterManager.add_init_admin_user()
    RegisterManager.admin_user_added = True



