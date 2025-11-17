"""
Reports API interface
"""
from fastapi import APIRouter

from app.model import (
    BaseResponse,
    ReportRequest
)

router = APIRouter(prefix='/reports', tags=['Reports'])


@router.post("/", response_model=BaseResponse[None])
async def submit_report(
    request: ReportRequest
):
    """提交举报"""
    pass