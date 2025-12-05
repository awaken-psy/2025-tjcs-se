from typing import Optional, List, Dict
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session  # 添加这个
from app.model.capsule import (
    CapsuleCreateRequest, CapsuleUpdateRequest,
    CapsuleDraftRequest, CapsuleCreateResponse,
    CapsuleDetail, CapsuleUpdateResponse, CapsuleListResponse, 
    CapsuleBasic, CapsuleDraftResponse, MultiModeBrowseResponse
)
from app.model.base import Pagination, BaseResponse
from app.auth.dependencies import login_required
from app.domain.user import AuthorizedUser
from app.services.capsule import CapsuleManager
from app.database.database import get_db

router = APIRouter(prefix='/capsules', tags=['Capsules'])

@router.post(
    "/",
    response_model=BaseResponse[CapsuleCreateResponse],
    summary="创建时光胶囊",
    description="创建新的时光胶囊，支持多媒体内容和多种解锁条件"
)
async def create_capsule(
    request: CapsuleCreateRequest, 
    user: AuthorizedUser = Depends(login_required), 
    db: Session = Depends(get_db)
):
    """创建胶囊"""
    try:
        manager = CapsuleManager(db)
        response = manager.create_capsule(request, user.user_id)

        return BaseResponse[CapsuleCreateResponse].success(
            code=200,
            message="胶囊创建成功",
            data=response
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建胶囊失败: {str(e)}")

@router.get(
    "/my",
    response_model=BaseResponse[CapsuleListResponse],
    summary="获取我的胶囊列表",
    description="获取当前用户创建的胶囊列表"
)
async def get_my_capsules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query("all", regex="^(all|draft|published)$"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取我的胶囊列表"""
    manager = CapsuleManager(db)
    result = manager.get_user_capsules(user.user_id, page, page_size)
    
    pagination = Pagination(
        page=result['page'],
        page_size=result['limit'],
        total=result['total'],
        total_pages=result['total_pages']
    )
    
    return BaseResponse[CapsuleListResponse].success(
        code=200,
        message="获取成功",
        data=CapsuleListResponse(capsules=result['capsules'], pagination=pagination)
    )

@router.get(
    "/{capsule_id}",
    response_model=BaseResponse[CapsuleDetail],
    summary="获取胶囊详情",
    description="获取单个胶囊的详细信息"
)
async def get_capsule_detail(
    capsule_id: int = Path(..., description="胶囊ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取胶囊详情"""
    manager = CapsuleManager(db)
    capsule_detail = manager.get_capsule_detail(capsule_id, user.user_id, user)
    
    if not capsule_detail:
        raise HTTPException(status_code=404, detail="胶囊不存在或无权访问")
    
    return BaseResponse[CapsuleDetail].success(
        code=200,
        message="获取成功",
        data=capsule_detail
    )

@router.put(
    "/{capsule_id}",
    response_model=BaseResponse[CapsuleUpdateResponse],
    summary="编辑胶囊信息",
    description="编辑胶囊信息，仅限创建者或管理员操作"
)
async def update_capsule(
    capsule_id: int = Path(..., description="胶囊ID"),
    request: CapsuleUpdateRequest = ...,
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """更新胶囊"""
    try:
        manager = CapsuleManager(db)
        success = manager.update_capsule(capsule_id, request, user.user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="胶囊不存在或无权限编辑")
        
        return BaseResponse[CapsuleUpdateResponse].success(
            code=200,
            message="更新成功",
            data=CapsuleUpdateResponse(
                capsule_id=capsule_id,
                updated_at=datetime.utcnow()
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新胶囊时发生错误: {str(e)}")

@router.delete(
    "/{capsule_id}",
    response_model=BaseResponse,
    summary="删除胶囊",
    description="删除胶囊，仅限创建者或管理员操作"
)
async def delete_capsule(
    capsule_id: int = Path(..., description="胶囊ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """删除胶囊"""
    try:
        manager = CapsuleManager(db)
        success = manager.delete_capsule(capsule_id, user.user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="胶囊不存在或无权限删除")

        return BaseResponse.success(
            code=200,
            message="删除成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除胶囊时发生错误: {str(e)}")

@router.post(
    "/drafts",
    response_model=BaseResponse[CapsuleDraftResponse],
    summary="保存草稿",
    description="保存胶囊草稿"
)
async def save_draft(
    request: CapsuleDraftRequest,
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """保存草稿"""
    try:
        manager = CapsuleManager(db)
        response = manager.save_draft(request, user.user_id)

        return BaseResponse[CapsuleDraftResponse].success(
            code=200,
            message="草稿保存成功",
            data=response
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存草稿失败: {str(e)}")

@router.get(
    "/browse",
    response_model=BaseResponse[MultiModeBrowseResponse],
    summary="多模式浏览胶囊",
    description="支持地图模式、时间轴模式、标签模式浏览胶囊"
)
async def browse_capsules(
    mode: str = Query(..., regex="^(map|timeline|tags)$"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """多模式浏览胶囊"""
    try:
        manager = CapsuleManager(db)
        
        if mode == "map":
            capsules = manager.get_capsules_with_location(user.user_id)
            return BaseResponse[MultiModeBrowseResponse].success(
                code=200,
                message="获取成功",
                data=MultiModeBrowseResponse(
                    mode=mode,
                    capsules=[capsule.to_api_basic() for capsule in capsules]
                )
            )
        elif mode == "timeline":
            timeline_groups = manager.get_capsules_by_timeline(user.user_id)
            api_timeline_groups = {}
            for month, capsules in timeline_groups.items():
                api_timeline_groups[month] = [capsule.to_api_basic() for capsule in capsules]
            
            return BaseResponse[MultiModeBrowseResponse].success(
                code=200,
                message="获取成功",
                data=MultiModeBrowseResponse(
                    mode=mode,
                    timeline_groups=api_timeline_groups
                )
            )
        elif mode == "tags":
            capsules = manager.get_capsules_by_tags(user.user_id)
            return BaseResponse[MultiModeBrowseResponse].success(
                code=200,
                message="获取成功",
                data=MultiModeBrowseResponse(
                    mode=mode,
                    capsules=[capsule.to_api_basic() for capsule in capsules]
                )
            )
        else:
            raise HTTPException(status_code=400, detail="不支持的浏览模式")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取胶囊时发生错误: {str(e)}")