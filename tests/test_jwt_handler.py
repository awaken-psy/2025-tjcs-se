"""
JWT Token 处理器测试
"""
import pytest
from datetime import datetime, timedelta, timezone
from auth.jwt_handler import JWTHandler, JWTConfig
from models.core.user import UserRole, Permission


class TestJWTHandler:
    """JWT 处理器测试"""
    
    def test_generate_access_token(self):
        """测试生成访问令牌"""
        token = JWTHandler.generate_access_token(
            user_id="user_001",
            username="测试用户",
            role=UserRole.USER,
            permissions=["read:capsule", "create:capsule"]
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_access_token(self):
        """测试验证访问令牌"""
        # 生成令牌
        token = JWTHandler.generate_access_token(
            user_id="user_001",
            username="测试用户",
            role=UserRole.USER,
            permissions=["read:capsule"]
        )
        
        # 验证令牌
        valid, payload = JWTHandler.verify_access_token(token)
        
        assert valid is True
        assert payload is not None
        assert payload["sub"] == "user_001"
        assert payload["username"] == "测试用户"
        assert payload["role"] == "user"
    
    def test_verify_invalid_token(self):
        """测试验证无效令牌"""
        valid, payload = JWTHandler.verify_access_token("invalid_token")
        
        assert valid is False
        assert payload is not None
        assert "error" in payload
    
    def test_generate_refresh_token(self):
        """测试生成刷新令牌"""
        token = JWTHandler.generate_refresh_token(
            user_id="user_001",
            username="测试用户"
        )
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_verify_refresh_token(self):
        """测试验证刷新令牌"""
        # 生成令牌
        token = JWTHandler.generate_refresh_token(
            user_id="user_001",
            username="测试用户"
        )
        
        # 验证令牌
        valid, payload = JWTHandler.verify_refresh_token(token)
        
        assert valid is True
        assert payload is not None
        assert payload["sub"] == "user_001"
        assert payload["type"] == JWTConfig.TOKEN_TYPE_REFRESH
    
    def test_refresh_access_token(self):
        """测试刷新访问令牌"""
        # 生成刷新令牌
        refresh_token = JWTHandler.generate_refresh_token(
            user_id="user_001",
            username="测试用户"
        )
        
        # 使用刷新令牌生成新的访问令牌
        success, new_token, error = JWTHandler.refresh_access_token(refresh_token)
        
        assert success is True
        assert new_token is not None
        assert error is None
        
        # 验证新的访问令牌
        valid, payload = JWTHandler.verify_access_token(new_token)
        assert valid is True
    
    def test_token_type_validation(self):
        """测试令牌类型验证"""
        # 生成访问令牌
        access_token = JWTHandler.generate_access_token(
            user_id="user_001",
            username="测试用户",
            role=UserRole.USER
        )
        
        # 用访问令牌验证刷新令牌（应该失败）
        valid, payload = JWTHandler.verify_refresh_token(access_token)
        assert valid is False
        
        # 生成刷新令牌
        refresh_token = JWTHandler.generate_refresh_token(
            user_id="user_001",
            username="测试用户"
        )
        
        # 用刷新令牌验证访问令牌（应该失败）
        valid, payload = JWTHandler.verify_access_token(refresh_token)
        assert valid is False
    
    def test_decode_token(self):
        """测试解码令牌"""
        token = JWTHandler.generate_access_token(
            user_id="user_001",
            username="测试用户",
            role=UserRole.USER
        )
        
        payload = JWTHandler.decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user_001"
        assert payload["username"] == "测试用户"
    
    def test_custom_expiry(self):
        """测试自定义过期时间"""
        # 创建1小时后过期的令牌
        token = JWTHandler.generate_access_token(
            user_id="user_001",
            username="测试用户",
            role=UserRole.USER,
            expires_hours=1
        )
        
        valid, payload = JWTHandler.verify_access_token(token)
        assert valid is True
        
        # 验证过期时间
        assert payload["exp"] > payload["iat"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
