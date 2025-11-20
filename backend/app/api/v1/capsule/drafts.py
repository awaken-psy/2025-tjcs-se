"""
胶囊草稿相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from auth.dependencies import login_required
from domain.user import RegisteredUser
from model.capsule_model import BaseResponse, ErrorResponse, DraftSaveRequest, DraftSaveResponse

from ..routes import drafts_router as router


@router.get(
    "/",
    response_model=BaseResponse,
    summary="获取草稿列表",
    description="获取用户的胶囊草稿列表"
)
async def get_drafts(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user: RegisteredUser = Depends(login_required)
):
    """获取草稿列表"""
    try:
        # TODO: 实现实际的查询逻辑
        # 这里先返回模拟数据

        return BaseResponse(
            success=True,
            message="获取草稿列表成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取草稿列表时发生错误: {str(e)}"
        )


@router.post(
    "/save",
    response_model=DraftSaveResponse,
    summary="保存草稿",
    description="保存胶囊草稿"
)
async def save_draft(
    request: DraftSaveRequest,
    user: RegisteredUser = Depends(login_required)
):
    """保存草稿"""
    try:
        # TODO: 实现实际的保存逻辑
        # 这里先返回模拟数据

        return DraftSaveResponse(
            success=True,
            message="草稿保存成功",
            draft_id="draft_123",
            saved_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"保存草稿时发生错误: {str(e)}"
        )


@router.delete(
    "/{draft_id}",
    response_model=BaseResponse,
    summary="删除草稿",
    description="删除指定的草稿"
)
async def delete_draft(
    draft_id: str = Path(..., description="草稿ID"),
    user: RegisteredUser = Depends(login_required)
):
    """删除草稿"""
    try:
        # TODO: 实现实际的删除逻辑
        # 这里先返回模拟数据

        return BaseResponse(
            success=True,
            message="草稿删除成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除草稿时发生错误: {str(e)}"
        )