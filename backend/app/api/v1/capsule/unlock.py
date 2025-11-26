"""
解锁相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List
from datetime import datetime

from app.model.capsule_model import UnlockCheckRequest, UnlockCapsuleRequest, UnlockVerifyRequest, UnlockVerifyResponse
from utils.location import Location
from app.model.capsule_model import (
    UnlockCheckResponse,
    UnlockCapsuleResponse,
    SimpleCapsuleInfo,
    DetailedCapsuleInfo
)
from auth.dependencies import login_required
from domain.capsule import CapsuleStatus, Visibility
from domain.condition import UnlockConditions
from domain.user import RegisteredUser
from services.capsule_manager import CapsuleManager

router = APIRouter(prefix="/unlock", tags=["Unlock"])


@router.post(
    "/check",
    response_model=UnlockCheckResponse,
    summary="检查可解锁胶囊",
    description="根据用户位置和时间检查可以解锁的胶囊列表"
)
async def check_unlockable_capsules(
    request: UnlockCheckRequest,
    user:RegisteredUser = Depends(login_required)):
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
async def unlock_capsule(
    request: UnlockCapsuleRequest,
    user:RegisteredUser = Depends(login_required)
    ):
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


@router.post(
    "/verify",
    response_model=UnlockVerifyResponse,
    summary="验证解锁条件",
    description="验证用户当前位置和时间是否满足胶囊的解锁条件，满足则执行解锁操作并返回访问令牌"
)
async def verify_unlock_conditions(
    request: UnlockVerifyRequest,
    user: RegisteredUser = Depends(login_required)
):
    """验证解锁条件"""
    try:
        # 初始化胶囊管理器
        capsule_manager = CapsuleManager()

        # 如果请求中有指定胶囊ID，则验证特定胶囊
        if request.capsule_id:
            result = capsule_manager.verify_unlock_conditions(
                capsule_id=request.capsule_id,
                user_id=user.user_id,
                user_lat=request.current_location.latitude,
                user_lon=request.current_location.longitude,
                current_time=request.current_time
            )

            if result["success"]:
                # 解锁成功，返回访问令牌和相关信息
                return UnlockVerifyResponse(
                    code=200,
                    data={
                        "access_token": result["access_token"],
                        "capsule_id": result["capsule_id"],
                        "unlocked_at": result["unlocked_at"]
                    },
                    message="胶囊解锁成功"
                )
            else:
                # 解锁失败
                return UnlockVerifyResponse(
                    code=400,
                    data=None,
                    message=f"解锁失败: {result['reason']}"
                )
        else:
            # 如果没有指定胶囊ID，返回错误（此API要求必须指定胶囊ID）
            return UnlockVerifyResponse(
                code=400,
                data=None,
                message="请指定要验证的胶囊ID"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"验证解锁条件时发生错误: {str(e)}"
        )
