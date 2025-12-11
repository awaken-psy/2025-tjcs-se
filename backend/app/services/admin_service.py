"""
Admin Service - 管理员服务层
"""
from datetime import datetime
from typing import Optional, Dict, Any

from app.database.repositories.admin_repository import AdminRepository
from app.model.admin import (
    PendingCapsulesQuery,
    PendingCapsulesResponse,
    ReportsQuery,
    ReportsResponse,
    ReviewCapsuleRequest,
    Action
)
from app.core.exceptions import RecordNotFoundException, ValidationException


class AdminService:
    """管理员服务"""

    def __init__(self, db=None):
        """初始化管理员服务"""
        self.repository = AdminRepository(db)

    def get_pending_capsules(self, query: PendingCapsulesQuery) -> PendingCapsulesResponse:
        """获取待审核胶囊"""
        try:
            # 设置默认值
            page = query.page or 1
            page_size = query.page_size or 20
            sort = query.sort.value if hasattr(query.sort, 'value') else (query.sort if query.sort else "latest")

            result = self.repository.get_pending_capsules(
                page=page,
                page_size=page_size,
                sort=sort
            )

            return PendingCapsulesResponse(
                capsules=result["capsules"]
            )

        except Exception as e:
            raise Exception(f"获取待审核胶囊失败: {str(e)}")

    def get_reports(self, query: ReportsQuery) -> ReportsResponse:
        """获取举报列表"""
        try:
            # 设置默认值
            page = query.page or 1
            page_size = query.page_size or 20
            status = query.status.value if hasattr(query.status, 'value') else query.status
            target_type = query.target_type.value if hasattr(query.target_type, 'value') else query.target_type
            reason = query.reason.value if hasattr(query.reason, 'value') else query.reason

            result = self.repository.get_reports(
                status=status,
                page=page,
                page_size=page_size,
                target_type=target_type,
                reason=reason
            )

            return ReportsResponse(
                reports=result["reports"]
            )

        except Exception as e:
            raise Exception(f"获取举报列表失败: {str(e)}")

    def review_capsule(self, capsule_id: str, request: ReviewCapsuleRequest) -> bool:
        """审核胶囊"""
        try:
            # 验证输入参数
            if not capsule_id:
                raise ValidationException("胶囊ID不能为空")

            if request.action == Action.REJECT and not request.reason:
                raise ValidationException("拒绝时必须提供拒绝原因")

            # 执行审核
            result = self.repository.review_capsule(
                capsule_id=capsule_id,
                action=request.action.value if hasattr(request.action, 'value') else request.action,
                reason=request.reason
            )

            return result

        except RecordNotFoundException:
            raise
        except ValidationException:
            raise
        except Exception as e:
            raise Exception(f"审核胶囊失败: {str(e)}")

    def resolve_report(self, report_id: str) -> bool:
        """处理举报"""
        try:
            # 验证输入参数
            if not report_id:
                raise ValidationException("举报ID不能为空")

            # 执行处理
            result = self.repository.resolve_report(report_id)

            return result

        except RecordNotFoundException:
            raise
        except ValidationException:
            raise
        except Exception as e:
            raise Exception(f"处理举报失败: {str(e)}")