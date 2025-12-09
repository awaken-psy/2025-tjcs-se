from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database.database import get_db
from app.model.hub import (
    UserInfoResponse, RecentActivity, RecentActivitiesResponse,
    NearbyCapsulesQuery, HubNearbyCapsulesResponse
)
from app.model.base import BaseResponse, Pagination
from app.model.unlock import NearbyCapsule
from app.auth.dependencies import login_required
from app.domain.user import AuthorizedUser
from app.logger import get_logger, api_logging
from app.services.capsule import CapsuleManager

router = APIRouter(prefix='/hub', tags=['Hub'])
logger = get_logger(f"router<{__name__}>")


@router.get(
    "/user-info",
    response_model=BaseResponse[UserInfoResponse],
    summary="获取用户基础信息",
    description="获取当前用户的基础信息和统计数据"
)
@api_logging(logger)
async def get_user_info(
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取用户基础信息"""
    try:
        # 获取用户统计信息
        from app.database.repositories.capsule_repository import CapsuleRepository

        capsule_repo = CapsuleRepository(db)

        # 获取用户胶囊统计
        user_capsules = capsule_repo.find_by_user_id(user.user_id, 1, 1000)
        total_capsules = user_capsules['total']

        # 获取解锁统计（这里简化处理，实际可能需要更复杂的统计逻辑）
        unlocked_count = 0  # TODO: 实现解锁统计

        stats = {
            "created_capsules": total_capsules,
            "unlocked_capsules": unlocked_count,
            "friends_count": 0,  # TODO: 实现好友统计
            "collection_count": 0  # TODO: 实现收藏统计
        }

        user_info = UserInfoResponse(
            user_id=user.user_id,
            nickname=user.nickname,
            avatar=user.avatar_url,
            email=user.email or "",
            created_at=user.created_at,
            stats=stats
        )

        return BaseResponse[UserInfoResponse].success(
            code=200,
            message="获取成功",
            data=user_info
        )

    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")


@router.get(
    "/nearby-capsules",
    response_model=BaseResponse[HubNearbyCapsulesResponse],
    summary="获取附近胶囊列表",
    description="获取用户当前位置附近的胶囊列表"
)
@api_logging(logger)
async def get_nearby_capsules(
    lat: float = Query(..., description="当前纬度"),
    lng: float = Query(..., description="当前经度"),
    range: int = Query(500, ge=10, le=10000, description="搜索半径（米）"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取附近胶囊列表"""
    try:
        manager = CapsuleManager(db)

        # 使用现有的解锁API获取附近胶囊
        from app.services.unlock_manager import UnlockManager
        unlock_manager = UnlockManager(db)

        # 获取附近的胶囊
        nearby_capsules = unlock_manager.get_nearby_capsules(
            latitude=lat,
            longitude=lng,
            radius_meters=range,  # 使用前端传递的range参数
            user_id=user.user_id,
            page=page,
            limit=limit
        )

        # 转换为hub响应格式
        response_capsules = []
        for capsule in nearby_capsules.get('capsules', []):
            # 创建位置信息
            location = {
                "latitude": capsule['latitude'],
                "longitude": capsule['longitude'],
                "distance": capsule['distance']
            }

            # 创建附近胶囊对象
            nearby_capsule = NearbyCapsule(
                id=str(capsule['id']),
                title=capsule['title'],
                location=location,
                visibility=capsule['visibility'],
                is_unlocked=capsule['is_unlocked'],
                can_unlock=capsule['can_unlock'],
                creator_nickname=capsule.get('creator_nickname', '匿名'),
                created_at=capsule['created_at']
            )
            response_capsules.append(nearby_capsule)

        response = HubNearbyCapsulesResponse(
            capsules=response_capsules
        )

        return BaseResponse[HubNearbyCapsulesResponse].success(
            code=200,
            message="获取成功",
            data=response
        )

    except Exception as e:
        logger.error(f"获取附近胶囊失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取附近胶囊失败: {str(e)}")


@router.get(
    "/recent-activities",
    response_model=BaseResponse[RecentActivitiesResponse],
    summary="获取最近用户动态",
    description="获取校园内最近的用户动态信息"
)
@api_logging(logger)
async def get_recent_activities(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取最近用户动态"""
    try:
        # 这里简化实现，返回模拟数据
        # 实际实现需要从数据库获取最近的动态

        activities = [
            RecentActivity(
                id=1,
                type="capsule_created",
                user_id=2,
                user_nickname="用户A",
                target_id=1,
                content="创建了新胶囊《我的回忆》",
                created_at=datetime.now(),
                metadata={"capsule_title": "我的回忆"}
            ),
            RecentActivity(
                id=2,
                type="capsule_unlocked",
                user_id=3,
                user_nickname="用户B",
                target_id=2,
                content="解锁了胶囊《时光印记》",
                created_at=datetime.now(),
                metadata={"capsule_title": "时光印记"}
            ),
            RecentActivity(
                id=3,
                type="friend_added",
                user_id=4,
                user_nickname="用户C",
                target_id=5,
                content="添加了新好友",
                created_at=datetime.now(),
                metadata={"friend_name": "用户D"}
            )
        ]

        response = RecentActivitiesResponse(
            activities=activities,
            total=len(activities)
        )

        return BaseResponse[RecentActivitiesResponse].success(
            code=200,
            message="获取成功",
            data=response
        )

    except Exception as e:
        logger.error(f"获取最近动态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取最近动态失败: {str(e)}")