"""
Admin Service 测试
"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.admin_service import AdminService
from app.model.admin import (
    PendingCapsulesQuery,
    PendingCapsulesResponse,
    ReportsQuery,
    ReportsResponse,
    ReviewCapsuleRequest,
    Action,
    Sort,
    Status,
    TargetType,
    Reason
)
from app.core.exceptions import RecordNotFoundException, ValidationException


class TestAdminService:
    """Admin Service 测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # Mock database session
        self.mock_db = Mock(spec=Session)
        self.admin_service = AdminService(self.mock_db)

    def test_init(self):
        """测试 AdminService 初始化"""
        service = AdminService()
        assert service.repository is not None

        service_with_db = AdminService(self.mock_db)
        assert service_with_db.repository is not None

    @patch('app.services.admin_service.AdminRepository')
    def test_get_pending_capsules_success(self, mock_repository_class):
        """测试获取待审核胶囊成功"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository

        mock_data = {
            "capsules": [
                {
                    "id": "1",
                    "title": "测试胶囊",
                    "creator_nickname": "测试用户",
                    "created_at": datetime.now(),
                    "report_count": 2,
                    "content_preview": "这是一个测试胶囊..."
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20
        }
        mock_repository.get_pending_capsules.return_value = mock_data

        query = PendingCapsulesQuery(page=1, page_size=20, sort=Sort.LATEST)
        service = AdminService(self.mock_db)

        # Act
        result = service.get_pending_capsules(query)

        # Assert
        assert isinstance(result, PendingCapsulesResponse)
        assert len(result.capsules) == 1
        assert result.capsules[0].id == "1"
        assert result.capsules[0].title == "测试胶囊"
        assert result.capsules[0].creator_nickname == "测试用户"
        assert result.capsules[0].report_count == 2

    @patch('app.services.admin_service.AdminRepository')
    def test_get_pending_capsules_with_defaults(self, mock_repository_class):
        """测试获取待审核胶囊使用默认值"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository

        mock_repository.get_pending_capsules.return_value = {
            "capsules": [],
            "total": 0,
            "page": 1,
            "page_size": 20
        }

        query = PendingCapsulesQuery()
        service = AdminService(self.mock_db)

        # Act
        result = service.get_pending_capsules(query)

        # Assert
        mock_repository.get_pending_capsules.assert_called_once_with(
            page=1,
            page_size=20,
            sort="latest"
        )
        assert isinstance(result, PendingCapsulesResponse)

    @patch('app.services.admin_service.AdminRepository')
    def test_get_reports_success(self, mock_repository_class):
        """测试获取举报列表成功"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository

        mock_repository.get_reports.return_value = {
            "reports": [],
            "total": 0,
            "page": 1,
            "page_size": 20
        }

        query = ReportsQuery()
        service = AdminService(self.mock_db)

        # Act
        result = service.get_reports(query)

        # Assert
        assert isinstance(result, ReportsResponse)
        mock_repository.get_reports.assert_called_once_with(
            status=None,
            page=1,
            page_size=20,
            target_type=None,
            reason=None
        )

    @patch('app.services.admin_service.AdminRepository')
    def test_get_reports_with_filters(self, mock_repository_class):
        """测试获取举报列表带筛选条件"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository

        mock_repository.get_reports.return_value = {
            "reports": [],
            "total": 0,
            "page": 2,
            "page_size": 10
        }

        query = ReportsQuery(
            page=2,
            page_size=10,
            status=Status.PENDING,
            target_type=TargetType.CAPSULE,
            reason=Reason.VIOLATION
        )
        service = AdminService(self.mock_db)

        # Act
        result = service.get_reports(query)

        # Assert
        mock_repository.get_reports.assert_called_once_with(
            status="pending",
            page=2,
            page_size=10,
            target_type="capsule",
            reason="违规内容"
        )
        assert isinstance(result, ReportsResponse)

    @patch('app.services.admin_service.AdminRepository')
    def test_review_capsule_approve_success(self, mock_repository_class):
        """测试审核胶囊通过成功"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository
        mock_repository.review_capsule.return_value = True

        request = ReviewCapsuleRequest(action=Action.APPROVE)
        service = AdminService(self.mock_db)

        # Act
        result = service.review_capsule("123", request)

        # Assert
        assert result is True
        mock_repository.review_capsule.assert_called_once_with(
            capsule_id="123",
            action="approve",
            reason=None
        )

    @patch('app.services.admin_service.AdminRepository')
    def test_review_capsule_reject_with_reason(self, mock_repository_class):
        """测试审核胶囊拒绝并填写原因"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository
        mock_repository.review_capsule.return_value = True

        request = ReviewCapsuleRequest(
            action=Action.REJECT,
            reason="内容违规"
        )
        service = AdminService(self.mock_db)

        # Act
        result = service.review_capsule("456", request)

        # Assert
        assert result is True
        mock_repository.review_capsule.assert_called_once_with(
            capsule_id="456",
            action="reject",
            reason="内容违规"
        )

    @patch('app.services.admin_service.AdminRepository')
    def test_review_capsule_reject_without_reason(self, mock_repository_class):
        """测试审核胶囊拒绝但未填写原因应该失败"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository

        request = ReviewCapsuleRequest(action=Action.REJECT)
        service = AdminService(self.mock_db)

        # Act & Assert
        with pytest.raises(ValidationException, match="拒绝时必须提供拒绝原因"):
            service.review_capsule("789", request)

    def test_review_capsule_empty_capsule_id(self):
        """测试审核胶囊时胶囊ID为空"""
        # Arrange
        request = ReviewCapsuleRequest(action=Action.APPROVE)
        service = AdminService(self.mock_db)

        # Act & Assert
        with pytest.raises(ValidationException, match="胶囊ID不能为空"):
            service.review_capsule("", request)

    def test_review_capsule_none_capsule_id(self):
        """测试审核胶囊时胶囊ID为None"""
        # Arrange
        request = ReviewCapsuleRequest(action=Action.APPROVE)
        service = AdminService(self.mock_db)

        # Act & Assert
        with pytest.raises(ValidationException, match="胶囊ID不能为空"):
            service.review_capsule(None, request)

    @patch('app.services.admin_service.AdminRepository')
    def test_review_capsule_not_found(self, mock_repository_class):
        """测试审核胶囊时胶囊不存在"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository
        mock_repository.review_capsule.side_effect = RecordNotFoundException("胶囊不存在")

        request = ReviewCapsuleRequest(action=Action.APPROVE)
        service = AdminService(self.mock_db)

        # Act & Assert
        with pytest.raises(RecordNotFoundException, match="胶囊不存在"):
            service.review_capsule("999", request)

    @patch('app.services.admin_service.AdminRepository')
    def test_resolve_report_success(self, mock_repository_class):
        """测试处理举报成功"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository
        mock_repository.resolve_report.return_value = True

        service = AdminService(self.mock_db)

        # Act
        result = service.resolve_report("report123")

        # Assert
        assert result is True
        mock_repository.resolve_report.assert_called_once_with("report123")

    def test_resolve_report_empty_report_id(self):
        """测试处理举报时举报ID为空"""
        # Arrange
        service = AdminService(self.mock_db)

        # Act & Assert
        with pytest.raises(ValidationException, match="举报ID不能为空"):
            service.resolve_report("")

    def test_resolve_report_none_report_id(self):
        """测试处理举报时举报ID为None"""
        # Arrange
        service = AdminService(self.mock_db)

        # Act & Assert
        with pytest.raises(ValidationException, match="举报ID不能为空"):
            service.resolve_report(None)

    @patch('app.services.admin_service.AdminRepository')
    def test_get_pending_capsules_repository_exception(self, mock_repository_class):
        """测试获取待审核胶囊时Repository抛出异常"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository
        mock_repository.get_pending_capsules.side_effect = Exception("数据库连接错误")

        query = PendingCapsulesQuery()
        service = AdminService(self.mock_db)

        # Act & Assert
        with pytest.raises(Exception, match="获取待审核胶囊失败"):
            service.get_pending_capsules(query)

    @patch('app.services.admin_service.AdminRepository')
    def test_get_reports_repository_exception(self, mock_repository_class):
        """测试获取举报列表时Repository抛出异常"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository
        mock_repository.get_reports.side_effect = Exception("查询超时")

        query = ReportsQuery()
        service = AdminService(self.mock_db)

        # Act & Assert
        with pytest.raises(Exception, match="获取举报列表失败"):
            service.get_reports(query)

    @patch('app.services.admin_service.AdminRepository')
    def test_resolve_report_repository_exception(self, mock_repository_class):
        """测试处理举报时Repository抛出异常"""
        # Arrange
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository
        mock_repository.resolve_report.side_effect = Exception("更新失败")

        service = AdminService(self.mock_db)

        # Act & Assert
        with pytest.raises(Exception, match="处理举报失败"):
            service.resolve_report("report123")