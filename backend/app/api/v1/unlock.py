"""
Unlock API interface
"""
from fastapi import APIRouter, Depends

from app.model import (
    BaseResponse,
    UnlockCapsuleRequest,
    UnlockCapsuleResponse,
    NearbyCapsulesQuery,
    NearbyCapsulesResponse
)

router = APIRouter(prefix='/unlock', tags=['Unlock'])


@router.post("/{capsule_id}", response_model=BaseResponse[UnlockCapsuleResponse])
async def unlock_capsule(
    capsule_id: str,
    request: UnlockCapsuleRequest
):
    """解锁胶囊"""
    pass


@router.get("/nearby", response_model=BaseResponse[NearbyCapsulesResponse])
async def get_nearby_capsules(
    query: NearbyCapsulesQuery = Depends()
):
    """获取附近胶囊"""
    pass


@router.get("/{capsule_id}/status", response_model=BaseResponse[dict])
async def get_unlock_status(
    capsule_id: str
):
    """获取解锁状态"""
    pass