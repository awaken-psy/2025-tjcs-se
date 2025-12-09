from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sqlalchemy.orm import Session
import secrets

from app.model.unlock import (
    CurrentLocation, UnlockCapsuleRequest, UnlockCapsuleResponse,
    NearbyCapsule, NearbyCapsulesResponse, NearbyCapsuleLocation
)
from app.model.base import BaseResponse, Pagination
from app.auth.dependencies import login_required
from app.domain.user import AuthorizedUser
from app.services.unlock_manager import UnlockManager
from app.database.database import get_db
from app.auth.jwt_handler import JWTHandler

router = APIRouter(prefix='/unlock', tags=['Unlock'])


@router.post(
    "/{capsule_id}",
    response_model=BaseResponse[UnlockCapsuleResponse],
    summary="解锁胶囊",
    description="根据位置或时间条件解锁时光胶囊"
)
async def unlock_capsule(
    request: UnlockCapsuleRequest,
    capsule_id: str = Path(..., description="胶囊ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """
    解锁胶囊API

    请求格式: { "current_location": { "latitude": 39.9042, "longitude": 116.4074 } }
    """
    try:
        current_time = datetime.now()

        # 调用服务层进行解锁
        unlock_manager = UnlockManager(db)

        # 解锁胶囊
        result = unlock_manager.unlock_capsule(
            user_id=user.user_id,
            capsule_id=capsule_id,
            user_latitude=request.current_location.latitude,
            user_longitude=request.current_location.longitude
        )

        if result.get('success', False):
            # 生成解锁访问令牌 - 使用JWT而非随机字符串
            # 这里可以生成一个包含解锁信息的特殊JWT
            unlock_token_payload = {
                "capsule_id": capsule_id,
                "user_id": user.user_id,
                "unlocked_at": current_time.isoformat(),
                "type": "unlock_access"
            }

            # 或者重新生成用户当前的JWT token
            # 这里选择重新生成用户的JWT，因为用户已经有了有效的认证
            access_token = JWTHandler.generate_access_token(
                user_id=user.user_id,
                username=user.username,
                role=user.role,
                permissions=list(user.permissions) if user.permissions else []
            )

            response_data = UnlockCapsuleResponse(
                capsule_id=str(capsule_id),  # 确保为字符串类型
                unlocked_at=current_time,
                access_token=access_token
            )

            return BaseResponse[UnlockCapsuleResponse].success(
                code=200,
                message="胶囊解锁成功",
                data=response_data
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get('message', '解锁失败')
            )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"解锁失败: {str(e)}")


@router.get(
    "/nearby",
    response_model=BaseResponse[NearbyCapsulesResponse],
    summary="获取附近胶囊",
    description="获取用户当前位置附近可解锁的时光胶囊"
)
async def get_nearby_capsules(
    latitude: float = Query(..., description="用户当前纬度"),
    longitude: float = Query(..., description="用户当前经度"),
    radius_meters: int = Query(100, ge=10, le=10000, description="搜索半径（米）"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """
    获取附近可解锁胶囊API
    """
    try:
        # 调用服务层获取附近胶囊
        unlock_manager = UnlockManager(db)

        result = unlock_manager.get_nearby_capsules(
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters,
            user_id=user.user_id,
            page=page,
            limit=limit
        )

        if result.get('success', False):
            # 转换服务层数据为API响应格式
            capsules_data = []

            for capsule_item in result.get('capsules', []):
                capsule = capsule_item.get('capsule', {})

                # 转换为API需要的格式
                capsule_api_data = NearbyCapsule(
                    id=capsule.get('id', ''),
                    title=capsule.get('title', '未知胶囊'),
                    location=NearbyCapsuleLocation(
                        latitude=capsule.get('unlock_location', [0, 0])[0],
                        longitude=capsule.get('unlock_location', [0, 0])[1],
                        distance=capsule_item.get('distance', 0)
                    ),
                    visibility=capsule.get('visibility', 'private'),
                    is_unlocked=capsule.get('status') == 'unlocked',
                    can_unlock=capsule_item.get('unlockable', False),
                    creator_nickname="用户",  # 服务层数据中没有此字段，使用默认值
                    created_at=capsule.get('created_at', datetime.now())
                )
                capsules_data.append(capsule_api_data)

            response_data = NearbyCapsulesResponse(capsules=capsules_data)

            return BaseResponse[NearbyCapsulesResponse].success(
                code=200,
                message=f"成功获取{len(capsules_data)}个附近胶囊",
                data=response_data
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('message', '获取附近胶囊失败')
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取附近胶囊时发生错误: {str(e)}"
        )


@router.get(
    "/{capsule_id}/status",
    response_model=BaseResponse[dict],
    summary="获取胶囊解锁状态",
    description="检查指定胶囊的解锁状态和解锁条件"
)
async def get_unlock_status(
    capsule_id: str = Path(..., description="胶囊ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取解锁状态"""
    try:
        # 调用服务层检查解锁状态
        unlock_manager = UnlockManager(db)

        # 检查用户是否已解锁该胶囊
        has_unlocked = unlock_manager.has_user_unlocked_capsule(user.user_id, capsule_id)

        # 获取胶囊信息
        capsule_domain = unlock_manager.repository.find_by_id(capsule_id)

        if not capsule_domain:
            raise HTTPException(status_code=404, detail="胶囊不存在")

        # 检查解锁条件
        unlock_conditions = unlock_manager.check_unlock_conditions(
            domain=capsule_domain,
            user_id=user.user_id
        )

        response_data = {
            "capsule_id": capsule_id,
            "is_unlocked": has_unlocked,
            "can_unlock": unlock_conditions.get('can_unlock', False),
            "unlock_time": capsule_domain.unlock_time.isoformat() if capsule_domain.unlock_time else None,
            "failed_conditions": unlock_conditions.get('failed_conditions', []),
            "conditions_met": unlock_conditions.get('conditions_met', [])
        }

        return BaseResponse[dict].success(
            code=200,
            message="获取解锁状态成功",
            data=response_data
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取解锁状态失败: {str(e)}"
        )