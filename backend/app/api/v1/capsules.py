"""
Capsules API interface
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.model import (
    BaseResponse,
    CapsuleCreateRequest,
    CapsuleCreateResponse,
    CapsuleUpdateRequest,
    CapsuleUpdateResponse,
    CapsuleDraftRequest,
    CapsuleDraftResponse,
    CapsuleListResponse,
    CapsuleDetail,
    MyCapsulesQuery,
    BrowseCapsulesQuery,
    BrowseCapsulesResponse
)

router = APIRouter(prefix='/capsules', tags=['Capsules'])


@router.post("/", response_model=BaseResponse[CapsuleCreateResponse])
async def create_capsule(
    request: CapsuleCreateRequest
):
    """创建胶囊"""
    pass


@router.get("/my", response_model=BaseResponse[CapsuleListResponse])
async def get_my_capsules(
    query: MyCapsulesQuery = Depends()
):
    """获取我的胶囊"""
    pass


@router.get("/browse", response_model=BaseResponse[BrowseCapsulesResponse])
async def browse_capsules(
    query: BrowseCapsulesQuery = Depends()
):
    """浏览胶囊"""
    pass


@router.get("/{capsule_id}", response_model=BaseResponse[CapsuleDetail])
async def get_capsule_detail(
    capsule_id: str
):
    """获取胶囊详情"""
    pass


@router.put("/{capsule_id}", response_model=BaseResponse[CapsuleUpdateResponse])
async def update_capsule(
    capsule_id: str,
    request: CapsuleUpdateRequest
):
    """更新胶囊"""
    pass


@router.delete("/{capsule_id}", response_model=BaseResponse[None])
async def delete_capsule(
    capsule_id: str
):
    """删除胶囊"""
    pass


@router.post("/{capsule_id}/draft", response_model=BaseResponse[CapsuleDraftResponse])
async def save_draft(
    capsule_id: str,
    request: CapsuleDraftRequest
):
    """保存草稿"""
    pass