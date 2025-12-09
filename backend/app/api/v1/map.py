from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database.database import get_db
from app.model.hub import UserLocationRequest, UserLocationResponse
from app.model.base import BaseResponse
from app.auth.dependencies import login_required
from app.domain.user import AuthorizedUser
from app.logger import get_logger, api_logging

router = APIRouter(prefix='/map', tags=['Map'])
logger = get_logger(f"router<{__name__}>")


@router.get(
    "/user-location",
    response_model=BaseResponse[UserLocationResponse],
    summary="获取用户当前位置",
    description="获取当前用户最后上报的位置信息"
)
@api_logging(logger)
async def get_user_location(
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取用户当前位置"""
    try:
        # 这里简化实现，返回用户默认位置或最后上报位置
        # 实际实现需要从用户位置表获取最后的位置记录

        user_location = UserLocationResponse(
            user_id=user.user_id,
            latitude=39.9005,  # 默认值（同济大学四平路校区）
            longitude=116.3020,
            address="上海市杨浦区四平路1239号",
            updated_at=datetime.now()
        )

        return BaseResponse[UserLocationResponse].success(
            code=200,
            message="获取成功",
            data=user_location
        )

    except Exception as e:
        logger.error(f"获取用户位置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户位置失败: {str(e)}")


@router.post(
    "/report-location",
    response_model=BaseResponse[Dict[str, Any]],
    summary="上报胶囊位置",
    description="用户上报胶囊或自己的位置信息"
)
@api_logging(logger)
async def report_location(
    location_data: UserLocationRequest,
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """上报胶囊位置"""
    try:
        # 这里简化实现，实际应该保存到用户位置表
        # 可以用于用户轨迹记录、附近胶囊计算等

        # 模拟保存位置信息
        logger.info(f"用户 {user.user_id} 上报位置: {location_data.latitude}, {location_data.longitude}")

        response_data = {
            "status": "success",
            "message": "位置上报成功",
            "location": {
                "user_id": user.user_id,
                "latitude": location_data.latitude,
                "longitude": location_data.longitude,
                "address": location_data.address,
                "reported_at": datetime.now().isoformat()
            }
        }

        return BaseResponse[Dict[str, Any]].success(
            code=200,
            message="位置上报成功",
            data=response_data
        )

    except Exception as e:
        logger.error(f"上报位置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上报位置失败: {str(e)}")


@router.get(
    "/capsule-markers",
    response_model=BaseResponse[List[Dict[str, Any]]],
    summary="获取校园胶囊地理标记数据",
    description="获取地图展示需要的胶囊标记数据"
)
@api_logging(logger)
async def get_capsule_markers(
    lat_min: float = Query(..., description="最小纬度"),
    lat_max: float = Query(..., description="最大纬度"),
    lng_min: float = Query(..., description="最小经度"),
    lng_max: float = Query(..., description="最大经度"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取校园胶囊地理标记数据"""
    try:
        from app.database.repositories.capsule_repository import CapsuleRepository
        from app.services.capsule import CapsuleManager

        capsule_manager = CapsuleManager(db)

        # 获取有位置信息的胶囊
        capsules_with_location = capsule_manager.get_capsules_with_location(
            user.user_id, page=1, limit=100
        )

        # 过滤在指定地理范围内的胶囊
        markers = []
        for capsule in capsules_with_location:
            if hasattr(capsule, 'unlock_location') and capsule.unlock_location:
                location = capsule.unlock_location
                capsule_lat = location[0]
                capsule_lng = location[1]

                # 检查是否在指定范围内
                if (lat_min <= capsule_lat <= lat_max and
                    lng_min <= capsule_lng <= lng_max):

                    marker_data = {
                        "id": capsule.capsule_id,
                        "title": capsule.title,
                        "latitude": capsule_lat,
                        "longitude": capsule_lng,
                        "address": location[2] if len(location) > 2 else "",
                        "visibility": capsule.visibility.value,
                        "created_at": capsule.created_at.isoformat(),
                        "can_view": capsule.can_view_by(str(user.user_id))
                    }
                    markers.append(marker_data)

        return BaseResponse[List[Dict[str, Any]]].success(
            code=200,
            message="获取成功",
            data=markers
        )

    except Exception as e:
        logger.error(f"获取胶囊标记失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取胶囊标记失败: {str(e)}")


@router.get(
    "/heatmap-data",
    response_model=BaseResponse[List[Dict[str, Any]]],
    summary="获取校园热力图数据",
    description="获取用于生成热力图的胶囊密度数据"
)
@api_logging(logger)
async def get_heatmap_data(
    lat_min: float = Query(..., description="最小纬度"),
    lat_max: float = Query(..., description="最大纬度"),
    lng_min: float = Query(..., description="最小经度"),
    lng_max: float = Query(..., description="最大经度"),
    intensity: int = Query(5, ge=1, le=10, description="热力图强度级别"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取校园热力图数据"""
    try:
        from app.database.repositories.capsule_repository import CapsuleRepository
        from app.services.capsule import CapsuleManager

        capsule_manager = CapsuleManager(db)

        # 获取所有有位置信息的胶囊
        capsules_with_location = capsule_manager.get_capsules_with_location(
            user.user_id, page=1, limit=500
        )

        # 生成热力图数据点
        heatmap_points = []
        for capsule in capsules_with_location:
            if hasattr(capsule, 'unlock_location') and capsule.unlock_location:
                location = capsule.unlock_location
                capsule_lat = location[0]
                capsule_lng = location[1]

                # 检查是否在指定范围内
                if (lat_min <= capsule_lat <= lat_max and
                    lng_min <= capsule_lng <= lng_max):

                    # 热力图数据格式：[纬度, 经度, 强度]
                    point = [
                        capsule_lat,
                        capsule_lng,
                        intensity  # 可以根据胶囊的热度（点赞数、查看数等）调整强度
                    ]
                    heatmap_points.append(point)

        return BaseResponse[List[Dict[str, Any]]].success(
            code=200,
            message="获取成功",
            data=[{
                "points": heatmap_points,
                "max_intensity": intensity,
                "area": {
                    "lat_min": lat_min,
                    "lat_max": lat_max,
                    "lng_min": lng_min,
                    "lng_max": lng_max
                }
            }]
        )

    except Exception as e:
        logger.error(f"获取热力图数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热力图数据失败: {str(e)}")