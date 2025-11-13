"""
JWT Token 处理器测试模块
"""
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from app.auth.jwt_handler import (
    JWTHandler, JWTConfig,
    AccessTokenPayload, RefreshTokenPayload
)
from app.domain.user import (
    UserRole, Permission, 
    BaseUser, AuthenticatedUser, AdminUser, UserFactory
)


@pytest.fixture
def test_user():
    """测试用户fixture"""
    return UserFactory.create_authenticated_user(
        user_id="user_001",
        username="测试用户"
    )


@pytest.fixture
def admin_user():
    """管理员用户fixture"""
    return UserFactory.create_admin_user(
        user_id="admin_001",
        username="管理员",
        admin_level=1
    )


@pytest.fixture
def guest_user():
    """访客用户fixture"""
    return UserFactory.create_guest_user()


def test_generate_access_token(test_user):
    """测试生成访问令牌"""
    # 生成访问令牌
    token = JWTHandler.generate_access_token(
        user_id=test_user.user_id,
        username=test_user.username,
        role=test_user.role,
        permissions=list(test_user.permissions),
        expires_hours=1
    )
    
    # 验证令牌不为空
    assert token is not None
    assert isinstance(token, str)
    
    # 解码令牌验证内容
    decoded = jwt.decode(
        token,
        JWTConfig.SECRET_KEY,
        algorithms=[JWTConfig.ALGORITHM]
    )
    
    assert decoded["sub"] == test_user.user_id
    assert decoded["username"] == test_user.username
    assert decoded["role"] == test_user.role.value
    assert decoded["token_type"] == JWTConfig.TokenType.TOKEN_TYPE_ACCESS


def test_generate_access_token_from_user(test_user, admin_user, guest_user):
    """测试从用户对象生成访问令牌"""
    # 从普通用户生成令牌
    token = JWTHandler.generate_access_token_from_user(test_user)
    assert token is not None
    
    # 从管理员生成令牌
    token = JWTHandler.generate_access_token_from_user(admin_user)
    assert token is not None
    
    # 测试访客用户应该抛出异常
    with pytest.raises(ValueError):
        JWTHandler.generate_access_token_from_user(guest_user)


def test_generate_refresh_token(test_user):
    """测试生成刷新令牌"""
    # 生成刷新令牌
    token = JWTHandler.generate_refresh_token(
        user_id=test_user.user_id,
        username=test_user.username,
        expires_days=1
    )
    
    # 验证令牌不为空
    assert token is not None
    assert isinstance(token, str)
    
    # 解码令牌验证内容
    decoded = jwt.decode(
        token,
        JWTConfig.SECRET_KEY,
        algorithms=[JWTConfig.ALGORITHM]
    )
    
    assert decoded["sub"] == test_user.user_id
    assert decoded["username"] == test_user.username
    assert decoded["token_type"] == JWTConfig.TokenType.TOKEN_TYPE_REFRESH


def test_generate_refresh_token_from_user(test_user, admin_user, guest_user):
    """测试从用户对象生成刷新令牌"""
    # 从普通用户生成令牌
    token = JWTHandler.generate_refresh_token_from_user(test_user)
    assert token is not None
    
    # 从管理员生成令牌
    token = JWTHandler.generate_refresh_token_from_user(admin_user)
    assert token is not None
    
    # 测试访客用户应该抛出异常
    with pytest.raises(ValueError):
        JWTHandler.generate_refresh_token_from_user(guest_user)


def test_verify_token_valid(test_user):
    """测试验证有效令牌"""
    # 生成有效令牌
    token = JWTHandler.generate_access_token(
        user_id=test_user.user_id,
        username=test_user.username,
        role=test_user.role,
        permissions=[]
    )
    
    # 验证令牌
    valid, payload, error = JWTHandler.verify_token(token)
    
    assert valid is True
    assert payload is not None
    assert error is None
    assert payload["sub"] == test_user.user_id


def test_verify_token_invalid():
    """测试验证无效令牌"""
    # 使用无效令牌
    invalid_token = "invalid.jwt.token"
    
    valid, payload, error = JWTHandler.verify_token(invalid_token)
    
    assert valid is False
    assert payload is None
    assert error is not None
    assert "无效" in error


@patch('jwt.decode')
def test_verify_token_expired(mock_decode):
    """测试验证过期令牌"""
    # 模拟过期错误
    mock_decode.side_effect = jwt.ExpiredSignatureError("Token已过期")
    
    valid, payload, error = JWTHandler.verify_token("any.token")
    
    assert valid is False
    assert payload is None
    assert error is not None
    assert "过期" in error


def test_verify_access_token(test_user):
    """测试验证访问令牌"""
    # 生成访问令牌
    token = JWTHandler.generate_access_token(
        user_id=test_user.user_id,
        username=test_user.username,
        role=test_user.role,
        permissions=[]
    )
    
    # 验证访问令牌
    valid, payload, error = JWTHandler.verify_access_token(token)
    
    assert valid is True
    assert isinstance(payload, AccessTokenPayload)
    assert payload.sub == test_user.user_id
    assert payload.role == test_user.role
    assert payload.token_type == JWTConfig.TokenType.TOKEN_TYPE_ACCESS


def test_verify_refresh_token(test_user):
    """测试验证刷新令牌"""
    # 生成刷新令牌
    token = JWTHandler.generate_refresh_token(
        user_id=test_user.user_id,
        username=test_user.username
    )
    
    # 验证刷新令牌
    valid, payload, error = JWTHandler.verify_refresh_token(token)
    
    assert valid is True
    assert isinstance(payload, RefreshTokenPayload)
    assert payload.sub == test_user.user_id
    assert payload.token_type == JWTConfig.TokenType.TOKEN_TYPE_REFRESH


def test_refresh_access_token(test_user):
    """测试刷新访问令牌"""
    # 生成刷新令牌
    refresh_token = JWTHandler.generate_refresh_token(
        user_id=test_user.user_id,
        username=test_user.username
    )
    
    # 刷新令牌
    success, new_access_token, new_refresh_token, error = JWTHandler.refresh_access_token(refresh_token)
    
    assert success is True
    assert new_access_token is not None
    assert new_refresh_token is not None
    assert error is None
    
    # 验证新的访问令牌有效
    valid, payload, _ = JWTHandler.verify_access_token(new_access_token)
    assert valid is True
    assert payload.sub == test_user.user_id


def test_refresh_access_token_invalid():
    """测试刷新无效的访问令牌"""
    # 使用无效的刷新令牌
    invalid_refresh_token = "invalid.refresh.token"
    
    success, new_access_token, new_refresh_token, error = JWTHandler.refresh_access_token(invalid_refresh_token)
    
    assert success is False
    assert new_access_token is None
    assert new_refresh_token is None
    assert error is not None


def test_payload_validation(test_user):
    """测试负载验证"""
    # 手动创建一个缺少必要字段的负载
    incomplete_payload = {
        "sub": test_user.user_id,
        "username": test_user.username,
        # 缺少 role, token_type, iat, exp
    }
    
    # 编码为令牌
    invalid_token = jwt.encode(
        incomplete_payload,
        JWTConfig.SECRET_KEY,
        algorithm=JWTConfig.ALGORITHM
    )
    
    # 验证应该失败
    valid, payload, error = JWTHandler.verify_access_token(invalid_token)
    assert valid is False
    assert payload is None
    assert error is not None


@patch('app.auth.jwt_handler.datetime')
def test_token_expiration(mock_datetime, test_user):
    """测试令牌过期时间设置"""
    # 模拟当前时间
    mock_now = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    mock_datetime.now.return_value = mock_now
    
    # 生成令牌，设置过期时间为1小时
    token = JWTHandler.generate_access_token(
        user_id=test_user.user_id,
        username=test_user.username,
        role=test_user.role,
        permissions=[],
        expires_hours=1
    )
    
    # 解码令牌检查过期时间（禁用过期验证）
    decoded = jwt.decode(
        token,
        JWTConfig.SECRET_KEY,
        algorithms=[JWTConfig.ALGORITHM],
        options={"verify_exp": False}
    )
    
    # 过期时间应该是当前时间+1小时
    expected_exp = mock_now + timedelta(hours=1)
    actual_exp = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    
    # 允许1秒的误差
    assert abs(actual_exp.timestamp() - expected_exp.timestamp()) < 1


def test_cross_token_type_validation(test_user):
    """测试跨令牌类型验证"""
    # 生成一个访问令牌
    access_token = JWTHandler.generate_access_token(
        user_id=test_user.user_id,
        username=test_user.username,
        role=test_user.role,
        permissions=[]
    )
    
    # 尝试用刷新令牌验证器验证访问令牌
    valid, payload, error = JWTHandler.verify_refresh_token(access_token)
    
    # 应该验证失败，因为令牌类型不匹配
    assert valid is False
    assert payload is None
    assert error is not None