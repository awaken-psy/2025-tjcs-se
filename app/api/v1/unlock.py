"""
解锁相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List
from datetime import datetime

from api.v1.model.request import UnlockCheckRequest, UnlockCapsuleRequest
from models.core.condition import Location
from api.v1.model.response import (
    UnlockCheckResponse,
    UnlockCapsuleResponse,
    ErrorResponse,
    SimpleCapsuleInfo,
    DetailedCapsuleInfo
)
from models.core.capsule import CapsuleStatus, Visibility
from models.core.condition import UnlockConditions

router = APIRouter(prefix="/unlock", tags=["unlock"])


@router.post(
    "/check",
    response_model=UnlockCheckResponse,
    summary="检查可解锁胶囊",
    description="根据用户位置和时间检查可以解锁的胶囊列表"
)
async def check_unlockable_capsules(request: UnlockCheckRequest):
    """检查可解锁胶囊"""
    try:

        # TODO: 实现实际的检查逻辑
        # 这里使用模拟数据演示功能

        return UnlockCheckResponse(
            success=True,
            message=f"找到 10 个胶囊，其中 3 个可以解锁",
            unlockable_capsules=[
                SimpleCapsuleInfo(
                    capsule_id="capsule_1",
                    title="毕业纪念",
                    created_at=datetime(2021, 1, 1, 0, 0, 0),
                    position=Location(
                        latitude=39.9042, 
                        longitude=116.4074,
                        address="北京市海淀区中关村")
                )
            ],
            total_capsules_found=10,
            unlockable_count=3,
            user_location=Location(
                latitude=request.user_location.latitude,
                longitude=request.user_location.longitude,
                address="北京市海淀区中关村"
            ),
            check_time=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"检查可解锁胶囊时发生错误: {str(e)}"
        )


@router.post(
    "/capsule",
    response_model=UnlockCapsuleResponse,
    summary="解锁胶囊",
    description="解锁指定的胶囊"
)
async def unlock_capsule(request: UnlockCapsuleRequest):
    """解锁胶囊"""
    try:

        # TODO: 实现实际的解锁逻辑
        # 这里使用模拟数据演示功能


        # 模拟解锁成功
        return UnlockCapsuleResponse(
            success=True,
            message="解锁成功",
            capsule_id=request.capsule_id,
            unlocked_at=datetime.now().isoformat(),
            capsule_context=DetailedCapsuleInfo(
                capsule_id=request.capsule_id
            ),
            unlock_method="手动解锁",
            unlock_conditions_met=["时间条件", "位置条件"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"解锁胶囊时发生错误: {str(e)}"
        )