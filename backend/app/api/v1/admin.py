"""
Admin API interface
"""
from fastapi import APIRouter, Depends, Query, Path, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional

from app.model.base import BaseResponse
from app.model.admin import (
    PendingCapsulesQuery,
    PendingCapsulesResponse,
    ReportsQuery,
    ReportsResponse,
    ReviewCapsuleRequest
)
from app.services.admin_service import AdminService
from app.database.database import get_db
from app.core.exceptions import RecordNotFoundException, ValidationException

router = APIRouter(prefix='/admin', tags=['Admin'])


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """依赖注入 AdminService"""
    return AdminService(db)

@router.get("/capsules/pending", response_model=BaseResponse[PendingCapsulesResponse])
async def get_pending_capsules(
    query: PendingCapsulesQuery = Depends(),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    获取待审核胶囊

    - **page**: 页码，默认为1
    - **page_size**: 每页数量，默认为20
    - **sort**: 排序方式："latest"(最新), "oldest"(最旧), "most_reported"(举报最多)
    """
    try:
        result = admin_service.get_pending_capsules(query)
        return BaseResponse.success(
            message="获取待审核胶囊成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/capsules/{capsule_id}/review", response_model=BaseResponse[None])
async def review_capsule(
    capsule_id: str,
    request: ReviewCapsuleRequest,
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    审核胶囊

    - **capsule_id**: 要审核的胶囊ID
    - **action**: 审核动作："approve"(通过) 或 "reject"(拒绝)
    - **reason**: 拒绝原因（仅在action为reject时需要）
    """
    try:
        admin_service.review_capsule(capsule_id, request)
        action_text = "通过" if request.action.value == "approve" else "拒绝"
        return BaseResponse.success(
            message=f"胶囊{action_text}审核成功",
            code=200
        )
    except RecordNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports", response_model=BaseResponse[ReportsResponse])
async def get_reports(
    query: ReportsQuery = Depends(),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    获取举报列表

    - **status**: 处理状态："pending"(待处理), "resolved"(已处理)
    - **page**: 页码，默认为1
    - **page_size**: 每页数量，默认为20
    - **target_type**: 举报目标类型："capsule", "comment", "user"
    - **reason**: 举报原因："违规内容", "侵权", "不良信息", "其他"
    """
    try:
        result = admin_service.get_reports(query)
        return BaseResponse.success(
            message="获取举报列表成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/{report_id}/resolve", response_model=BaseResponse[None])
async def resolve_report(
    report_id: str,
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    处理举报

    - **report_id**: 要处理的举报ID
    """
    try:
        admin_service.resolve_report(report_id)
        return BaseResponse.success(
            message="举报处理成功",
            code=200
        )
    except RecordNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))