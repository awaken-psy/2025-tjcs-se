"""
时光胶囊API接口
"""
from app.database.database import get_db
from sqlalchemy.orm import Session
from app.services.capsule import CapsuleManager

from typing import Optional, List,Dict
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends, Query, Path
import json
from app.model.capsule import (
    CapsuleCreateRequest, CapsuleUpdateRequest,
    Location, UnlockConditions,
    MediaFile, CapsuleStats,Creator,
    CapsuleDraftRequest,
    CapsuleCreateResponse, CapsuleDetail,
    CapsuleUpdateResponse, CapsuleListResponse,CapsuleBasic
    , CapsuleDraftResponse,MultiModeBrowseResponse
)
from app.model.base import Pagination
from app.model.base import BaseResponse
from app.auth.dependencies import login_required
from app.domain.user import AuthorizedUser

# 创建API路由
router = APIRouter(prefix='/capsules', tags=['Capsules'])

def _map_to_basic(capsule) -> CapsuleBasic:
    """把ORM对象映射为CapsuleBasic"""
    return CapsuleBasic(
        id=str(capsule.id),
        title=capsule.title,
        visibility=capsule.visibility,
        status=capsule.status,
        created_at=capsule.created_at,
        content_preview=(capsule.text_content[:120] if capsule.text_content else None),
        cover_image=None,  # TODO: 从CapsuleMedia获取封面图
        unlock_count=0,  # TODO: 从UnlockRecord统计
        like_count=0,   # TODO: 从交互记录统计
        comment_count=0  # TODO: 从交互记录统计
    )


def _map_to_detail(capsule, user: AuthorizedUser) -> CapsuleDetail:
    """把ORM对象映射为CapsuleDetail"""
    return CapsuleDetail(
        id=str(capsule.id),
        title=capsule.title,
        content=capsule.text_content,
        visibility=capsule.visibility,
        status=capsule.status,
        created_at=capsule.created_at,
        tags=json.loads(capsule.tag_json) if capsule.tag_json else [],
        location=Location(
            latitude=capsule.latitude,
            longitude=capsule.longitude,
            address=capsule.address
        ) if capsule.latitude and capsule.longitude else None,
        unlock_conditions=None,  # TODO: 从UnlockCondition表查询
        media_files=[],  # TODO: 从CapsuleMedia表查询
        creator=Creator(
            user_id=capsule.user_id,
            nickname=getattr(user, 'nickname', '用户'),
            avatar=getattr(user, 'avatar', None)
        ),
        stats=CapsuleStats(
            view_count=0,     # TODO: 从访问记录统计
            like_count=0,     # TODO: 从点赞记录统计
            comment_count=0,  # TODO: 从评论记录统计
            unlock_count=0,   # TODO: 从解锁记录统计
            is_liked=False,   # TODO: 查询用户是否点赞
            is_collected=False  # TODO: 查询用户是否收藏
        ),
        updated_at=capsule.updated_at
    )


def _now() -> datetime:
    return datetime.utcnow()
def _make_capsule_id() -> str:
    return f"capsule_{int(datetime.utcnow().timestamp() * 1000)}"
# 胶囊创建API
@router.post(
    "/",
    response_model=BaseResponse[CapsuleCreateResponse],
    summary="创建时光胶囊",
    description="创建新的时光胶囊，支持多媒体内容和多种解锁条件"
)
async def create_capsule(request: CapsuleCreateRequest, user: AuthorizedUser = Depends(login_required)):
    """创建胶囊"""
    capsule_id = _make_capsule_id()
    now = _now()
    created = CapsuleCreateResponse(
        capsule_id=capsule_id,
        title=request.title,
        status="draft",
        created_at=datetime.utcnow()
    )#APIFOX上需要的数据结构

    return BaseResponse[CapsuleCreateResponse].success(
        code = 200,
        message="操作成功",
        data=created
    )


# 获取胶囊详情API - 返回标准CapsuleDetail模型
@router.get(
    "/{capsule_id}",
    response_model=BaseResponse[CapsuleDetail],
    summary="获取胶囊详情",
    description="获取单个胶囊的详细信息"
)
async def get_capsule_detail(
    capsule_id: str = Path(..., description="胶囊ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)  # 添加这行
):
    """获取胶囊详情"""
    manager = CapsuleManager(db)
    
    capsule = manager.get_capsule_detail(capsule_id, user.user_id)
    if not capsule:
        raise HTTPException(status_code=404, detail="胶囊不存在")
    
    data = _map_to_detail(capsule, user)
    
    return BaseResponse[CapsuleDetail].success(
        code=200,
        message="获取成功",
        data=data
    )


#获取我的列表
@router.get(
    "/my",
    response_model=BaseResponse[CapsuleListResponse],
    summary="获取我的胶囊列表",
    description="获取当前用户创建的胶囊列表（返回 CapsuleBasic 列表 + Pagination）"
)
async def get_my_capsules(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)  # 添加这行
):
    """获取我的胶囊列表"""
    manager = CapsuleManager(db)
    
    result = manager.get_user_capsules(user.user_id, page, limit)
    capsules = result.get("capsules", [])
    
    basic_list = [_map_to_basic(c) for c in capsules]
    
    # 移除capsules_store，使用真实数据
    total = result.get("total", len(capsules))
    total_pages = result.get("total_pages", (total + limit - 1) // limit if total > 0 else 1)
    pagination = Pagination(page=result.get("page", page), page_size=result.get("limit", limit), total=total, total_pages=total_pages)
    
    return BaseResponse[CapsuleListResponse].success(
        code=200,
        message="获取成功",
        data=CapsuleListResponse(capsules=basic_list, pagination=pagination)
    )



#删除胶囊API
@router.delete(
    "/{capsule_id}",
    response_model=BaseResponse,
    summary="删除胶囊",
    description="删除胶囊，仅限创建者或管理员操作"
)
async def delete_capsule(
    capsule_id: str = Path(..., description="胶囊ID"),
    user: AuthorizedUser = Depends(login_required)
):
    """删除胶囊"""
    return BaseResponse.success(
        code = 200,
        message="删除成功"
    )

# 编辑胶囊API
@router.put(
    "/{capsule_id}",
    response_model=BaseResponse[CapsuleUpdateResponse],
    summary="编辑胶囊信息",
    description="编辑胶囊信息，仅限创建者或管理员操作"
)
async def edit_capsule(
    request: CapsuleUpdateRequest,
    capsule_id: str = Path(..., description="胶囊ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """编辑胶囊：通过 CapsuleManager.update_capsule_from_request 更新并返回结果（不使用 try/except）"""
    manager = CapsuleManager(db)

    # 直接调用 manager 的更新方法（方法在 services/capsule.py 中已实现）
    updated = manager.update_capsule_from_request(capsule_id, request, user.user_id)
    if not updated:
        raise HTTPException(status_code=404, detail="胶囊不存在或无权限更新")

    # 读取更新后的对象以获取 updated_at（若不可用则使用当前时间）
    capsule = manager.get_capsule_detail(capsule_id, user.user_id)
    updated_at = getattr(capsule, "updated_at", datetime.utcnow()) if capsule else datetime.utcnow()

    resp = CapsuleUpdateResponse(
        capsule_id=capsule_id,
        updated_at=updated_at
    )

    return BaseResponse[CapsuleUpdateResponse].success(
        code=200,
        message="更新成功",
        data=resp
    )


#保存草稿API
@router.post(
    "/draft",
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
    manager = CapsuleManager(db)
    
    capsule = manager.save_draft_from_request(request, user.user_id)
    
    created = CapsuleDraftResponse(
        draft_id=str(capsule.id),
        saved_at=capsule.created_at
    )
    
    return BaseResponse[CapsuleDraftResponse].success(
        code=200,
        message="保存成功",
        data=created
    )


#多模式浏览胶囊API
# 多模式胶囊浏览API
@router.get(
    "/browse",
    response_model=BaseResponse[MultiModeBrowseResponse],
    summary="多模式浏览胶囊",
    description="支持map/timeline/tags三种模式浏览胶囊"
)
async def browse_capsules(
    mode: str = Query("timeline", description="浏览模式: map/timeline/tags"),
    page: int = Query(1, ge=1, description="页码（map和tags模式使用）"),
    limit: int = Query(20, ge=1, le=100, description="每页数量（map和tags模式使用）"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """多模式浏览胶囊：从数据库通过 CapsuleManager 获取数据并按模型返回"""
    manager = CapsuleManager(db)

    if mode == "map":
        # 地图模式：取有位置信息的胶囊（支持分页）
        capsules_orm = manager.get_capsules_with_location(user.user_id, page=page, limit=limit)
        capsules = [_map_to_basic(c) for c in capsules_orm]

        total = len(capsules_orm)  # 若需要真实 total，后续在 Manager 中增加 count 查询
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        pagination = Pagination(page=page, page_size=limit, total=total, total_pages=total_pages)

        data = MultiModeBrowseResponse(
            mode=mode,
            capsules=capsules,
            pagination=pagination
        )

    elif mode == "timeline":
        # 时间轴模式：按月份分组返回（不分页）
        timeline_raw = manager.get_capsules_by_timeline(user.user_id)
        timeline_groups = {}
        for month, group in timeline_raw.items():
            timeline_groups[month] = [_map_to_basic(c) for c in group]

        data = MultiModeBrowseResponse(
            mode=mode,
            timeline_groups=timeline_groups
        )

    elif mode == "tags":
        # 标签模式：按标签/分页返回
        capsules_orm = manager.get_capsules_by_tags(user.user_id, page=page, limit=limit)
        capsules = [_map_to_basic(c) for c in capsules_orm]

        total = len(capsules_orm)
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        pagination = Pagination(page=page, page_size=limit, total=total, total_pages=total_pages)

        data = MultiModeBrowseResponse(
            mode=mode,
            capsules=capsules,
            pagination=pagination
        )

    else:
        raise HTTPException(status_code=400, detail="不支持的浏览模式")

    return BaseResponse[MultiModeBrowseResponse].success(
        code=200,
        message="获取成功",
        data=data
    )


# ============== NEARBY CAPSULES API ==============

@router.get(
    "/nearby",
    response_model=BaseResponse[dict],
    summary="获取附近胶囊",
    description="获取用户附近的胶囊列表，包含距离和解锁状态信息"
)
async def get_nearby_capsules(
    latitude: float = Query(..., description="用户当前纬度"),
    longitude: float = Query(..., description="用户当前经度"),
    radius_meters: int = Query(1000, ge=10, le=10000, description="搜索半径（米）"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取附近胶囊"""
    try:
        # 使用CapsuleManager获取附近胶囊
        manager = CapsuleManager(db)

        # 尝试使用services中的nearby功能
        try:
            # 导入nearby相关的服务
            from app.services.capsule_manager import CapsuleManager as NearbyCapsuleManager

            nearby_manager = NearbyCapsuleManager()
            if hasattr(nearby_manager, 'get_nearby_capsules'):
                nearby_data = nearby_manager.get_nearby_capsules(latitude, longitude, radius_meters, user.user_id)

                return BaseResponse[dict].success(
                    code=200,
                    message=f"成功获取{len(nearby_data)}个附近胶囊",
                    data={
                        "capsules": nearby_data
                    }
                )
        except ImportError:
            pass

        # 如果nearby服务不可用，返回基础查询结果
        # 这里可以实现简单的距离查询逻辑
        capsules_orm = manager.get_capsules(user.user_id, page=1, limit=50)

        # 简单的附近胶囊筛选（基于位置的大致过滤）
        nearby_capsules = []
        for capsule_orm in capsules_orm:
            if capsule_orm.latitude and capsule_orm.longitude:
                # 简单的距离计算（实际应该使用更精确的方法）
                distance = ((latitude - capsule_orm.latitude) ** 2 +
                          (longitude - capsule_orm.longitude) ** 2) ** 0.5 * 111000  # 转换为大致米数

                if distance <= radius_meters:
                    capsule_data = {
                        "id": str(capsule_orm.id),
                        "title": capsule_orm.title,
                        "can_unlock": False,  # 需要实现解锁条件检查
                        "created_at": capsule_orm.created_at,
                        "creator_nickname": getattr(user, 'nickname', '用户'),
                        "is_unlocked": False,
                        "location": {
                            "distance": distance,
                            "latitude": capsule_orm.latitude,
                            "longitude": capsule_orm.longitude
                        },
                        "visibility": capsule_orm.visibility
                    }
                    nearby_capsules.append(capsule_data)

        # 按距离排序
        nearby_capsules.sort(key=lambda x: x["location"]["distance"])

        return BaseResponse[dict].success(
            code=200,
            message=f"成功获取{len(nearby_capsules)}个附近胶囊",
            data={
                "capsules": nearby_capsules
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取附近胶囊时发生错误: {str(e)}"
        )