"""
Authentication API interface
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db

   

from app.model import (
        BaseResponse,
        UserRegisterRequest,
        UserLoginRequest,
        UserAuthResponse,
        UserRefreshTokenResponse,
        SendCodeRequest,
    )

from app.services.verifycode import verify_code_manager
from app.services.register import RegisterManager
from app.services.login import LoginManager


router = APIRouter(prefix='/auth', tags=['Authorization'])

@router.post("/sendcode", response_model=BaseResponse[None])
async def send_code(request: SendCodeRequest):
    """发送验证码"""
    try:
        success, message = verify_code_manager.send_verify_code(request.email)

        if success:
            return BaseResponse.success(message=message)
        else:
            return BaseResponse.fail(message=message)
    except Exception as e:
        return BaseResponse.fail(message=f"发送验证码失败: {str(e)}")



@router.post("/register", response_model=BaseResponse[UserAuthResponse])
async def register(
    request: UserRegisterRequest,
):
    """用户注册"""
    try:
        # 创建注册管理器
        register_manager = RegisterManager()

        # 执行用户注册
        success, message, user_data = register_manager.register_user(
            email=request.email,
            password=request.password,
            nickname=request.nickname,
            campus_id=request.student_id,
            verify_code=request.verify_code
        )

        if success and user_data:
            # 创建响应数据
            auth_response = UserAuthResponse(
                user_id=user_data["user_id"],
                email=user_data["email"],
                nickname=user_data["nickname"],
                token=user_data["token"],
                refresh_token=user_data["refresh_token"],
                avatar=user_data["avatar"]
            )
            return BaseResponse.success(data=auth_response, message=message)
        else:
            return BaseResponse.fail(message=message)

    except Exception as e:
        return BaseResponse.fail(message=f"注册失败: {str(e)}")


@router.get("/check-email/{email}", response_model=BaseResponse[dict])
async def check_email_availability(
    email: str,
):
    """检查邮箱是否可用"""
    try:
        register_manager = RegisterManager()
        is_available, message = register_manager.check_email_availability(email)

        return BaseResponse.success(
            data={"available": is_available},
            message=message
        )
    except Exception as e:
        return BaseResponse.fail(message=f"检查邮箱可用性失败: {str(e)}")


@router.get("/check-student-id/{student_id}", response_model=BaseResponse[dict])
async def check_student_id_availability(
    student_id: str,
):
    """检查学号是否可用"""
    try:
        register_manager = RegisterManager()
        is_available, message = register_manager.check_student_id_availability(student_id)

        return BaseResponse.success(
            data={"available": is_available},
            message=message
        )
    except Exception as e:
        return BaseResponse.fail(message=f"检查学号可用性失败: {str(e)}")


@router.post("/login", response_model=BaseResponse[UserAuthResponse])
async def login(
    request: UserLoginRequest,
):
    """用户登录"""
    try:

        # 执行用户登录
        success, message, user_data = LoginManager().login_user(
            email_or_username=request.email,
            password=request.password
        )

        if success and user_data:
            # 创建响应数据
            auth_response = UserAuthResponse(
                user_id=user_data["user_id"],
                email=user_data["email"],
                nickname=user_data["nickname"],
                token=user_data["token"],
                refresh_token=user_data["refresh_token"],
                avatar=user_data["avatar"]
            )
            return BaseResponse.success(data=auth_response, message=message)
        else:
            return BaseResponse.fail(message=message)

    except Exception as e:
        return BaseResponse.fail(message=f"登录失败: {str(e)}")


@router.post("/logout", response_model=BaseResponse[None])
async def logout():
    """用户登出"""
    # TODO: 实现用户登出逻辑
    # 1. 将token加入黑名单
    pass


@router.post("/refresh", response_model=BaseResponse[UserRefreshTokenResponse])
async def refresh_token():
    """刷新令牌"""
    # TODO: 实现token刷新逻辑
    pass