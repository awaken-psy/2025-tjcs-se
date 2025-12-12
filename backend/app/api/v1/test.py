"""
Test API endpoints for admin functionality

该文件定义了管理员专用的测试接口，用于系统调试和验证。
所有接口都需要管理员权限。

API层职责：
1. 权限验证（通过admin_required依赖）
2. 请求参数验证
3. 调用service层处理业务逻辑
4. 统一响应格式处理
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from logger import api_logging, get_logger

# 导入认证依赖和响应模型
from app.auth.dependencies import admin_required, AdminUser
from app.database.database import get_db
from app.model import BaseResponse

from app.services.admin_test import admin_test_service


router = APIRouter(prefix="/test", tags=["Test"])
logger = get_logger(f"router<{__name__}>")


# ------------------------------------------------------------------
# 管理员测试接口：获取指定用户邮箱的注册验证码
# ------------------------------------------------------------------
@router.get("/verification-code/{email}", response_model=BaseResponse[dict])
@api_logging(logger)
async def get_user_verification_code(
    email: str,
    admin_user: AdminUser = Depends(admin_required)
):
    """
    获取指定用户邮箱的当前注册验证码

    Args:
        email: 用户邮箱地址
        admin_user: 管理员用户信息（通过认证依赖注入）
        db: 数据库会话

    Returns:
        包含验证码信息的响应
    """
    logger.info(f"管理员 {admin_user.username} 请求获取邮箱 {email} 的验证码")

    try:
        # 调用service层处理业务逻辑
        success, message, data = admin_test_service.get_user_verification_code(email)

        if success:
            return BaseResponse.success(data=data, message=message)
        else:
            # 业务失败
            return BaseResponse.fail(message=message)

    except HTTPException:
        # 重新抛出HTTP异常（如认证失败）
        raise
    except Exception as e:
        logger.error(f"获取用户验证码失败: {str(e)}")
        return BaseResponse.fail(message=f"获取验证码失败: {str(e)}")


# ------------------------------------------------------------------
# 管理员测试接口：检查系统状态
# ------------------------------------------------------------------
@router.get("/system-status", response_model=BaseResponse[dict])
@api_logging(logger)
async def get_system_status(admin_user: AdminUser = Depends(admin_required)):
    """
    获取系统状态信息（管理员专用）

    Args:
        admin_user: 管理员用户信息

    Returns:
        系统状态信息
    """
    logger.info(f"管理员 {admin_user.username} 请求获取系统状态")

    try:
        # 调用service层处理业务逻辑
        success, message, data = admin_test_service.get_system_status()

        if success:
            return BaseResponse.success(data=data, message=message)
        else:
            return BaseResponse.fail(message=message)

    except HTTPException:
        # 重新抛出HTTP异常（如认证失败）
        raise
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        return BaseResponse.fail(message=f"获取系统状态失败: {str(e)}")