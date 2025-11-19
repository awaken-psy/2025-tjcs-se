"""
胶囊相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from domain.condition import Location, UnlockConditions
from domain.capsule import CapsuleStatus, Visibility
from domain.user import RegisteredUser
from auth.dependencies import login_required

from model.capsule_model import CapsuleCreateRequest, CapsuleUpdateRequest
from model.capsule_model import CapsuleCreatedResponse, CapsuleListResponse, CapsuleDetailResponse, CapsuleUpdateResponse, ErrorResponse, CapsuleDeleteResponse
from model.capsule_model import NearbyCapsulesResponse, NearbyCapsule, NearbyCapsuleLocation
from services.capsule_manager import CapsuleManager

from fastapi import APIRouter

router = APIRouter(prefix="/capsule", tags=["Capsule"])


@router.get(
    "/nearby",
    response_model=NearbyCapsulesResponse,
    summary="获取附近胶囊",
    description="获取用户附近的胶囊列表，包含距离和解锁状态信息"
)
async def get_nearby_capsules(
    latitude: float = Query(..., description="用户当前纬度"),
    longitude: float = Query(..., description="用户当前经度"),
    radius_meters: int = Query(1000, ge=10, le=10000, description="搜索半径（米）"),
    user: RegisteredUser = Depends(login_required)
):
    """获取附近胶囊"""
    try:
        # 简化测试 - 直接返回模拟数据
        print(f"Getting nearby capsules for user {user.user_id} at {latitude}, {longitude}")

        mock_nearby_capsules = [
            {
                "can_unlock": False,
                "created_at": datetime(2024, 10, 26, 10, 0, 0),
                "creator_nickname": "小明",
                "id": "caps_001",
                "is_unlocked": False,
                "location": NearbyCapsuleLocation(
                    distance=150.5,
                    latitude=39.9042,
                    longitude=116.4074
                ),
                "title": "毕业纪念",
                "visibility": "public"
            },
            {
                "can_unlock": True,
                "created_at": datetime(2024, 10, 25, 14, 30, 0),
                "creator_nickname": "张三",
                "id": "caps_002",
                "is_unlocked": False,
                "location": NearbyCapsuleLocation(
                    distance=320.8,
                    latitude=39.9052,
                    longitude=116.4084
                ),
                "title": "足球比赛回忆",
                "visibility": "friends"
            },
            {
                "can_unlock": False,
                "created_at": datetime(2024, 10, 24, 9, 15, 0),
                "creator_nickname": "李四",
                "id": "caps_003",
                "is_unlocked": True,
                "location": NearbyCapsuleLocation(
                    distance=580.2,
                    latitude=39.9032,
                    longitude=116.4064
                ),
                "title": "我们分手了",
                "visibility": "private"
            }
        ]

        return NearbyCapsulesResponse(
            code=200,
            data={
                "capsules": mock_nearby_capsules
            },
            message=f"成功获取{len(mock_nearby_capsules)}个附近胶囊"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取附近胶囊时发生错误: {str(e)}"
        )


@router.post(
    "/",
    response_model=CapsuleCreatedResponse,
    summary="创建时光胶囊",
    description="创建新的时光胶囊，支持多媒体内容和多种解锁条件"
)
async def create_capsule(request: CapsuleCreateRequest, user: RegisteredUser = Depends(login_required)):
    """创建胶囊"""
    try:
        # TODO: 实现实际的胶囊创建逻辑
        # 这里先返回模拟数据

        return CapsuleCreatedResponse(
            success=True,
            message="胶囊创建成功",
            capsule_id="caps_114514",
            title=request.title,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建胶囊时发生错误: {str(e)}"
        )


@router.get(
    "/",
    response_model=CapsuleListResponse,
    summary="获取可查看的胶囊列表",
    description="获取可查看的胶囊列表（自己创建的或已解锁的）"
)
async def get_capsules(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user: RegisteredUser = Depends(login_required)
):
    """获取可查看的胶囊列表"""
    try:
        # TODO: 实现实际的查询逻辑
        # 这里先返回模拟数据

        # 模拟胶囊数据
        mock_capsules = [
            {
                "capsule_id": "caps_1",
                "title": "毕业纪念"
            },
            {
                "capsule_id": "caps_2",
                "title": "足球比赛"
            },
            {
                "capsule_id": "caps_3",
                "title": "我们分手了"
            }
        ]

        return CapsuleListResponse(
            success=True,
            message=f"get {len(mock_capsules)} capsules.",
            capsule_list=mock_capsules,
            page=1,
            pages=1
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取胶囊列表时发生错误: {str(e)}"
        )


@router.get(
    "/{capsule_id}",
    response_model=CapsuleDetailResponse,
    summary="获取胶囊详情",
    description="获取单个胶囊的详细信息"
)
async def get_capsule_detail(
    capsule_id: str = Path(..., description="胶囊ID"),
    user: RegisteredUser = Depends(login_required)
):
    """获取胶囊详情"""
    try:
        # TODO: 实现实际的查询逻辑
        # 这里先返回模拟数据

        if capsule_id != "caps_1":
            return ErrorResponse(
                success=False,
                message="无法获取胶囊详情",
                error={
                    "reason":f"胶囊{capsule_id}不存在"
                }
            )

        # 模拟胶囊详情数据（锁定状态）
        capsule_data = {
            "capsule_id": capsule_id,
            "title": "毕业纪念",
            "status": CapsuleStatus.LOCKED,
            "visibility": Visibility.CAMPUS,
            "location": {
                "latitude": 39.9042,
                "longitude": 116.4074,
                "address": "北京大学图书馆"
            },
            "created_at": "2024-10-26T10:00:00Z",
            "estimated_unlock_time": "2025-06-30T00:00:00Z",
            "like_count": 5,
            "comment_count": 3,
            "is_liked": False,
            "can_unlock": False,
            "unlock_conditions": {
                "time_based": {
                    "unlock_time": "2025-06-30T00:00:00Z",
                    "remaining_days": 247
                },
                "location_based": {
                    "trigger_latitude": 39.9042,
                    "trigger_longitude": 116.4074,
                    "radius_meters": 100,
                    "current_distance": 150
                }
            }
        }

        return CapsuleDetailResponse(
            success=True,
            message="当前为为测试数据，字段之后可能还会变化",
            capsule_info=capsule_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取胶囊详情时发生错误: {str(e)}"
        )


@router.put(
    "/{capsule_id}",
    response_model=CapsuleUpdateResponse,
    summary="更新胶囊信息",
    description="更新胶囊信息，仅限创建者或管理员操作"
)
async def update_capsule(
    request: CapsuleUpdateRequest,
    capsule_id: str = Path(..., description="胶囊ID"),
    user: RegisteredUser = Depends(login_required)
):
    """更新胶囊信息"""
    try:
        # TODO: 实现实际的更新逻辑
        # 这里先返回模拟数据

        if capsule_id != "caps_114514":
            return ErrorResponse(
                success=False,
                message="更新失败",
                error={
                    "reason":f"胶囊{capsule_id}不存在"
                }
            )

        # 模拟更新字段
        updated_fields = []
        if request.title:
            updated_fields.append("title")
        if request.text_content:
            updated_fields.append("description")
        if request.visibility:
            updated_fields.append("visibility")
        if request.media_files_to_remove or request.media_files_to_add:
            updated_fields.append("media_files")
        if not updated_fields:
            return ErrorResponse(
                success=False,
                message="更新失败",
                error={
                    "reason":f"没有要更新的内容"
                }
            )
        return CapsuleUpdateResponse(
            success=True,
            message="胶囊更新成功",
            capsule_id=capsule_id,
            updated_fields=updated_fields,
            updated_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新胶囊时发生错误: {str(e)}"
        )


@router.delete(
    "/{capsule_id}",
    response_model=CapsuleDeleteResponse,
    summary="删除胶囊",
    description="删除胶囊",
)
async def delete_capsule(
    capsule_id: str = Path(..., description="胶囊ID"),
    user: RegisteredUser = Depends(login_required)
):
    """删除胶囊"""
    try:
        # TODO: 实现实际的删除逻辑
        # 这里先返回模拟数据

        if capsule_id != "caps_114514":
            ErrorResponse(
                success=False,
                message="胶囊删除失败",
                error={
                    "reason":f"胶囊{capsule_id}不存在"
                }
            )

        return CapsuleDeleteResponse(
            success=True,
            message="胶囊已删除",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除胶囊时发生错误: {str(e)}"
        )



