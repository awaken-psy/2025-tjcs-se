"""
JWT Token 处理模块 - 生成、验证、刷新 JWT Token
"""
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple, List, Union
from enum import Enum
from domain.user import UserRole, Permission
from pydantic import BaseModel, Field, ValidationError
from domain.user import UserRole, Permission, GuestUser, RegisteredUser, AdminUser, BaseUser


class JWTConfig:
    """JWT 配置类"""
    # 密钥 - 生产环境应从环境变量读取
    SECRET_KEY = "your-secret-key-change-in-production"  # TODO: 从环境变量读取
    
    # Token 过期时间（小时）
    ACCESS_TOKEN_EXPIRE_HOURS = 24
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Token 类型
    class TokenType(str, Enum):
        TOKEN_TYPE_ACCESS = "access"
        TOKEN_TYPE_REFRESH = "refresh"
    
    # 算法
    ALGORITHM = "HS256"

class AccessTokenPayload(BaseModel):
    """访问令牌"""
    sub: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: UserRole = Field(..., description="用户角色")
    permissions: List[Permission] = Field([], description="用户权限列表")
    token_type: JWTConfig.TokenType = Field(..., description="Token类型")
    iat: datetime = Field(..., description="发行时间")
    exp: datetime = Field(..., description="过期时间")

    # @staticmethod
    # def from_user(user: AuthenticatedUser|AdminUser):
    #     """从 AuthenticatedUser 创建 AccessTokenPayload"""
    #     return AccessTokenPayload(
    #         sub=user.user_id,
    #         username=user.username, 
    #         role=user.role,
    #         permissions=[p for p in user.permissions],
    #         token_type=JWTConfig.TokenType.TOKEN_TYPE_ACCESS,
    #         iat=datetime.now(timezone.utc),  # 发行时间
    #         exp=datetime.now(timezone.utc) + timedelta(hours=JWTConfig.ACCESS_TOKEN_EXPIRE_HOURS),  # 过期时间
    #     )


class RefreshTokenPayload(BaseModel):
    """刷新令牌"""
    sub: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    token_type: JWTConfig.TokenType = Field(..., description="Token类型")
    iat: datetime = Field(..., description="发行时间")
    exp: datetime = Field(..., description="过期时间")

    # @staticmethod
    # def from_user(user: AuthenticatedUser|AdminUser):
    #     """从 AuthenticatedUser 创建 RefreshTokenPayload"""
    #     return RefreshTokenPayload(
    #         sub=user.user_id,
    #         username=user.username,
    #         token_type=JWTConfig.TokenType.TOKEN_TYPE_REFRESH,
    #         iat=datetime.now(timezone.utc),  # 发行时间
    #         exp=datetime.now(timezone.utc) + timedelta(days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS),  # 过期时间
    #     )


class JWTHandler:
    """JWT Token 处理器"""

    @staticmethod
    def generate_token(payload: BaseModel) -> str:
        """
        生成 JWT Token
        
        Args:
            payload: 载荷对象
        
        Returns:
            JWT Token 字符串
        """
        token = jwt.encode(
            payload.model_dump(),
            JWTConfig.SECRET_KEY,
            algorithm=JWTConfig.ALGORITHM
        )
        return token
    
    @staticmethod
    def generate_access_token(
        user_id: str,
        username: str,
        role: UserRole,
        permissions: Optional[list[Permission]] = None,
        expires_hours: Optional[int] = None,
    ) -> str:
        """
        生成访问令牌 (Access Token)
        
        Args:
            user_id: 用户ID
            username: 用户名
            role: 用户角色
            permissions: 权限列表
            expires_hours: 过期时间（小时）

        
        Returns:
            JWT Token 字符串
        """
        if expires_hours is None:
            expires_hours = JWTConfig.ACCESS_TOKEN_EXPIRE_HOURS


        payload = AccessTokenPayload(
            sub=user_id,  # Subject - 用户ID
            username=username,
            role=role,
            permissions=permissions or [],
            token_type=JWTConfig.TokenType.TOKEN_TYPE_ACCESS,
            iat=datetime.now(timezone.utc),  # 发行时间
            exp=datetime.now(timezone.utc) + timedelta(hours=expires_hours),  # 过期时间
        )
        
        return JWTHandler.generate_token(payload)
    
    @staticmethod
    def generate_access_token_from_user(user: BaseUser) -> str:
        """
        生成访问令牌 (Access Token)
        
        Args:
            user: 用户对象
        
        Returns:
            JWT Token 字符串
        """
        if user.role == UserRole.GUEST:
            raise ValueError("访客用户无访问令牌")

        return JWTHandler.generate_access_token(
            user_id=user.user_id,
            username=user.username,
            role=user.role,
            permissions=[p for p in user.permissions],
            expires_hours=JWTConfig.ACCESS_TOKEN_EXPIRE_HOURS
        )
    
    @staticmethod
    def generate_refresh_token(
        user_id: str,
        username: str,
        expires_days: Optional[int] = None,
    ) -> str:
        """
        生成刷新令牌 (Refresh Token)
        
        Args:
            user_id: 用户ID
            username: 用户名
            expires_days: 过期时间（天）
        
        Returns:
            JWT Token 字符串
        """
        if expires_days is None:
            expires_days = JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS
        

        payload = RefreshTokenPayload(
            sub=user_id,
            username=username,
            token_type=JWTConfig.TokenType.TOKEN_TYPE_REFRESH,
            iat=datetime.now(timezone.utc),  # 发行时间
            exp=datetime.now(timezone.utc) + timedelta(days=expires_days),  # 过期时间
        )
        
        return JWTHandler.generate_token(payload)
    
    @staticmethod
    def generate_refresh_token_from_user(user: BaseUser) -> str:
        """
        生成刷新令牌 (Refresh Token)
        
        Args:
            user: 用户对象
        
        Returns:
            JWT Token 字符串
        """
        if user.role == UserRole.GUEST:
            raise ValueError("访客用户无刷新令牌")
        return JWTHandler.generate_refresh_token(
            user_id=user.user_id,
            username=user.username,
            expires_days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS,
        )
    
    @staticmethod
    def verify_token(token: str) -> Tuple[bool, Optional[Dict[str, str]], Optional[str]]:
        """
        验证 Token 的有效性
        
        Args:
            token: JWT Token 字符串
        
        Returns:
            (是否有效, 解码后的 payload, 错误信息) 元组
        """
        try:
            payload = jwt.decode(
                token,
                JWTConfig.SECRET_KEY,
                algorithms=[JWTConfig.ALGORITHM]
            )
            return True, payload, None
        except jwt.ExpiredSignatureError:
            return False, None, "Token已过期"
        except jwt.InvalidTokenError:
            return False, None, "无效的Token"
        # except ValidationError:
        #     return False, None, "Token字段解析失败"
        except Exception as e:
            return False, None, f"未知错误: {str(e)}"
        
    @staticmethod
    def verify_access_token(token: str) -> Tuple[bool, Union[AccessTokenPayload, None], Optional[str]]:
        """
        验证访问令牌的有效性
        
        Args:
            token: JWT Token 字符串
        
        Returns:
            (是否有效, 解码后的 payload, 错误信息) 元组
        """
        valid, payload_dict, error = JWTHandler.verify_token(token)
        if not valid or payload_dict is None:
            return False, None, error
        
        # 检查token_type是否为access
        if payload_dict.get("token_type") != JWTConfig.TokenType.TOKEN_TYPE_ACCESS:
            return False, None, "令牌类型错误，需要访问令牌"
        
        # 从字典中解析 payload
        try:
            payload = AccessTokenPayload.model_validate(payload_dict)
        except ValidationError:
            return False, None, "Access Token字段解析失败"
        
        return True, payload, None
    
    @staticmethod
    def verify_refresh_token(token: str) -> Tuple[bool, Union[RefreshTokenPayload, None], Optional[str]]:
        """
        验证刷新令牌的有效性
        
        Args:
            token: JWT Token 字符串
        
        Returns:
            (是否有效, 解码后的 payload, 错误信息) 元组
        """
        valid, payload_dict, error = JWTHandler.verify_token(token)
        if not valid or payload_dict is None:
            return False, None, error
        
        # 检查token_type是否为refresh
        if payload_dict.get("token_type") != JWTConfig.TokenType.TOKEN_TYPE_REFRESH:
            return False, None, "令牌类型错误，需要刷新令牌"
        
        # 从字典中解析 payload
        try:
            payload = RefreshTokenPayload.model_validate(payload_dict)
        except ValidationError:
            return False, None, "Refresh Token字段解析失败"
        
        return True, payload, None
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        使用刷新令牌生成新的访问令牌和刷新令牌
        
        Args:
            refresh_token: 刷新令牌
        
        Returns:
            (是否成功, 新的access_token, 新的refresh_token, 错误信息) 元组
        """
        valid, payload, error = JWTHandler.verify_refresh_token(refresh_token)
        if not valid or payload is None:
            return False, None, None, error
        
        # 生成新的 access token
        new_access_token = JWTHandler.generate_access_token(
            user_id=payload.sub,
            username=payload.username,
            role=UserRole.USER,  # TODO: 默认为 USER，实际应从数据库获取
            permissions=[]
        )

        new_refresh_token = JWTHandler.generate_token(payload)
        
        return True, new_access_token, new_refresh_token, None
    
    # @staticmethod
    # def decode_token(token: str) -> Union[AccessTokenPayload, RefreshTokenPayload, None]:
    #     """
    #     解码 Token（不验证过期时间）
        
    #     Args:
    #         token: JWT Token 字符串
        
    #     Returns:
    #         解码后的 payload，或 None 如果解码失败
    #     """
    #     try:
    #         payload = jwt.decode(
    #             token,
    #             JWTConfig.SECRET_KEY,
    #             algorithms=[JWTConfig.ALGORITHM],
    #             options={"verify_exp": False}  # 不验证过期时间
    #         )
    #         return AccessTokenPayload.model_validate(payload)
    #     except jwt.InvalidTokenError:
    #         return None
    #     except ValidationError:
    #         return None


