"""
JWT Token 处理模块 - 生成、验证、刷新 JWT Token
"""
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from app.models.core.user import UserRole, Permission


class JWTConfig:
    """JWT 配置类"""
    # 密钥 - 生产环境应从环境变量读取
    SECRET_KEY = "your-secret-key-change-in-production"  # TODO: 从环境变量读取
    
    # Token 过期时间（小时）
    ACCESS_TOKEN_EXPIRE_HOURS = 24
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Token 类型
    TOKEN_TYPE_ACCESS = "access"
    TOKEN_TYPE_REFRESH = "refresh"
    
    # 算法
    ALGORITHM = "HS256"


class JWTHandler:
    """JWT Token 处理器"""
    
    @staticmethod
    def generate_access_token(
        user_id: str,
        username: str,
        role: UserRole,
        permissions: list = None,
        expires_hours: Optional[int] = None
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
        
        payload = {
            "sub": user_id,  # Subject - 用户ID
            "username": username,
            "role": role.value,
            "permissions": permissions or [],
            "type": JWTConfig.TOKEN_TYPE_ACCESS,
            "iat": datetime.now(timezone.utc),  # 发行时间
            "exp": datetime.now(timezone.utc) + timedelta(hours=expires_hours),  # 过期时间
        }
        
        token = jwt.encode(
            payload,
            JWTConfig.SECRET_KEY,
            algorithm=JWTConfig.ALGORITHM
        )
        return token
    
    @staticmethod
    def generate_refresh_token(
        user_id: str,
        username: str,
        expires_days: Optional[int] = None
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
        
        payload = {
            "sub": user_id,
            "username": username,
            "type": JWTConfig.TOKEN_TYPE_REFRESH,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(days=expires_days),
        }
        
        token = jwt.encode(
            payload,
            JWTConfig.SECRET_KEY,
            algorithm=JWTConfig.ALGORITHM
        )
        return token
    
    @staticmethod
    def verify_token(token: str) -> Tuple[bool, Optional[Dict]]:
        """
        验证 Token 的有效性
        
        Args:
            token: JWT Token 字符串
        
        Returns:
            (是否有效, 解码后的 payload) 元组
        """
        try:
            payload = jwt.decode(
                token,
                JWTConfig.SECRET_KEY,
                algorithms=[JWTConfig.ALGORITHM]
            )
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, {"error": "Token已过期"}
        except jwt.InvalidTokenError as e:
            return False, {"error": f"无效的Token: {str(e)}"}
    
    @staticmethod
    def verify_access_token(token: str) -> Tuple[bool, Optional[Dict]]:
        """
        验证访问令牌
        
        Args:
            token: JWT Token 字符串
        
        Returns:
            (是否有效, 解码后的 payload) 元组
        """
        valid, payload = JWTHandler.verify_token(token)
        if not valid:
            return False, payload
        
        # 检查 token 类型
        if payload.get("type") != JWTConfig.TOKEN_TYPE_ACCESS:
            return False, {"error": "不是有效的 Access Token"}
        
        return True, payload
    
    @staticmethod
    def verify_refresh_token(token: str) -> Tuple[bool, Optional[Dict]]:
        """
        验证刷新令牌
        
        Args:
            token: JWT Token 字符串
        
        Returns:
            (是否有效, 解码后的 payload) 元组
        """
        valid, payload = JWTHandler.verify_token(token)
        if not valid:
            return False, payload
        
        # 检查 token 类型
        if payload.get("type") != JWTConfig.TOKEN_TYPE_REFRESH:
            return False, {"error": "不是有效的 Refresh Token"}
        
        return True, payload
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        使用刷新令牌生成新的访问令牌
        
        Args:
            refresh_token: 刷新令牌
        
        Returns:
            (是否成功, 新的access_token, 错误信息) 元组
        """
        valid, payload = JWTHandler.verify_refresh_token(refresh_token)
        if not valid:
            return False, None, payload.get("error", "Token验证失败")
        
        # 生成新的 access token
        new_access_token = JWTHandler.generate_access_token(
            user_id=payload.get("sub"),
            username=payload.get("username"),
            role=UserRole.USER,  # 默认为 USER，实际应从数据库获取
            permissions=[]
        )
        
        return True, new_access_token, None
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """
        解码 Token（不验证过期时间）
        
        Args:
            token: JWT Token 字符串
        
        Returns:
            解码后的 payload，或 None 如果解码失败
        """
        try:
            payload = jwt.decode(
                token,
                JWTConfig.SECRET_KEY,
                algorithms=[JWTConfig.ALGORITHM],
                options={"verify_exp": False}  # 不验证过期时间
            )
            return payload
        except jwt.InvalidTokenError:
            return None
