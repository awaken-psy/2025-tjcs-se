"""
时光胶囊服务层和API接口综合测试
适配项目实际配置
"""
import pytest
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session, Query
from fastapi.testclient import TestClient
from fastapi import HTTPException

# 导入被测试的模块
from app.services.capsule import CapsuleManager
from app.api.v1.capsules import router, _map_to_basic, _map_to_detail
from app.database.orm.capsule import Capsule
from app.model.capsule import (
    CapsuleCreateRequest, CapsuleUpdateRequest, CapsuleDraftRequest,
    Location, UnlockConditions, CapsuleBasic, CapsuleDetail,
    CapsuleCreateResponse, CapsuleUpdateResponse, CapsuleDraftResponse,
    MultiModeBrowseResponse, CapsuleListResponse, Creator, CapsuleStats
)
from app.domain.user import AuthorizedUser
from app.model.base import Pagination
from app.main import app


class TestCapsuleServiceLayer:
    """胶囊服务层测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def capsule_manager(self, mock_db):
        """胶囊管理器实例"""
        return CapsuleManager(mock_db)

    @pytest.fixture
    def sample_capsule(self):
        """示例胶囊对象"""
        capsule = Mock(spec=Capsule)
        capsule.id = "capsule_test_123"
        capsule.title = "测试胶囊标题"
        capsule.text_content = "这是测试胶囊内容"
        capsule.visibility = "public"
        capsule.status = "published"
        capsule.created_at = datetime.now(timezone.utc)
        capsule.updated_at = datetime.now(timezone.utc)
        capsule.user_id = 1
        capsule.latitude = 31.2304
        capsule.longitude = 121.4737
        capsule.address = "上海市"
        capsule.tag_json = json.dumps(["测试", "胶囊"])
        return capsule

    def test_create_capsule_from_request(self, capsule_manager, mock_db):
        """测试从请求创建胶囊"""
        request_data = CapsuleCreateRequest(
            title="测试胶囊标题",
            content="这是测试胶囊内容",
            visibility="public",
            tags=["测试", "胶囊"],
            location=Location(
                latitude=31.2304,
                longitude=121.4737,
                address="上海市"
            ),
            unlock_conditions=UnlockConditions(
                type="time",
                value="2024-12-31T23:59:59Z",
                radius=100
            ),
            media_files=["file1.jpg", "file2.jpg"]
        )

        # 模拟数据库操作
        mock_capsule = Mock(spec=Capsule)
        mock_capsule.id = "test_capsule_id"
        mock_db.add.return_value = None
        mock_db.flush.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        with patch('app.services.capsule.Capsule', return_value=mock_capsule):
            with patch('app.services.capsule.UnlockCondition'):
                result = capsule_manager.create_capsule_from_request(request_data, user_id=1)

        # 验证数据库操作被调用
        mock_db.add.assert_called()
        mock_db.flush.assert_called()
        mock_db.commit.assert_called()
        mock_db.refresh.assert_called()
        assert result is not None

    def test_get_capsule_detail_success(self, capsule_manager, sample_capsule):
        """测试成功获取胶囊详情"""
        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_capsule
        capsule_manager.db.query.return_value = mock_query

        result = capsule_manager.get_capsule_detail("capsule_test_123", user_id=1)

        assert result == sample_capsule

    def test_get_capsule_detail_not_found(self, capsule_manager):
        """测试胶囊不存在的情况"""
        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        capsule_manager.db.query.return_value = mock_query

        result = capsule_manager.get_capsule_detail("nonexistent", user_id=1)

        assert result is None

    def test_get_capsule_detail_no_permission(self, capsule_manager, sample_capsule):
        """测试无权限访问胶囊的情况"""
        sample_capsule.visibility = "private"
        sample_capsule.user_id = 2  # 不同的用户

        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_capsule
        capsule_manager.db.query.return_value = mock_query

        result = capsule_manager.get_capsule_detail("capsule_test_123", user_id=1)

        assert result is None

    def test_get_user_capsules(self, capsule_manager, sample_capsule):
        """测试获取用户胶囊列表"""
        # 模拟分页查询
        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 1

        # 模拟分页结果
        mock_page_query = Mock(spec=Query)
        mock_page_query.offset.return_value = mock_page_query
        mock_page_query.limit.return_value = mock_page_query
        mock_page_query.all.return_value = [sample_capsule]

        # 设置链式调用
        mock_query.offset.return_value.limit.return_value = mock_page_query
        capsule_manager.db.query.return_value = mock_query

        result = capsule_manager.get_user_capsules(user_id=1, page=1, limit=20)

        assert result['capsules'] == [sample_capsule]
        assert result['total'] == 1
        assert result['page'] == 1
        assert result['limit'] == 20
        assert result['total_pages'] == 1

    def test_update_capsule_from_request_success(self, capsule_manager, sample_capsule):
        """测试成功更新胶囊"""
        update_request = CapsuleUpdateRequest(
            title="更新后的标题",
            content="更新后的内容",
            visibility="private"
        )

        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_capsule
        capsule_manager.db.query.return_value = mock_query
        capsule_manager.db.commit.return_value = None

        result = capsule_manager.update_capsule_from_request("capsule_test_123", update_request, user_id=1)

        assert result is True
        assert sample_capsule.title == "更新后的标题"
        assert sample_capsule.text_content == "更新后的内容"
        assert sample_capsule.visibility == "private"
        capsule_manager.db.commit.assert_called_once()

    def test_delete_capsule_success(self, capsule_manager, sample_capsule):
        """测试成功删除胶囊"""
        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_capsule
        capsule_manager.db.query.return_value = mock_query
        capsule_manager.db.delete.return_value = None
        capsule_manager.db.commit.return_value = None

        result = capsule_manager.delete_capsule("capsule_test_123", user_id=1)

        assert result is True
        capsule_manager.db.delete.assert_called_once_with(sample_capsule)
        capsule_manager.db.commit.assert_called_once()

    def test_save_draft_from_request(self, capsule_manager):
        """测试保存草稿"""
        draft_request = CapsuleDraftRequest(
            title="草稿标题",
            content="草稿内容",
            visibility="private"
        )

        mock_capsule = Mock(spec=Capsule)
        mock_capsule.id = "draft_id"
        mock_capsule.created_at = datetime.now(timezone.utc)

        with patch('app.services.capsule.Capsule', return_value=mock_capsule):
            capsule_manager.db.add.return_value = None
            capsule_manager.db.commit.return_value = None
            capsule_manager.db.refresh.return_value = None

            result = capsule_manager.save_draft_from_request(draft_request, user_id=1)

        assert result == mock_capsule
        capsule_manager.db.add.assert_called_once()
        capsule_manager.db.commit.assert_called_once()

    def test_get_capsules_with_location(self, capsule_manager, sample_capsule):
        """测试获取带位置信息的胶囊"""
        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_capsule]
        capsule_manager.db.query.return_value = mock_query

        result = capsule_manager.get_capsules_with_location(user_id=1, page=1, limit=20)

        assert result == [sample_capsule]
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(20)

    def test_get_capsules_by_timeline(self, capsule_manager, sample_capsule):
        """测试按时间轴获取胶囊"""
        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_capsule]
        capsule_manager.db.query.return_value = mock_query

        result = capsule_manager.get_capsules_by_timeline(user_id=1)

        month_key = sample_capsule.created_at.strftime("%Y年%m月")
        assert month_key in result
        assert result[month_key] == [sample_capsule]

    def test_get_capsules_by_tags(self, capsule_manager, sample_capsule):
        """测试按标签获取胶囊"""
        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_capsule]
        capsule_manager.db.query.return_value = mock_query

        result = capsule_manager.get_capsules_by_tags(user_id=1, page=1, limit=20)

        assert result == [sample_capsule]
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(20)


class TestCapsuleAPIEndpoints:
    """胶囊API端点测试"""

    @pytest.fixture
    def client(self):
        """测试客户端"""
        return TestClient(app)

    def test_map_to_basic(self):
        """测试ORM对象到CapsuleBasic的映射"""
        mock_capsule = Mock(spec=Capsule)
        mock_capsule.id = "test_id"
        mock_capsule.title = "测试胶囊"
        mock_capsule.visibility = "public"
        mock_capsule.status = "published"
        mock_capsule.created_at = datetime.now(timezone.utc)
        mock_capsule.text_content = "测试内容"

        result = _map_to_basic(mock_capsule)

        assert isinstance(result, CapsuleBasic)
        assert result.id == "test_id"
        assert result.title == "测试胶囊"
        assert result.visibility == "public"
        assert result.status == "published"
        assert result.content_preview == "测试内容"

    def test_map_to_detail(self):
        """测试ORM对象到CapsuleDetail的映射"""
        mock_user = Mock(spec=AuthorizedUser)
        mock_user.user_id = 1
        mock_user.nickname = "测试用户"

        mock_capsule = Mock(spec=Capsule)
        mock_capsule.id = "test_id"
        mock_capsule.title = "测试胶囊"
        mock_capsule.text_content = "测试内容"
        mock_capsule.visibility = "public"
        mock_capsule.status = "published"
        mock_capsule.created_at = datetime.now(timezone.utc)
        mock_capsule.updated_at = datetime.now(timezone.utc)
        mock_capsule.latitude = 31.2304
        mock_capsule.longitude = 121.4737
        mock_capsule.address = "上海市"
        mock_capsule.tag_json = json.dumps(["测试", "胶囊"])
        mock_capsule.user_id = 1

        result = _map_to_detail(mock_capsule, mock_user)

        assert isinstance(result, CapsuleDetail)
        assert result.id == "test_id"
        assert result.title == "测试胶囊"
        assert result.content == "测试内容"
        assert result.visibility == "public"
        assert result.status == "published"
        assert result.location is not None
        assert result.location.latitude == 31.2304
        assert result.location.longitude == 121.4737
        assert result.location.address == "上海市"
        assert result.tags == ["测试", "胶囊"]
        assert result.creator is not None
        assert result.creator.user_id == 1

    def test_capsule_routes_registered(self):
        """测试胶囊路由是否正确注册"""
        # 检查路由是否在应用中注册
        routes = [route.path for route in app.routes]
        capsule_routes = [route for route in routes if "capsule" in route.lower()]

        # 应该有胶囊相关的路由
        assert len(capsule_routes) > 0

    def test_create_capsule_api_basic(self):
        """测试创建胶囊API基础功能"""
        # 使用TestClient测试基础路由
        with TestClient(app) as client:
            # 测试路由是否存在（不验证具体业务逻辑）
            response = client.post("/api/v1/capsules/")
            # 应该返回401（未认证）而不是404（路由不存在）
            assert response.status_code != 404

    def test_get_capsule_detail_api_basic(self):
        """测试获取胶囊详情API基础功能"""
        with TestClient(app) as client:
            response = client.get("/api/v1/capsules/test_id")
            # 应该返回401（未认证）而不是404（路由不存在）
            assert response.status_code != 404

    def test_get_my_capsules_api_basic(self):
        """测试获取我的胶囊列表API基础功能"""
        with TestClient(app) as client:
            response = client.get("/api/v1/capsules/my")
            # 应该返回401（未认证）而不是404（路由不存在）
            assert response.status_code != 404

    def test_update_capsule_api_basic(self):
        """测试更新胶囊API基础功能"""
        update_data = {"title": "更新后的标题"}
        with TestClient(app) as client:
            response = client.put("/api/v1/capsules/test_id", json=update_data)
            # 应该返回401（未认证）而不是404（路由不存在）
            assert response.status_code != 404

    def test_save_draft_api_basic(self):
        """测试保存草稿API基础功能"""
        draft_data = {"title": "草稿标题", "content": "草稿内容"}
        with TestClient(app) as client:
            response = client.post("/api/v1/capsules/draft", json=draft_data)
            # 应该返回401（未认证）而不是404（路由不存在）
            assert response.status_code != 404

    def test_browse_capsules_api_basic(self):
        """测试多模式浏览胶囊API基础功能"""
        with TestClient(app) as client:
            response = client.get("/api/v1/capsules/browse?mode=map")
            # 应该返回401（未认证）而不是404（路由不存在）
            assert response.status_code != 404

    def test_delete_capsule_api_basic(self):
        """测试删除胶囊API基础功能"""
        with TestClient(app) as client:
            response = client.delete("/api/v1/capsules/test_id")
            # 应该返回401（未认证）而不是404（路由不存在）
            assert response.status_code != 404


class TestCapsuleModelValidation:
    """胶囊数据模型验证测试"""

    def test_capsule_create_request_valid(self):
        """测试有效的胶囊创建请求"""
        request = CapsuleCreateRequest(
            title="测试胶囊",
            content="测试内容",
            visibility="public",
            tags=["测试", "胶囊"],
            location=Location(latitude=31.2304, longitude=121.4737, address="上海市"),
            unlock_conditions=UnlockConditions(type="time", value="2024-12-31T23:59:59Z"),
            media_files=["file1.jpg"]
        )

        assert request.title == "测试胶囊"
        assert request.content == "测试内容"
        assert request.visibility == "public"
        assert request.tags == ["测试", "胶囊"]
        assert request.location.latitude == 31.2304
        assert request.unlock_conditions.type == "time"
        assert request.media_files == ["file1.jpg"]

    def test_capsule_update_request_partial(self):
        """测试部分更新的胶囊请求"""
        request = CapsuleUpdateRequest(
            title="新标题"
            # content和visibility保持为None
        )

        assert request.title == "新标题"
        assert request.content is None
        assert request.visibility is None

    def test_capsule_draft_request_minimal(self):
        """测试最小化的草稿请求"""
        request = CapsuleDraftRequest()

        assert request.title is None
        assert request.content is None
        assert request.visibility is None

    def test_location_model(self):
        """测试位置模型"""
        location = Location(
            latitude=31.2304,
            longitude=121.4737,
            address="上海市"
        )

        assert location.latitude == 31.2304
        assert location.longitude == 121.4737
        assert location.address == "上海市"

    def test_unlock_conditions_time(self):
        """测试时间型解锁条件"""
        condition = UnlockConditions(
            type="time",
            value="2024-12-31T23:59:59Z"
        )

        assert condition.type == "time"
        assert condition.value == "2024-12-31T23:59:59Z"
        assert condition.radius is None

    def test_unlock_conditions_location(self):
        """测试位置型解锁条件"""
        condition = UnlockConditions(
            type="location",
            radius=100.0
        )

        assert condition.type == "location"
        assert condition.radius == 100.0
        assert condition.value is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])