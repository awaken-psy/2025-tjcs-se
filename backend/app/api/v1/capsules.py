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

from model.capsule import (
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
router = APIRouter()


capsules_store: Dict[str, CapsuleDetail] = {}

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
    user: AuthorizedUser = Depends(login_required)
):
    """获取胶囊详情"""
    # TODO: 从数据库查询胶囊详情
    # 目前返回模拟数据，符合CapsuleDetail模型结构
    
    data = CapsuleDetail(
        id=capsule_id,
        title="时光胶囊示例",
        content="这是胶囊的完整内容，记录了美好的回忆...",
        visibility="public",
        status="published",
        created_at=datetime.utcnow(),
        tags=["回忆", "青春", "纪念"],
        location=Location(
            latitude=31.2304,
            longitude=121.4737,
            address="上海市浦东新区"
        ),
        unlock_conditions=UnlockConditions(
            type="time",
            value="2024-12-31T23:59:59Z",
            is_unlocked=False
        ),
        media_files=[
            MediaFile(
                id="file_123",
                type="image",
                url="https://example.com/files/photo.jpg",
                thumbnail="https://example.com/files/thumb.jpg"
            )
        ],
        creator=Creator(
            user_id=user.user_id,
            nickname=getattr(user, 'nickname', '用户'),
            avatar=getattr(user, 'avatar', None)
        ),
        stats=CapsuleStats(
            view_count=150,
            like_count=25,
            comment_count=8,
            unlock_count=5,
            is_liked=True,
            is_collected=False
        ),
        updated_at=datetime.utcnow()
    )
    
    return BaseResponse[CapsuleDetail].success(
        code=200,
        message="获取成功",
        data=data
    )


#数据库表映射到CapsuleBasic数据模型
def _map_to_basic(c) -> CapsuleBasic:
    """把 ORM / domain 对象映射为 CapsuleBasic"""
    return CapsuleBasic(
        id=str(getattr(c, "id", "")),
        title=getattr(c, "title", ""),
        visibility=getattr(c, "visibility", "private"),
        status=getattr(c, "status", "draft"),
        created_at=getattr(c, "created_at", datetime.utcnow()),
        content_preview=(getattr(c, "text_content", "")[:120] if getattr(c, "text_content", None) else None),
        cover_image=(getattr(c, "cover_img", None) or (getattr(c, "media_files", [None])[0].url if getattr(c, "media_files", None) else None)),
        unlock_count=(getattr(c, "unlock_count", 0) if getattr(c, "unlock_count", None) is not None else 0),
        like_count=(getattr(c, "like_count", 0) if getattr(c, "like_count", None) is not None else 0),
        comment_count=(getattr(c, "comment_count", 0) if getattr(c, "comment_count", None) is not None else 0)
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
    db: Session = Depends(get_db)
):
    """从 DB 读取当前用户的胶囊并返回 CapsuleListResponse（CapsuleBasic 列表 + pagination）"""
    manager = CapsuleManager(db)
    result = manager.get_user_capsules(user_id=user.user_id, page=page, limit=limit, status_filter=None)
    items = result.get("capsules", [])
    total = result.get("total", len(items))

    basic_list = [ _map_to_basic(c) for c in items ]

    total_pages = result.get("total_pages", (total + limit - 1) // limit if total > 0 else 1)
    pagination = Pagination(page=result.get("page", page), page_size=result.get("limit", limit), total=total, total_pages=total_pages)

    return BaseResponse.success(
        code = 200,
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
    user: AuthorizedUser = Depends(login_required)
):
    """编辑胶囊"""
    
    # 这里可以添加数据库更新逻辑
    # 目前先返回成功响应
    
    return BaseResponse[CapsuleUpdateResponse].success(
        code=200,
        message="更新成功",
        data=CapsuleUpdateResponse(
            capsule_id=capsule_id,
            updated_at=datetime.utcnow()
        )
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
    user: AuthorizedUser = Depends(login_required)
):
    """保存草稿"""
    draft_id = _make_capsule_id()
    now = _now()
    created = CapsuleDraftResponse(
        draft_id=draft_id,
        saved_at=now
    )#APIFOX上需要的数据结构

    return BaseResponse[CapsuleDraftResponse].success(
        code = 200,
        message="操作成功",
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
    """多模式浏览胶囊"""
    # TODO: 从数据库查询胶囊数据
    # 目前返回模拟数据
    
    if mode == "map":
        # 地图模式：返回带位置信息的胶囊
        capsules = [
            CapsuleBasic(
                id="capsule_1",
                title="外滩回忆",
                visibility="public",
                status="published",
                created_at=datetime.utcnow(),
                content_preview="在外滩的美好回忆...",
                cover_image="https://picsum.photos/id/1/300/200",
                like_count=25,
                view_count=150
            ),
            CapsuleBasic(
                id="capsule_2", 
                title="同济时光",
                visibility="public",
                status="published",
                created_at=datetime.utcnow(),
                content_preview="在同济大学的点点滴滴...",
                cover_image="https://picsum.photos/id/2/300/200",
                like_count=30,
                view_count=200
            )
        ]
        
        data = MultiModeBrowseResponse(
            mode=mode,
            capsules=capsules
        )
        
    elif mode == "timeline":
        # 时间轴模式：按时间分组的胶囊
        timeline_groups = {
            "2024年1月": [
                CapsuleBasic(
                    id="capsule_3",
                    title="新年愿望",
                    visibility="public",
                    status="published", 
                    created_at=datetime(2024, 1, 15, 10, 30),
                    content_preview="2024年的新年愿望...",
                    cover_image="https://picsum.photos/id/3/300/200",
                    like_count=15,
                    view_count=80
                )
            ],
            "2023年12月": [
                CapsuleBasic(
                    id="capsule_4",
                    title="圣诞回忆",
                    visibility="public",
                    status="published",
                    created_at=datetime(2023, 12, 25, 18, 0),
                    content_preview="圣诞节的美好时光...",
                    cover_image="https://picsum.photos/id/4/300/200", 
                    like_count=20,
                    view_count=120
                )
            ]
        }
        
        data = MultiModeBrowseResponse(
            mode=mode,
            timeline_groups=timeline_groups
        )
        
    elif mode == "tags":
        # 标签模式：按标签分类的胶囊
        capsules = [
            CapsuleBasic(
                id="capsule_5",
                title="毕业纪念",
                visibility="public",
                status="published",
                created_at=datetime.utcnow(),
                content_preview="毕业典礼的珍贵时刻...",
                cover_image="https://picsum.photos/id/5/300/200",
                like_count=50,
                view_count=300
            )
        ]
        
        data = MultiModeBrowseResponse(
            mode=mode,
            capsules=capsules
        )
        
    else:
        raise HTTPException(status_code=400, detail="不支持的浏览模式")
    
    return BaseResponse[MultiModeBrowseResponse].success(
        code=200,
        message="获取成功",
        data=data
    )