"""
时光胶囊分层架构测试
重点测试Repository、Domain、Service层
"""
import pytest
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session, Query

# 导入被测试的模块
from app.services.capsule import CapsuleService, CapsuleManager
from app.database.repositories.capsule_repository import CapsuleRepository
from app.domain.capsule import Capsule as CapsuleDomain, CapsuleStatus, Visibility, ContentType
from app.database.orm.capsule import Capsule
from app.model.capsule import (
    CapsuleCreateRequest, CapsuleUpdateRequest, CapsuleDraftRequest,
    Location, UnlockConditions, CapsuleBasic, CapsuleDetail,
    CapsuleCreateResponse, CapsuleUpdateResponse, CapsuleDraftResponse,
    Creator, CapsuleStats
)


class TestCapsuleRepository:
    """Repository层测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def repository(self, mock_db):
        """Repository实例"""
        return CapsuleRepository(mock_db)

    @pytest.fixture
    def sample_orm_capsule(self):
        """示例ORM胶囊对象"""
        capsule = Mock(spec=Capsule)
        capsule.id = "test_capsule_123"
        capsule.user_id = 1
        capsule.title = "测试胶囊"
        capsule.text_content = "测试内容"
        capsule.visibility = "public"
        capsule.status = "published"
        capsule.created_at = datetime.now(timezone.utc)
        capsule.updated_at = datetime.now(timezone.utc)
        capsule.latitude = 31.2304
        capsule.longitude = 121.4737
        capsule.tag_json = json.dumps(["测试", "胶囊"])
        return capsule

    def test_find_by_id_success(self, repository, mock_db, sample_orm_capsule):
        """测试成功查找胶囊"""
        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_orm_capsule
        mock_db.query.return_value = mock_query

        result = repository.find_by_id("test_capsule_123")

        assert result is not None
        assert result.capsule_id == "test_capsule_123"
        assert isinstance(result, CapsuleDomain)

    def test_save_domain_object(self, repository, mock_db):
        """测试保存Domain对象"""
        domain = CapsuleDomain(
            capsule_id="new_capsule",
            owner_id="1",
            title="新胶囊",
            content="新内容"
        )

        mock_orm = Mock()
        mock_orm.id = "new_capsule"
        
        with patch.object(repository, '_domain_to_orm', return_value=mock_orm):
            with patch.object(repository, '_orm_to_domain', return_value=domain):
                result = repository.save(domain)

        assert result == domain
        mock_db.add.assert_called_once_with(mock_orm)
        mock_db.commit.assert_called_once()


class TestCapsuleDomain:
    """Domain层测试"""

    @pytest.fixture
    def sample_domain_capsule(self):
        """示例Domain胶囊对象"""
        return CapsuleDomain(
            capsule_id="test_capsule_123",
            owner_id="1",
            title="测试胶囊",
            content="测试内容",
            visibility=Visibility.CAMPUS,
            status=CapsuleStatus.LOCKED
        )

    def test_can_view_by_owner(self, sample_domain_capsule):
        """测试所有者可以查看"""
        assert sample_domain_capsule.can_view_by("1") is True

    def test_can_view_by_public(self, sample_domain_capsule):
        """测试公开胶囊的查看权限"""
        sample_domain_capsule.visibility = Visibility.CAMPUS
        assert sample_domain_capsule.can_view_by("2") is True

    def test_can_view_by_private(self, sample_domain_capsule):
        """测试私有胶囊的查看权限"""
        sample_domain_capsule.visibility = Visibility.PRIVATE
        assert sample_domain_capsule.can_view_by("2") is False

    def test_to_api_basic(self, sample_domain_capsule):
        """测试Domain转API基础模型"""
        result = sample_domain_capsule.to_api_basic()
        
        assert isinstance(result, CapsuleBasic)
        assert result.id == "test_capsule_123"
        assert result.title == "测试胶囊"
        assert result.visibility == "campus"
        assert result.status == "locked"

    def test_to_api_detail(self, sample_domain_capsule):
        """测试Domain转API详情模型"""
        mock_user = Mock()
        mock_user.nickname = "测试用户"
        mock_user.avatar_url = None
        
        result = sample_domain_capsule.to_api_detail(mock_user)
        
        assert isinstance(result, CapsuleDetail)
        assert result.id == "test_capsule_123"
        assert result.title == "测试胶囊"
        assert result.content == "测试内容"
        assert result.creator is not None
        assert result.creator.user_id == 1


class TestCapsuleService:
    """Service层测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_repository(self):
        """模拟Repository"""
        return Mock(spec=CapsuleRepository)

    @pytest.fixture
    def service(self, mock_db, mock_repository):
        """Service实例"""
        service = CapsuleService(mock_db)
        service.repository = mock_repository
        return service

    def test_create_capsule(self, service, mock_repository):
        """测试创建胶囊"""
        request = CapsuleCreateRequest(
            title="新胶囊",
            content="新内容",
            visibility="public"
        )
        
        mock_domain = CapsuleDomain(
            capsule_id="new_capsule",
            owner_id="1",
            title="新胶囊",
            content="新内容"
        )
        
        mock_repository.save.return_value = mock_domain
        
        result = service.create_capsule(request, user_id=1)
        
        assert isinstance(result, CapsuleCreateResponse)
        assert result.capsule_id == "new_capsule"
        mock_repository.save.assert_called_once()

    def test_get_capsule_detail_success(self, service, mock_repository):
        """测试获取胶囊详情成功"""
        mock_domain = CapsuleDomain(
            capsule_id="test_capsule",
            owner_id="1",
            title="测试胶囊"
        )
        
        mock_user = Mock()
        mock_user.nickname = "测试用户"
        
        mock_repository.find_by_id.return_value = mock_domain
        
        with patch.object(mock_domain, 'can_view_by', return_value=True):
            with patch.object(mock_domain, 'to_api_detail', return_value=Mock()):
                result = service.get_capsule_detail("test_capsule", 1, mock_user)
        
        assert result is not None
        mock_repository.find_by_id.assert_called_once_with("test_capsule")

    def test_get_capsule_detail_not_found(self, service, mock_repository):
        """测试获取胶囊详情不存在"""
        mock_repository.find_by_id.return_value = None
        
        result = service.get_capsule_detail("nonexistent", 1, Mock())
        
        assert result is None

    def test_update_capsule_success(self, service, mock_repository):
        """测试成功更新胶囊"""
        mock_domain = CapsuleDomain(
            capsule_id="test_capsule",
            owner_id="1",
            title="旧标题"
        )
        
        mock_repository.find_by_id.return_value = mock_domain
        mock_repository.save.return_value = mock_domain
        
        request = CapsuleUpdateRequest(title="新标题", content="新内容")
        result = service.update_capsule("test_capsule", request, user_id=1)
        
        assert result is True
        assert mock_domain.title == "新标题"
        mock_repository.save.assert_called_once()

    def test_delete_capsule_success(self, service, mock_repository):
         """测试成功删除胶囊"""
         mock_domain = CapsuleDomain(
            capsule_id="test_capsule",
            owner_id="1",
            title="测试胶囊"  # 添加缺失的必需参数
        )
    
         mock_repository.find_by_id.return_value = mock_domain
         mock_repository.delete_by_id.return_value = True
    
         result = service.delete_capsule("test_capsule", user_id=1)
    
         assert result is True
         mock_repository.delete_by_id.assert_called_once_with("test_capsule")

    def test_get_user_capsules(self, service, mock_repository):
        """测试获取用户胶囊列表"""
        mock_repository.find_by_user_id.return_value = {
            'capsules': [],
            'total': 0,
            'page': 1,
            'limit': 20,
            'total_pages': 0
        }
        
        result = service.get_user_capsules(user_id=1, page=1, limit=20)
        
        assert result['total'] == 0
        assert len(result['capsules']) == 0
        mock_repository.find_by_user_id.assert_called_once_with(1, 1, 20)

    def test_save_draft(self, service, mock_repository):
        """测试保存草稿"""
        request = CapsuleDraftRequest(
            title="草稿标题",
            content="草稿内容"
        )
        
        mock_domain = CapsuleDomain(
            capsule_id="draft_123",
            owner_id="1",
            title="草稿标题"
        )
        
        mock_repository.save.return_value = mock_domain
        
        result = service.save_draft(request, user_id=1)
        
        assert isinstance(result, CapsuleDraftResponse)
        assert result.draft_id == "draft_123"
        mock_repository.save.assert_called_once()

    def test_get_capsules_by_timeline(self, service, mock_repository):
        """测试按时间轴获取胶囊"""
        mock_repository.find_by_user_timeline.return_value = []
        
        result = service.get_capsules_by_timeline(user_id=1)
        
        assert isinstance(result, dict)
        mock_repository.find_by_user_timeline.assert_called_once_with(1)


class TestCapsuleManagerAlias:
    """测试CapsuleManager别名"""

    def test_manager_alias_exists(self):
        """测试CapsuleManager别名是否存在"""
        assert CapsuleManager == CapsuleService

    def test_can_create_manager(self):
        """测试可以创建Manager实例"""
        mock_db = Mock(spec=Session)
        manager = CapsuleManager(mock_db)
        assert isinstance(manager, CapsuleService)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])