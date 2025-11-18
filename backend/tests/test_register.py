"""
用户注册功能测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.config import Base, get_db
from app.auth.password import password_manager
from app.database.repositories.user_repository import UserRepository

# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_client():
    """创建测试客户端"""
    # 创建测试数据库表
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client

    # 清理测试数据库
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def user_repository():
    """创建用户仓库实例"""
    db = TestingSessionLocal()
    repository = UserRepository(db)
    yield repository
    db.close()


class TestUserRegister:
    """用户注册测试类"""

    def test_register_success(self, test_client):
        """测试成功注册用户"""
        # 准备测试数据
        register_data = {
            "email": "test@example.com",
            "password": "Test123456",
            "nickname": "测试用户",
            "student_id": "20230001",
            "verify_code": "123456"  # 测试时跳过验证码验证
        }

        # 发送注册请求
        response = test_client.post("/api/v1/auth/register", json=register_data)

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "注册成功"
        assert "data" in data
        assert data["data"]["email"] == "test@example.com"
        assert data["data"]["nickname"] == "测试用户"
        assert "token" in data["data"]
        assert "refresh_token" in data["data"]

    def test_register_duplicate_email(self, test_client):
        """测试重复邮箱注册"""
        # 先注册一个用户
        register_data = {
            "email": "duplicate@example.com",
            "password": "Test123456",
            "nickname": "测试用户1",
            "verify_code": "123456"
        }
        test_client.post("/api/v1/auth/register", json=register_data)

        # 尝试用相同邮箱注册
        duplicate_data = {
            "email": "duplicate@example.com",
            "password": "Test123456",
            "nickname": "测试用户2",
            "verify_code": "123456"
        }
        response = test_client.post("/api/v1/auth/register", json=duplicate_data)

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "该邮箱或用户名已被注册" in data["message"]

    def test_register_weak_password(self, test_client):
        """测试弱密码注册"""
        register_data = {
            "email": "weakpass@example.com",
            "password": "123",  # 弱密码
            "nickname": "测试用户",
            "verify_code": "123456"
        }

        response = test_client.post("/api/v1/auth/register", json=register_data)

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "密码长度至少需要8位" in data["message"]

    def test_register_missing_required_fields(self, test_client):
        """测试缺少必填字段"""
        # 缺少邮箱
        register_data = {
            "password": "Test123456",
            "nickname": "测试用户",
            "verify_code": "123456"
        }

        response = test_client.post("/api/v1/auth/register", json=register_data)

        # 验证响应
        assert response.status_code == 422  # 422 Unprocessable Entity

    def test_check_email_availability(self, test_client):
        """测试邮箱可用性检查"""
        # 检查可用邮箱
        response = test_client.get("/api/v1/auth/check-email/available@example.com")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["available"] is True

        # 注册一个用户
        register_data = {
            "email": "taken@example.com",
            "password": "Test123456",
            "nickname": "测试用户",
            "verify_code": "123456"
        }
        test_client.post("/api/v1/auth/register", json=register_data)

        # 检查已占用邮箱
        response = test_client.get("/api/v1/auth/check-email/taken@example.com")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["available"] is False

    def test_check_student_id_availability(self, test_client):
        """测试学号可用性检查"""
        # 检查可用学号
        response = test_client.get("/api/v1/auth/check-student-id/20230002")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["available"] is True

        # 注册一个带学号的用户
        register_data = {
            "email": "student@example.com",
            "password": "Test123456",
            "nickname": "测试学生",
            "student_id": "20230003",
            "verify_code": "123456"
        }
        test_client.post("/api/v1/auth/register", json=register_data)

        # 检查已占用学号
        response = test_client.get("/api/v1/auth/check-student-id/20230003")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["available"] is False


class TestPasswordManager:
    """密码管理器测试类"""

    def test_password_hashing(self):
        """测试密码哈希"""
        password = "Test123456"

        # 哈希密码
        success, hashed_password = password_manager.hash_password(password)
        assert success is True
        assert hashed_password is not None
        assert hashed_password != password

        # 验证密码
        verify_success, message = password_manager.verify_password(password, hashed_password)
        assert verify_success is True
        assert message == "密码验证成功"

    def test_password_verification_failure(self):
        """测试密码验证失败"""
        password = "Test123456"
        wrong_password = "WrongPassword"

        # 哈希密码
        success, hashed_password = password_manager.hash_password(password)
        assert success is True

        # 使用错误密码验证
        verify_success, message = password_manager.verify_password(wrong_password, hashed_password)
        assert verify_success is False
        assert message == "密码错误"

    def test_password_strength_validation(self):
        """测试密码强度验证"""
        # 测试强密码
        strong_password = "StrongPass123"
        is_valid, message = password_manager.validate_password_strength(strong_password)
        assert is_valid is True

        # 测试短密码
        short_password = "123"
        is_valid, message = password_manager.validate_password_strength(short_password)
        assert is_valid is False
        assert "密码长度至少需要8位" in message

        # 测试无数字密码
        no_digit_password = "NoDigitsHere"
        is_valid, message = password_manager.validate_password_strength(no_digit_password)
        assert is_valid is False
        assert "密码必须包含至少一个数字" in message

        # 测试无字母密码
        no_letter_password = "12345678"
        is_valid, message = password_manager.validate_password_strength(no_letter_password)
        assert is_valid is False
        assert "密码必须包含至少一个字母" in message


class TestUserRepository:
    """用户仓库测试类"""

    def test_create_user(self, user_repository):
        """测试创建用户"""
        user_data = user_repository.create_user(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            nickname="测试用户",
            student_id="20230001"
        )

        assert user_data is not None
        assert user_data["username"] == "testuser"
        assert user_data["email"] == "test@example.com"
        assert user_data["nickname"] == "测试用户"
        assert user_data["campus_id"] == "20230001"

    def test_get_user_by_email(self, user_repository):
        """测试通过邮箱获取用户"""
        # 先创建用户
        user_repository.create_user(
            username="testuser2",
            email="test2@example.com",
            password_hash="hashed_password",
            nickname="测试用户2"
        )

        # 通过邮箱获取用户
        user_data = user_repository.get_user_by_email("test2@example.com")

        assert user_data is not None
        assert user_data["email"] == "test2@example.com"
        assert user_data["username"] == "testuser2"

    def test_get_user_by_email_or_username(self, user_repository):
        """测试通过邮箱或用户名获取用户"""
        # 先创建用户
        user_repository.create_user(
            username="testuser3",
            email="test3@example.com",
            password_hash="hashed_password",
            nickname="测试用户3"
        )

        # 通过邮箱获取
        user_by_email = user_repository.get_user_by_email_or_username("test3@example.com")
        assert user_by_email is not None
        assert user_by_email["email"] == "test3@example.com"

        # 通过用户名获取
        user_by_username = user_repository.get_user_by_email_or_username("testuser3")
        assert user_by_username is not None
        assert user_by_username["username"] == "testuser3"

    def test_check_email_exists(self, user_repository):
        """测试检查邮箱是否存在"""
        # 先创建用户
        user_repository.create_user(
            username="testuser4",
            email="test4@example.com",
            password_hash="hashed_password",
            nickname="测试用户4"
        )

        # 检查存在的邮箱
        exists = user_repository.check_email_exists("test4@example.com")
        assert exists is True

        # 检查不存在的邮箱
        not_exists = user_repository.check_email_exists("nonexistent@example.com")
        assert not_exists is False

    def test_check_student_id_exists(self, user_repository):
        """测试检查学号是否存在"""
        # 先创建带学号的用户
        user_repository.create_user(
            username="testuser5",
            email="test5@example.com",
            password_hash="hashed_password",
            nickname="测试用户5",
            student_id="20230005"
        )

        # 检查存在的学号
        exists = user_repository.check_student_id_exists("20230005")
        assert exists is True

        # 检查不存在的学号
        not_exists = user_repository.check_student_id_exists("99999999")
        assert not_exists is False

    def test_mark_user_as_verified(self, user_repository):
        """测试标记用户为已验证"""
        # 先创建用户
        user_data = user_repository.create_user(
            username="testuser6",
            email="test6@example.com",
            password_hash="hashed_password",
            nickname="测试用户6"
        )

        # 初始状态应为未验证
        assert user_data["is_verified"] is False

        # 标记为已验证
        success = user_repository.mark_user_as_verified(user_data["id"])
        assert success is True

        # 验证状态已更新
        updated_user = user_repository.get_user_by_id(user_data["id"])
        assert updated_user["is_verified"] is True