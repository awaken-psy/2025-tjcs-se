from typing import Optional, List, Dict
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.model.event import (
    EventCreateRequest, EventUpdateRequest, EventRegistrationRequest,
    EventCreateResponse, EventUpdateResponse, EventDeleteResponse,
    EventRegistrationResponse, EventCancelResponse, EventResponse,
    EventListResponse
)
from app.model.base import BaseResponse, Pagination
from app.auth.dependencies import login_required
from app.domain.user import AuthorizedUser
from app.services.event_service import EventService
from app.logger import get_logger, api_logging

# 初始化 FastAPI 路由和日志
router = APIRouter(prefix='/events', tags=['Events'])
logger = get_logger(f"router<{__name__}>")


## 📝 活动创建与管理

@router.post(
    "/",
    response_model=BaseResponse[EventCreateResponse],
    summary="创建活动",
    description="创建新的活动"
)
@api_logging(logger)
async def create_event(
    request: EventCreateRequest,
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db),
):
    """创建活动"""
    try:
        service = EventService(db)
        response = service.create_event(request, user.user_id)

        return BaseResponse[EventCreateResponse].success(
            code=200,
            message="活动创建成功",
            data=response
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建活动失败: {str(e)}")


@router.put(
    "/{event_id}",
    response_model=BaseResponse[EventUpdateResponse],
    summary="更新活动",
    description="更新活动信息，仅限创建者操作"
)
@api_logging(logger)
async def update_event(
    event_id: str = Path(..., description="活动ID"),
    request: EventUpdateRequest = ...,
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db),
):
    """更新活动"""
    try:
        service = EventService(db)
        response = service.update_event(event_id, request, user.user_id)

        return BaseResponse[EventUpdateResponse].success(
            code=200,
            message="活动更新成功",
            data=response
        )

    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "权限" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=f"更新活动失败: {str(e)}")


@router.delete(
    "/{event_id}",
    response_model=BaseResponse[EventDeleteResponse],
    summary="删除活动",
    description="删除活动，仅限创建者操作"
)
@api_logging(logger)
async def delete_event(
    event_id: str = Path(..., description="活动ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db),
):
    """删除活动"""
    try:
        service = EventService(db)
        response = service.delete_event(event_id, user.user_id)

        return BaseResponse[EventDeleteResponse].success(
            code=200,
            message="活动删除成功",
            data=response
        )

    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "权限" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=f"删除活动失败: {str(e)}")


## 📃 活动查询

@router.get(
    "/",
    response_model=BaseResponse[EventListResponse],
    summary="获取活动列表",
    description="获取所有活动列表，分页显示"
)
@api_logging(logger)
async def get_events_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
):
    """获取活动列表"""
    try:
        service = EventService(db)
        result = service.get_events_list(page, size)

        return BaseResponse[EventListResponse].success(
            code=200,
            message="获取成功",
            data=EventListResponse(
                list=result['list'],
                total=result['total'],
                page=result['page'],
                page_size=result['page_size']
            )
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取活动列表失败: {str(e)}")


@router.get(
    "/my",
    response_model=BaseResponse[EventListResponse],
    summary="获取我创建的活动",
    description="获取当前用户创建的活动列表"
)
@api_logging(logger)
async def get_my_events(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db),
):
    """获取我创建的活动"""
    try:
        service = EventService(db)
        result = service.get_my_events(user.user_id, page, size)

        return BaseResponse[EventListResponse].success(
            code=200,
            message="获取成功",
            data=EventListResponse(
                list=result['list'],
                total=result['total'],
                page=result['page'],
                page_size=result['page_size']
            )
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取我的活动失败: {str(e)}")


@router.get(
    "/my-registered",
    response_model=BaseResponse[EventListResponse],
    summary="获取我报名的活动",
    description="获取当前用户报名的活动列表"
)
@api_logging(logger)
async def get_my_registrations(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db),
):
    """获取我报名的活动"""
    try:
        service = EventService(db)
        result = service.get_my_registrations(user.user_id, page, size)

        return BaseResponse[EventListResponse].success(
            code=200,
            message="获取成功",
            data=EventListResponse(
                list=result['list'],
                total=result['total'],
                page=result['page'],
                page_size=result['page_size']
            )
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取我的报名失败: {str(e)}")


@router.get(
    "/{event_id}",
    response_model=BaseResponse[EventResponse],
    summary="获取活动详情",
    description="获取单个活动的详细信息"
)
@api_logging(logger)
async def get_event_detail(
    event_id: str = Path(..., description="活动ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db),
):
    """获取活动详情"""
    try:
        service = EventService(db)
        event_detail = service.get_event_detail(event_id, user.user_id)

        if not event_detail:
            raise HTTPException(status_code=404, detail="活动不存在")

        return BaseResponse[EventResponse].success(
            code=200,
            message="获取成功",
            data=event_detail
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取活动详情失败: {str(e)}")


## 🎯 活动报名相关

@router.post(
    "/{event_id}/register",
    response_model=BaseResponse[EventRegistrationResponse],
    summary="报名活动",
    description="报名参加活动"
)
@api_logging(logger)
async def register_event(
    event_id: str = Path(..., description="活动ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db),
):
    """报名活动"""
    try:
        service = EventService(db)
        response = service.register_event(event_id, user.user_id)

        return BaseResponse[EventRegistrationResponse].success(
            code=200,
            message="报名成功",
            data=response
        )

    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "已经报名" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=f"报名活动失败: {str(e)}")


@router.post(
    "/{event_id}/cancel",
    response_model=BaseResponse[EventCancelResponse],
    summary="取消报名",
    description="取消活动报名"
)
@api_logging(logger)
async def cancel_registration(
    event_id: str = Path(..., description="活动ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db),
):
    """取消报名"""
    try:
        service = EventService(db)
        response = service.cancel_registration(event_id, user.user_id)

        return BaseResponse[EventCancelResponse].success(
            code=200,
            message="取消报名成功",
            data=response
        )

    except Exception as e:
        if "未找到" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=f"取消报名失败: {str(e)}")