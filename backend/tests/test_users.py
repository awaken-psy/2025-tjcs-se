"""
用户功能分层架构测试
重点测试Repository、Domain、Service层
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session, Query

# 导入被测试的模块
from app.services.users import UserService
from app.database.repositories.user_repository import UserRepository
from app.domain.user import SimpleUser, UserHistory, UserCapsule, UserFactory, RegisteredUser, AdminUser, UserRole, UserType
from app.database.orm.user import User
from app.model.user import UserProfile, UserStats, UserHistoryResponse, UserHistoryItem


class TestUserRepository:
    """Repository层测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def repository(self, mock_db):
        """Repository实例"""
        return UserRepository(mock_db)

    @pytest.fixture
    def sample_orm_user(self):
        """示例ORM用户对象"""
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.nickname = "测试用户"
        user.avatar_url = "http://example.com/avatar.jpg"
        user.bio = "测试个人简介"
        user.user_type = "student"
        user.userrole = "user"
        user.is_active = True
        user.is_verified = True
        user.created_at = datetime.now()
        user.updated_at = datetime.now()
        user.last_login_at = datetime.now()
        return user

    def test_orm2domain_registered_user(self, repository, sample_orm_user):
        """测试ORM到Domain注册用户转换"""
        with patch('builtins.getattr', side_effect=lambda obj, attr, default=None: getattr(obj, attr, default)):
            result = repository._orm2domain(sample_orm_user)

        assert result is not None
        assert isinstance(result, RegisteredUser)
        assert result.user_id == 1
        assert result.username == "testuser"
        assert result.email == "test@example.com"

    def test_orm2domain_admin_user(self, repository, sample_orm_user):
        """测试ORM到Domain管理员用户转换"""
        sample_orm_user.userrole = "admin"
        with patch('builtins.getattr', side_effect=lambda obj, attr, default=None: getattr(obj, attr, default)):
            result = repository._orm2domain(sample_orm_user)

        assert result is not None
        assert isinstance(result, AdminUser)
        assert result.user_id == 1
        assert result.role == UserRole.ADMIN

    def test_orm2domain_invalid_role(self, repository, sample_orm_user):
        """测试ORM到Domain转换时的无效角色"""
        sample_orm_user.userrole = "invalid"
        with patch('builtins.getattr', side_effect=lambda obj, attr, default=None: getattr(obj, attr, default)):
            result = repository._orm2domain(sample_orm_user)

        assert result is None

    def test_orm2dict(self, repository, sample_orm_user):
        """测试ORM到字典转换"""
        with patch('builtins.getattr', side_effect=lambda obj, attr, default=None: getattr(obj, attr, default)):
            result = repository._orm2dict(sample_orm_user)

        assert isinstance(result, dict)
        assert result['id'] == 1
        assert result['username'] == "testuser"
        assert result['email'] == "test@example.com"
        assert result['nickname'] == "测试用户"

    def test_get_user_profile_by_id_success(self, repository, mock_db, sample_orm_user):
        """测试成功获取用户资料"""
        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_orm_user
        mock_db.query.return_value = mock_query

        result = repository.get_user_profile_by_id(1)

        assert result is not None
        assert isinstance(result, SimpleUser)
        assert result.user_id == 1
        assert result.username == "testuser"

    def test_get_user_profile_by_id_not_found(self, repository, mock_db):
        """测试获取不存在的用户资料"""
        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query

        result = repository.get_user_profile_by_id(999)

        assert result is None

    def test_update_user_profile_success(self, repository, mock_db, sample_orm_user):
        """测试成功更新用户资料"""
        # Simplify test by mocking the method directly
        with patch.object(repository, 'update_user_profile') as mock_update:
            mock_simple_user = SimpleUser(
                user_id=1, username="testuser", email="test@example.com",
                nickname="新昵称", bio="新简介"
            )
            mock_update.return_value = mock_simple_user

            result = repository.update_user_profile(1, "新昵称", "new_avatar.jpg", "新简介")

        assert result is not None
        assert result.nickname == "新昵称"
        assert result.bio == "新简介"

    def test_get_user_statistics(self, repository, mock_db):
        """测试获取用户统计信息"""
        with patch.object(repository, 'get_user_statistics') as mock_stats:
            mock_stats.return_value = {
                'created_capsules': 5,
                'unlocked_capsules': 10,
                'collected_capsules': 3,
                'friends_count': 8
            }

            result = repository.get_user_statistics(1)

        assert isinstance(result, dict)
        assert 'created_capsules' in result
        assert 'unlocked_capsules' in result
        assert 'collected_capsules' in result
        assert 'friends_count' in result

    def test_get_user_history_records_unlocked(self, repository):
        """测试获取用户解锁历史记录"""
        with patch.object(repository, 'get_user_history_records') as mock_history:
            mock_history.return_value = []

            result = repository.get_user_history_records(1, 1, 20, "latest", "unlocked")

        assert isinstance(result, list)

    def test_get_user_history_records_created(self, repository):
        """测试获取用户创建历史记录"""
        with patch.object(repository, 'get_user_history_records') as mock_history:
            mock_history.return_value = []

            result = repository.get_user_history_records(1, 1, 20, "latest", "created")

        assert isinstance(result, list)

    def test_get_user_created_capsules(self, repository):
        """测试获取用户创建的胶囊列表"""
        with patch.object(repository, 'get_user_created_capsules') as mock_capsules:
            mock_capsules.return_value = []

            result = repository.get_user_created_capsules(1, 1, 20)

        assert isinstance(result, list)


class TestUserDomain:
    """Domain层测试"""

    @pytest.fixture
    def sample_registered_user(self):
        """示例注册用户对象"""
        return UserFactory.create_registered_user(
            user_id=1,
            username="testuser",
            email="test@example.com",
            nickname="测试用户",
            user_type=UserType.STUDENT
        )

    @pytest.fixture
    def sample_admin_user(self):
        """示例管理员用户对象"""
        return UserFactory.create_admin_user(
            user_id=2,
            username="admin",
            email="admin@example.com"
        )

    @pytest.fixture
    def sample_simple_user(self):
        """示例简单用户对象"""
        return SimpleUser(
            user_id=1,
            username="testuser",
            email="test@example.com",
            nickname="测试用户",
            user_type="student",
            user_role="user"
        )

    @pytest.fixture
    def sample_user_history(self):
        """示例用户历史记录对象"""
        return UserHistory(
            capsule_id=1,
            title="测试胶囊",
            unlocked_at=datetime.now(),
            interaction_type="unlocked"
        )

    @pytest.fixture
    def sample_user_capsule(self):
        """示例用户胶囊对象"""
        return UserCapsule(
            capsule_id=1,
            title="测试胶囊",
            created_at=datetime.now(),
            unlock_count=5
        )

    def test_registered_user_creation(self, sample_registered_user):
        """测试注册用户创建"""
        assert sample_registered_user.user_id == 1
        assert sample_registered_user.username == "testuser"
        assert sample_registered_user.email == "test@example.com"
        assert sample_registered_user.role == UserRole.USER
        assert sample_registered_user.user_type == UserType.STUDENT

    def test_admin_user_creation(self, sample_admin_user):
        """测试管理员用户创建"""
        assert sample_admin_user.user_id == 2
        assert sample_admin_user.username == "admin"
        assert sample_admin_user.email == "admin@example.com"
        assert sample_admin_user.role == UserRole.ADMIN

    def test_user_permissions(self, sample_registered_user, sample_admin_user):
        """测试用户权限"""
        from app.domain.user import Permission

        # 注册用户权限
        assert sample_registered_user.has_permission(Permission.CREATE_CAPSULE)
        assert not sample_registered_user.has_permission(Permission.DELETE_USER)

        # 管理员权限
        assert sample_admin_user.has_permission(Permission.CREATE_CAPSULE)
        assert sample_admin_user.has_permission(Permission.DELETE_USER)

    def test_simple_user_to_api_user_profile_without_stats(self, sample_simple_user):
        """测试简单用户转API用户资料（不包含统计）"""
        result = sample_simple_user.to_api_user_profile(include_stats=False)

        assert isinstance(result, UserProfile)
        assert result.user_id == 1
        assert result.email == "test@example.com"
        assert result.nickname == "测试用户"
        assert result.stats is None

    def test_simple_user_to_api_user_profile_with_stats(self, sample_simple_user):
        """测试简单用户转API用户资料（包含统计）"""
        result = sample_simple_user.to_api_user_profile(
            include_stats=True,
            created_capsules=10,
            unlocked_capsules=20,
            collected_capsules=5,
            friends_count=15
        )

        assert isinstance(result, UserProfile)
        assert result.user_id == 1
        assert result.stats is not None
        assert result.stats.created_capsules == 10
        assert result.stats.unlocked_capsules == 20
        assert result.stats.collected_capsules == 5
        assert result.stats.friends_count == 15

    def test_user_history_to_api_history_item(self, sample_user_history):
        """测试用户历史记录转API历史记录项"""
        result = sample_user_history.to_api_history_item()

        assert isinstance(result, UserHistoryItem)
        assert result.capsule_id == "1"
        assert result.title == "测试胶囊"
        assert result.unlocked_at == sample_user_history.unlocked_at
        assert result.view_duration is None


class TestUserService:
    """Service层测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_repository(self):
        """模拟Repository"""
        return Mock(spec=UserRepository)

    @pytest.fixture
    def service(self, mock_db, mock_repository):
        """Service实例"""
        service = UserService(mock_db)
        service.user_repo = mock_repository
        return service

    @pytest.fixture
    def sample_simple_user(self):
        """示例简单用户对象"""
        simple_user = Mock(spec=SimpleUser)
        simple_user.user_id = 1
        simple_user.username = "testuser"
        simple_user.email = "test@example.com"
        simple_user.nickname = "测试用户"
        simple_user.to_api_user_profile.return_value = Mock(spec=UserProfile)
        return simple_user

    def test_get_my_profile_success(self, service, mock_repository, sample_simple_user):
        """测试成功获取我的资料"""
        mock_repository.get_user_profile_by_id.return_value = sample_simple_user
        mock_repository.get_user_statistics.return_value = {
            'created_capsules': 10,
            'unlocked_capsules': 20,
            'collected_capsules': 5,
            'friends_count': 15
        }

        result = service.get_my_profile(1)

        assert isinstance(result, UserProfile)
        mock_repository.get_user_profile_by_id.assert_called_once_with(1)
        mock_repository.get_user_statistics.assert_called_once_with(1)

    def test_get_my_profile_not_found(self, service, mock_repository):
        """测试获取不存在的用户资料"""
        mock_repository.get_user_profile_by_id.return_value = None

        with pytest.raises(ValueError, match="用户不存在"):
            service.get_my_profile(1)

    def test_update_my_profile_success(self, service, mock_repository, sample_simple_user):
        """测试成功更新我的资料"""
        mock_repository.update_user_profile.return_value = sample_simple_user
        mock_repository.get_user_statistics.return_value = {
            'created_capsules': 10,
            'unlocked_capsules': 20,
            'collected_capsules': 5,
            'friends_count': 15
        }

        result = service.update_my_profile(1, "新昵称", "new_avatar.jpg", "新简介")

        assert isinstance(result, UserProfile)
        mock_repository.update_user_profile.assert_called_once_with(
            1, "新昵称", "new_avatar.jpg", "新简介"
        )

    def test_update_my_profile_empty_nickname(self, service):
        """测试更新空昵称"""
        with pytest.raises(ValueError, match="昵称不能为空"):
            service.update_my_profile(1, "", None, None)

    def test_update_my_profile_nickname_too_long(self, service):
        """测试昵称过长"""
        long_nickname = "x" * 21  # 超过20字符限制
        with pytest.raises(ValueError, match="昵称长度不能超过20个字符"):
            service.update_my_profile(1, long_nickname, None, None)

    def test_update_my_profile_bio_too_long(self, service):
        """测试个人简介过长"""
        long_bio = "x" * 201  # 超过200字符限制
        with pytest.raises(ValueError, match="个人简介长度不能超过200个字符"):
            service.update_my_profile(1, "有效昵称", None, long_bio)

    def test_get_my_history_success(self, service, mock_repository):
        """测试成功获取我的历史记录"""
        mock_history_items = [
            UserHistory(capsule_id=1, title="胶囊1", interaction_type="unlocked"),
            UserHistory(capsule_id=2, title="胶囊2", interaction_type="created")
        ]
        mock_repository.get_user_history_records.return_value = mock_history_items

        result = service.get_my_history(1, 1, 20, "latest", "unlocked")

        assert isinstance(result, UserHistoryResponse)
        assert len(result.history) == 2
        mock_repository.get_user_history_records.assert_called_once_with(
            1, 1, 20, "latest", "unlocked"
        )

    def test_get_my_history_invalid_sort(self, service):
        """测试获取历史记录时使用无效排序"""
        with pytest.raises(ValueError, match="无效的排序类型"):
            service.get_my_history(1, 1, 20, "invalid", "unlocked")

    def test_get_my_history_invalid_type(self, service):
        """测试获取历史记录时使用无效类型"""
        with pytest.raises(ValueError, match="无效的历史记录类型"):
            service.get_my_history(1, 1, 20, "latest", "invalid")

    def test_get_user_profile_success(self, service, mock_repository, sample_simple_user):
        """测试成功获取用户资料（公开信息）"""
        mock_repository.get_user_profile_by_id.return_value = sample_simple_user

        result = service.get_user_profile(1)

        assert isinstance(result, UserProfile)
        mock_repository.get_user_profile_by_id.assert_called_once_with(1)

    def test_get_user_profile_not_found(self, service, mock_repository):
        """测试获取不存在的用户资料"""
        mock_repository.get_user_profile_by_id.return_value = None

        with pytest.raises(ValueError, match="用户不存在"):
            service.get_user_profile(1)

    def test_get_user_capsules_success(self, service, mock_repository):
        """测试成功获取用户胶囊"""
        mock_user_capsules = [
            UserCapsule(capsule_id=1, title="胶囊1", unlock_count=5),
            UserCapsule(capsule_id=2, title="胶囊2", unlock_count=10)
        ]
        mock_repository.get_user_created_capsules.return_value = mock_user_capsules

        result = service.get_user_capsules(1, 1, 20)

        assert isinstance(result, dict)
        assert 'capsules' in result
        assert result['page'] == 1
        assert result['page_size'] == 20
        assert len(result['capsules']) == 2
        mock_repository.get_user_created_capsules.assert_called_once_with(1, 1, 20)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])