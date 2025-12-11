"""
Authentication API interface (authentication.py)

该文件定义了所有与用户认证和授权相关的 API 接口。
它属于 API 路由层，职责是接收 HTTP 请求，验证数据格式，并将核心业务逻辑
委派给 app.services 层的相应管理器进行处理。
"""
# ------------------------------------------------------------------
# 1. 外部和内部依赖导入
# ------------------------------------------------------------------
from fastapi import APIRouter, HTTPException, Depends # 导入 FastAPI 核心模块
from sqlalchemy.orm import Session # 导入 SQLAlchemy Session，用于数据库操作
from app.database.database import get_db # 导入获取数据库 Session 的依赖函数
from logger import api_logging, get_logger # 导入自定义的日志记录和 API 日志装饰器

# ------------------------------------------------------------------
# 2. 数据模型 (Pydantic DTOs) 导入
# ------------------------------------------------------------------
# 导入所有用于请求体、响应体和统一结构的数据模型
from app.model import (
        BaseResponse,             # 标准化的 API 响应模型 (包含 success, message, data)
        UserRegisterRequest,      # 用户注册请求体模型 (Pydantic)
        UserLoginRequest,         # 用户登录请求体模型
        UserAuthResponse,         # 成功注册/登录后的响应数据模型 (包含用户信息和 Token)
        UserRefreshTokenResponse, # 刷新 Token 后的响应数据模型
        SendCodeRequest,          # 发送验证码请求体模型
    )

# ------------------------------------------------------------------
# 3. 业务服务层管理器 (Service Managers) 导入
# ------------------------------------------------------------------
# 导入实现核心业务逻辑的服务管理器
from app.services.verifycode import verify_code_manager # 验证码管理服务
from app.services.register import RegisterManager       # 注册业务逻辑服务
from app.services.login import LoginManager             # 登录业务逻辑服务


# 实例化 FastAPI 路由
router = APIRouter(prefix='/auth', tags=['Authorization']) # 设置路由前缀为 /auth，并在文档中标记为 Authorization
logger = get_logger(f"router<{__name__}>") # 初始化路由特定的日志记录器

# ------------------------------------------------------------------
# 4. 接口: 发送验证码
# ------------------------------------------------------------------
@router.post("/sendcode", response_model=BaseResponse[None]) # 定义 POST /auth/sendcode 接口
@api_logging(logger) # 记录该 API 接口的调用情况
async def send_code(request: SendCodeRequest):
    """发送验证码"""
    try:
        # 调用 Service 层：执行生成验证码、存储到 Redis、发送邮件等核心操作
        success, message = verify_code_manager.send_verify_code(request.email)

        if success:
            return BaseResponse.success(message=message) # 成功响应
        else:
            return BaseResponse.fail(message=message)    # 业务失败响应 (如邮箱格式错误、发送频率限制等)
    except Exception as e:
        # 捕获并处理未预期的异常 (如邮件服务连接失败)
        return BaseResponse.fail(message=f"发送验证码失败: {str(e)}")


# ------------------------------------------------------------------
# 5. 接口: 用户注册
# ------------------------------------------------------------------
@router.post("/register", response_model=BaseResponse[UserAuthResponse]) # 定义 POST /auth/register 接口
@api_logging(logger)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db), # 通过依赖注入获取一个数据库 Session
):
    """用户注册"""
    try:
        # 实例化注册管理器，并将数据库 Session 传递给它
        register_manager = RegisterManager(db)

        # 执行用户注册的业务逻辑。Service 层将负责：
        # 1. 验证码校验
        # 2. 邮箱和学号查重
        # 3. 密码哈希处理
        # 4. 创建用户记录
        # 5. 生成 JWT (Access Token 和 Refresh Token)
        success, message, user_data = register_manager.register_user(
            email=request.email,
            password=request.password,
            nickname=request.nickname,
            campus_id=request.student_id,
            verify_code=request.verify_code
        )

        if success and user_data:
            # 注册成功：将 Service 层返回的数据 (user_data) 映射为响应模型
            auth_response = UserAuthResponse(
                user_id=user_data["user_id"],
                email=user_data["email"],
                nickname=user_data["nickname"],
                token=user_data["token"],               # Access Token
                refresh_token=user_data["refresh_token"],# Refresh Token
                avatar=user_data["avatar"]
            )
            return BaseResponse.success(data=auth_response, message=message)
        else:
            # 业务失败响应 (如验证码错误、邮箱已注册等)
            return BaseResponse.fail(message=message)

    except Exception as e:
        # 捕获并处理未预期的异常 (如数据库连接错误)
        return BaseResponse.fail(message=f"注册失败: {str(e)}")


# ------------------------------------------------------------------
# 6. 接口: 检查邮箱可用性
# ------------------------------------------------------------------
@router.get("/check-email/{email}", response_model=BaseResponse[dict]) # 定义 GET /auth/check-email/{email} 接口
async def check_email_availability(
    email: str,
    db: Session = Depends(get_db),
):
    """检查邮箱是否可用"""
    try:
        register_manager = RegisterManager(db)
        # 调用 Service 层进行数据库查询，检查邮箱是否已存在
        is_available, message = register_manager.check_email_availability(email)

        return BaseResponse.success(
            data={"available": is_available}, # 返回布尔值 indicating availability
            message=message
        )
    except Exception as e:
        return BaseResponse.fail(message=f"检查邮箱可用性失败: {str(e)}")


# ------------------------------------------------------------------
# 7. 接口: 检查学号可用性
# ------------------------------------------------------------------
@router.get("/check-student-id/{student_id}", response_model=BaseResponse[dict]) # 定义 GET /auth/check-student-id/{student_id} 接口
async def check_student_id_availability(
    student_id: str,
    db: Session = Depends(get_db),
):
    """检查学号是否可用"""
    try:
        register_manager = RegisterManager(db)
        # 调用 Service 层进行数据库查询，检查学号是否已存在
        is_available, message = register_manager.check_student_id_availability(student_id)

        return BaseResponse.success(
            data={"available": is_available}, # 返回布尔值 indicating availability
            message=message
        )
    except Exception as e:
        return BaseResponse.fail(message=f"检查学号可用性失败: {str(e)}")


# ------------------------------------------------------------------
# 8. 接口: 用户登录
# ------------------------------------------------------------------
@router.post("/login", response_model=BaseResponse[UserAuthResponse]) # 定义 POST /auth/login 接口
@api_logging(logger)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """用户登录"""
    try:
        # 实例化 LoginManager 并执行登录业务逻辑
        # Service 层负责：用户查找、密码校验（哈希对比）、生成新的 JWTs
        success, message, user_data = LoginManager(db).login_user(
            email_or_username=request.email,
            password=request.password
        )

        if success and user_data:
            logger.debug(f"登录成功, 返回的数据: {user_data}")
            
            # 登录成功：将 Service 层返回的数据映射为响应模型
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
            # 业务失败响应 (如密码错误、用户不存在等)
            return BaseResponse.fail(message=message)

    except Exception as e:
        # 捕获并处理未预期的异常
        return BaseResponse.fail(message=f"登录失败: {str(e)}")


# ------------------------------------------------------------------
# 9. 接口: 用户登出 (TODO)
# ------------------------------------------------------------------
@router.post("/logout", response_model=BaseResponse[None])
async def logout():
    """用户登出"""
    # TODO: 实现用户登出逻辑
    # 1. 核心逻辑通常涉及：
    #    a) 从请求头获取当前 Access Token。
    #    b) 将该 Access Token 加入到 **Token 黑名单** (通常存储在 Redis 中)，使其在过期前失效。
    pass


# ------------------------------------------------------------------
# 10. 接口: 刷新令牌 (TODO)
# ------------------------------------------------------------------
@router.post("/refresh", response_model=BaseResponse[UserRefreshTokenResponse])
async def refresh_token():
    """刷新令牌"""
    # TODO: 实现 token 刷新逻辑
    # 1. 从请求体或 Header 中获取 Refresh Token。
    # 2. 调用 Service 层验证 Refresh Token 的有效性。
    # 3. 成功后，生成 **新的 Access Token** 和 **新的 Refresh Token**。
    pass