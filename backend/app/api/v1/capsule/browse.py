"""
胶囊浏览相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from auth.dependencies import login_required
from domain.user import RegisteredUser
from model.capsule_model import BaseResponse, ErrorResponse, Location

from ..routes import browse_router as router


@router.get(
    "/nearby",
    response_model=BaseResponse,
    summary="获取附近胶囊",
    description="根据用户位置获取附近的胶囊列表"
)
async def get_nearby_capsules(
    latitude: float = Query(..., description="纬度"),
    longitude: float = Query(..., description="经度"),
    radius_meters: int = Query(1000, ge=10, le=10000, description="搜索半径（米）"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user: RegisteredUser = Depends(login_required)
):
    """获取附近胶囊"""
    try:
        # TODO: 实现实际的查询逻辑
        # 这里先返回模拟数据

        return BaseResponse(
            success=True,
            message="获取附近胶囊成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取附近胶囊时发生错误: {str(e)}"
        )


@router.get(
    "/popular",
    response_model=BaseResponse,
    summary="获取热门胶囊",
    description="获取热门的胶囊列表"
)
async def get_popular_capsules(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    time_range: str = Query("week", regex="day|week|month", description="时间范围"),
    user: RegisteredUser = Depends(login_required)
):
    """获取热门胶囊"""
    try:
        # TODO: 实现实际的查询逻辑
        # 这里先返回模拟数据

        return BaseResponse(
            success=True,
            message="获取热门胶囊成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取热门胶囊时发生错误: {str(e)}"
        )


@router.get(
    "/search",
    response_model=BaseResponse,
    summary="搜索胶囊",
    description="根据关键词搜索胶囊"
)
async def search_capsules(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user: RegisteredUser = Depends(login_required)
):
    """搜索胶囊"""
    try:
        # TODO: 实现实际的搜索逻辑
        # 这里先返回模拟数据

        return BaseResponse(
            success=True,
            message="搜索胶囊成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"搜索胶囊时发生错误: {str(e)}"
        )