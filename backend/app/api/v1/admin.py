"""
Admin API interface
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.model import (
    BaseResponse,
    PendingCapsulesQuery,
    PendingCapsulesResponse,
    ReportsQuery,
    ReportsResponse,
    ReviewCapsuleRequest
)

router = APIRouter(prefix='/admin', tags=['Admin'])



@router.get("/capsules/pending", response_model=BaseResponse[PendingCapsulesResponse])
async def get_pending_capsules(
    query: PendingCapsulesQuery = Depends()
):
    """获取待审核胶囊"""
    pass


@router.post("/capsules/{capsule_id}/review", response_model=BaseResponse[None])
async def review_capsule(
    capsule_id: str,
    request: ReviewCapsuleRequest
):
    """审核胶囊"""
    pass


@router.get("/reports", response_model=BaseResponse[ReportsResponse])
async def get_reports(
    query: ReportsQuery = Depends()
):
    """获取举报列表"""
    pass


@router.post("/reports/{report_id}/resolve", response_model=BaseResponse[None])
async def resolve_report(
    report_id: str
):
    """处理举报"""
    pass