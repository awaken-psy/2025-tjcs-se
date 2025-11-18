"""
胶囊相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Query, Path, Depends, UploadFile, File
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from domain.user import RegisteredUser
from auth.dependencies import login_required

from model.capsule_model import (
    CapsuleCreateRequest, CapsuleUpdateRequest,
    CapsuleCreatedResponse, CapsuleListResponse, CapsuleDetailResponse,
    CapsuleUpdateResponse, ErrorResponse, CapsuleDeleteResponse,
    CapsuleStatus, CapsuleVisibility, Location, UnlockConditions,
    CapsuleListItem, PaginationInfo, MediaFile, UserInfo, CapsuleStats,
    CapsuleDetailInfo
)

from ..routes import capsule_router as router


@router.post(
    "/",
    response_model=CapsuleCreatedResponse,
    summary="创建时光胶囊",
    description="创建新的时光胶囊，支持多媒体内容和多种解锁条件"
)
async def create_capsule(request: CapsuleCreateRequest, user: RegisteredUser = Depends(login_required)):
    """创建胶囊 (新版API)"""
    try:
        # TODO: 实现实际的胶囊创建逻辑
        # 这里先返回模拟数据

        return CapsuleCreatedResponse(
            success=True,
            message="胶囊创建成功",
            capsule_id="caps_114514",
            title=request.title,
            status=CapsuleStatus.PUBLISHED,
            created_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建胶囊时发生错误: {str(e)}"
        )


@router.post(
    "/create",
    response_model=CapsuleCreatedResponse,
    summary="创建时光胶囊(旧版)",
    description="创建新的时光胶囊，兼容旧版前端API"
)
async def create_capsule_legacy(request: CapsuleCreateRequest, user: RegisteredUser = Depends(login_required)):
    """创建胶囊"""
    try:
        # TODO: 实现实际的胶囊创建逻辑
        # 这里先返回模拟数据

        return CapsuleCreatedResponse(
            success=True,
            message="胶囊创建成功",
            capsule_id="caps_114514",
            title=request.title,
            status=CapsuleStatus.PUBLISHED,
            created_at=datetime.now()
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
    status: Optional[str] = Query(None, description="按状态筛选"),
    visibility: Optional[str] = Query(None, description="按可见性筛选"),
    user: RegisteredUser = Depends(login_required)
):
    """获取可查看的胶囊列表"""
    try:
        # TODO: 实现实际的查询逻辑
        # 这里先返回模拟数据

        # 模拟胶囊数据
        mock_capsules = [
            CapsuleListItem(
                capsule_id="caps_1",
                title="毕业纪念",
                content="记录我们美好的毕业时光",
                visibility=CapsuleVisibility.PUBLIC,
                status=CapsuleStatus.PUBLISHED,
                tags=["毕业", "纪念", "校园"],
                created_at=datetime(2024, 1, 15, 10, 30, 0),
                updated_at=datetime(2024, 1, 15, 10, 30, 0),
                location=Location(latitude=39.9042, longitude=116.4074, address="北京大学"),
                media_count=3
            ),
            CapsuleListItem(
                capsule_id="caps_2",
                title="足球比赛",
                content="激动人心的决赛时刻",
                visibility=CapsuleVisibility.FRIENDS,
                status=CapsuleStatus.PUBLISHED,
                tags=["足球", "比赛", "运动"],
                created_at=datetime(2024, 2, 20, 15, 45, 0),
                updated_at=datetime(2024, 2, 20, 15, 45, 0),
                location=Location(latitude=39.9050, longitude=116.4080, address="体育场"),
                media_count=5
            ),
            CapsuleListItem(
                capsule_id="caps_3",
                title="旅行日记",
                content="第一次去西藏的美好回忆",
                visibility=CapsuleVisibility.PRIVATE,
                status=CapsuleStatus.DRAFT,
                tags=["旅行", "西藏", "日记"],
                created_at=datetime(2024, 3, 10, 9, 15, 0),
                updated_at=datetime(2024, 3, 12, 14, 20, 0),
                location=Location(latitude=29.6500, longitude=91.1000, address="拉萨"),
                media_count=8
            )
        ]

        # 模拟分页信息
        total_items = len(mock_capsules)
        total_pages = (total_items + limit - 1) // limit
        pagination = PaginationInfo(
            page=page,
            page_size=limit,
            total=total_items,
            total_pages=total_pages
        )

        return CapsuleListResponse(
            capsules=mock_capsules,
            pagination=pagination
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取胶囊列表时发生错误: {str(e)}"
        )


@router.get(
    "/my",
    response_model=CapsuleListResponse,
    summary="获取我的胶囊列表",
    description="获取当前用户创建的胶囊列表"
)
async def get_my_capsules(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user: RegisteredUser = Depends(login_required)
):
    """获取我的胶囊列表"""
    try:
        # TODO: 实现实际的查询逻辑
        # 这里先返回模拟数据

        # 模拟胶囊数据
        mock_capsules = [
            CapsuleListItem(
                capsule_id="caps_1",
                title="我的胶囊1",
                content="这是我的第一个胶囊",
                visibility=CapsuleVisibility.PRIVATE,
                status=CapsuleStatus.PUBLISHED,
                tags=["个人", "回忆"],
                created_at=datetime(2024, 1, 15, 10, 30, 0),
                updated_at=datetime(2024, 1, 15, 10, 30, 0),
                media_count=2
            )
        ]

        # 模拟分页信息
        total_items = len(mock_capsules)
        total_pages = (total_items + limit - 1) // limit
        pagination = PaginationInfo(
            page=page,
            page_size=limit,
            total=total_items,
            total_pages=total_pages
        )

        return CapsuleListResponse(
            capsules=mock_capsules,
            pagination=pagination
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取我的胶囊列表时发生错误: {str(e)}"
        )


@router.get(
    "/detail/{capsule_id}",
    response_model=CapsuleDetailResponse,
    summary="获取胶囊详情(旧版)",
    description="获取单个胶囊的详细信息，兼容旧版前端API"
)
async def get_capsule_detail_legacy(
    capsule_id: str = Path(..., description="胶囊ID"),
    user: RegisteredUser = Depends(login_required)
):
    """获取胶囊详情 (旧版API)"""
    return await get_capsule_detail(capsule_id, user)


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

        # 模拟媒体文件数据
        media_files = [
            MediaFile(
                id="file_1",
                type="image",
                url="https://example.com/files/photo1.jpg",
                thumbnail="https://example.com/files/thumbnail1.jpg"
            ),
            MediaFile(
                id="file_2",
                type="audio",
                url="https://example.com/files/audio1.mp3",
                duration=120.5
            )
        ]

        # 模拟解锁条件数据
        from model.capsule_model import UnlockCondition
        unlock_conditions = UnlockConditions(conditions=[
            UnlockCondition(
                type="time",
                value="2024-12-31T23:59:59Z",
                is_unlocked=False
            ),
            UnlockCondition(
                type="location",
                value="39.9042,116.4074",
                radius=50,
                is_unlocked=False
            )
        ])

        # 模拟胶囊详情数据
        capsule_detail = CapsuleDetailInfo(
            id=capsule_id,
            title="毕业纪念",
            content="记录我们美好的毕业时光，这是我们在大学的最后一天，大家一起拍了很多照片，留下了珍贵的回忆。",
            visibility=CapsuleVisibility.PUBLIC,
            status=CapsuleStatus.PUBLISHED,
            tags=["毕业", "纪念", "校园", "回忆"],
            location=Location(
                latitude=39.9042,
                longitude=116.4074,
                address="北京大学图书馆"
            ),
            unlock_conditions=unlock_conditions,
            media_files=media_files,
            creator=UserInfo(
                user_id=123,
                nickname="小明",
                avatar="https://example.com/avatar.jpg"
            ),
            stats=CapsuleStats(
                view_count=150,
                like_count=25,
                comment_count=8,
                unlock_count=5,
                is_liked=True,
                is_collected=False
            ),
            created_at=datetime(2024, 1, 15, 10, 30, 0),
            updated_at=datetime(2024, 1, 16, 11, 30, 0)
        )

        return CapsuleDetailResponse(capsule=capsule_detail)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取胶囊详情时发生错误: {str(e)}"
        )


@router.post(
    "/edit/{capsule_id}",
    response_model=CapsuleUpdateResponse,
    summary="编辑胶囊信息(旧版)",
    description="编辑胶囊信息，兼容旧版前端API"
)
async def edit_capsule_legacy(
    request: CapsuleUpdateRequest,
    capsule_id: str = Path(..., description="胶囊ID"),
    user: RegisteredUser = Depends(login_required)
):
    """编辑胶囊 (旧版API - POST方法)"""
    return await update_capsule(request, capsule_id, user)


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
        if request.content:
            updated_fields.append("content")
        if request.visibility:
            updated_fields.append("visibility")
        if request.tags:
            updated_fields.append("tags")
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
            updated_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新胶囊时发生错误: {str(e)}"
        )


@router.post(
    "/delete/{capsule_id}",
    response_model=CapsuleDeleteResponse,
    summary="删除胶囊(旧版)",
    description="删除胶囊，兼容旧版前端API"
)
async def delete_capsule_legacy(
    capsule_id: str = Path(..., description="胶囊ID"),
    user: RegisteredUser = Depends(login_required)
):
    """删除胶囊 (旧版API - POST方法)"""
    return await delete_capsule(capsule_id, user)


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
            return ErrorResponse(
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


@router.post(
    "/upload-img",
    summary="上传胶囊图片(旧版)",
    description="上传胶囊图片，兼容旧版前端API"
)
async def upload_capsule_image_legacy(
    img: UploadFile = File(..., description="图片文件"),
    user: RegisteredUser = Depends(login_required)
):
    """上传胶囊图片 (旧版API)"""
    try:
        # TODO: 实现实际的图片上传逻辑
        # 这里先返回模拟数据

        if not img.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="只能上传图片文件"
            )

        # 模拟上传成功
        return {
            "success": True,
            "message": "图片上传成功",
            "data": {
                "url": f"https://example.com/uploads/{img.filename}",
                "filename": img.filename,
                "size": 0  # 实际应该获取文件大小
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传图片时发生错误: {str(e)}"
        )


