from typing import Optional, List, Dict
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Path # 导入 FastAPI 核心组件
from sqlalchemy.orm import Session # 导入数据库 Session
from app.database.database import get_db # 数据库依赖注入函数
from app.model.capsule import (
    CapsuleCreateRequest, CapsuleUpdateRequest, # 请求体模型
    CapsuleDraftRequest, CapsuleCreateResponse,
    CapsuleDetail, CapsuleUpdateResponse, CapsuleListResponse, 
    CapsuleBasic, CapsuleDraftResponse, MultiModeBrowseResponse # 响应体模型
)
from app.model.base import Pagination, BaseResponse # 基础响应结构和分页模型
from app.auth.dependencies import login_required # 登录认证依赖函数
from app.domain.user import AuthorizedUser # 认证后的用户领域模型
from app.services.capsule import CapsuleManager # 核心业务逻辑服务管理器
from app.logger import get_logger, api_logging # 日志记录工具

# 初始化 FastAPI 路由和日志
router = APIRouter(prefix='/capsules', tags=['Capsules']) # 设置路由前缀 /capsules
logger = get_logger(f"router<{__name__}>")

 

## 📝 胶囊创建与存储

@router.post(
    "/",
    response_model=BaseResponse[CapsuleCreateResponse],
    summary="创建时光胶囊",
    description="创建新的时光胶囊，支持多媒体内容和多种解锁条件"
)
@api_logging(logger)
async def create_capsule(
    raw_data: dict,  # 接受原始前端数据 (注意: 这里使用 dict 而非 Pydantic 模型是为了处理 location 字段的灵活性)
    user: AuthorizedUser = Depends(login_required), # 依赖注入：确保用户已登录，并获取用户信息
    db: Session = Depends(get_db), # 依赖注入：获取数据库会话
):
    """创建胶囊"""
    try:
        manager = CapsuleManager(db)

        # 添加调试信息
        # logger.info(f"接收到的原始数据: {raw_data}")

        location_data = raw_data.get('location')
        location_obj = None

        # 1. 业务特殊处理：手动解析和验证 location 字段
        # 由于前端数据结构可能不完全匹配 CapsuleCreateRequest，此处需手动提取并构造 Location 模型。
        logger.info(f"location_data: {location_data}, type: {type(location_data)}")

        if isinstance(location_data, dict):
            lat = location_data.get('latitude')
            lng = location_data.get('longitude')

            logger.info(f"从location对象中提取: lat={lat}, lng={lng}")

            # 2. 检查经纬度是否存在且非空
            if lat is not None and lng is not None:
                from app.model.capsule import Location # 局部导入 Location 模型
                location_obj = Location(
                    # 注意：如果客户端发送的是字符串，这里需要进行类型转换
                    latitude=float(lat), # 强制类型转换为 float
                    longitude=float(lng),# 强制类型转换为 float
                    address=location_data.get('address', '')
                )
                logger.info(f"构造的location_obj: {location_obj}")
            else:
                logger.warning(f"经纬度为空: lat={lat}, lng={lng}")
        else:
            logger.warning(f"location_data不是字典类型或为空: {location_data}")

        # 构建标准的 CapsuleCreateRequest 对象，用于传递给 Service 层
        # Pydantic 模型提供了严格的类型检查和数据转换
        request = CapsuleCreateRequest(
            title=raw_data['title'],
            content=raw_data['content'],
            visibility=raw_data['visibility'],
            tags=raw_data.get('tags', []),
            location=location_obj, # 传递解析后的 Location 对象
            unlock_conditions=raw_data.get('unlock_conditions'),
            media_files=raw_data.get('media_files', [])
        )

        # 调用 Service 层执行创建胶囊的核心业务逻辑
        response = manager.create_capsule(request, user.user_id)

        # 直接返回服务层的响应（已经在服务层完成类型转换）
        return BaseResponse[CapsuleCreateResponse].success(
            code=200,
            message="胶囊创建成功",
            data=response  # response已经是正确的格式
        )

    except Exception as e:
        # 捕获异常，并统一返回 500 错误
        raise HTTPException(status_code=500, detail=f"创建胶囊失败: {str(e)}")

 

## 📃 胶囊读取 (列表与详情)

@router.get(
    "/my",
    response_model=BaseResponse[CapsuleListResponse],
    summary="获取我的胶囊列表",
    description="获取当前用户创建的胶囊列表"
)
@api_logging(logger)
async def get_my_capsules(
    page: int = Query(1, ge=1), # 分页参数：当前页码，默认 1
    size: int = Query(20, ge=1, le=100),  # 分页参数：每页大小，默认 20
    status: str = Query("all", pattern="^(all|draft|published)$"), # 过滤状态：all, draft (草稿), published (已发布)
    user: AuthorizedUser = Depends(login_required), # 确保用户已登录
    db: Session = Depends(get_db), # 依赖注入：获取数据库会话
):
    """获取我的胶囊列表"""
    manager = CapsuleManager(db) # 🔥 修复：传递数据库会话
    # 调用 Service 层获取用户胶囊列表、总数和分页信息
    result = manager.get_user_capsules(user.user_id, page, size, status, user)

    # 构造标准分页信息响应
    pagination = Pagination(
        page=result['page'],
        page_size=size,
        total=result['total'],
        total_pages=result['total_pages']
    )

    return BaseResponse[CapsuleListResponse].success(
        code=200,
        message="获取成功",
        # 构造列表响应模型，包含胶囊列表和分页信息
        data=CapsuleListResponse(capsules=result['capsules'], pagination=pagination)
    )

## 🌐 胶囊多模式浏览

@router.get(
    "/browse",
    response_model=BaseResponse[MultiModeBrowseResponse],
    summary="多模式浏览胶囊",
    description="支持地图模式、时间轴模式、标签模式浏览胶囊"
)
@api_logging(logger)
async def browse_capsules(
    mode: str = Query(..., pattern="^(map|timeline|tags)$"), # 查询参数：浏览模式，强制限制为 'map', 'timeline', 'tags' 之一
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db), # 依赖注入：获取数据库会话
):
    """多模式浏览胶囊"""
    try:
        manager = CapsuleManager(db)

        if mode == "map":
            # 地图模式：获取带有地理位置信息的胶囊，用于在地图上展示
            capsules = manager.get_capsules_with_location(user.user_id, page, size)
            return BaseResponse[MultiModeBrowseResponse].success(
                code=200,
                message="获取成功",
                data=MultiModeBrowseResponse(
                    mode=mode,
                    # 将领域模型对象转换为 API 基础响应模型
                    capsules=[capsule.to_api_basic() for capsule in capsules]
                )
            )
        elif mode == "timeline":
            # 时间轴模式：获取按时间分组的胶囊数据
            timeline_groups: Dict[str, List] = manager.get_capsules_by_timeline(user.user_id)
            api_timeline_groups = {}
            # 遍历 Service 层返回的分组数据，转换为 API 响应格式
            for month, capsules in timeline_groups.items():
                api_timeline_groups[month] = [capsule.to_api_basic() for capsule in capsules]

            return BaseResponse[MultiModeBrowseResponse].success(
                code=200,
                message="获取成功",
                data=MultiModeBrowseResponse(
                    mode=mode,
                    timeline_groups=api_timeline_groups # 返回按月分组的列表
                )
            )
        elif mode == "tags":
            # 标签模式：获取按标签分类或简单列表的胶囊数据
            capsules = manager.get_capsules_by_tags(user.user_id, page, size)
            return BaseResponse[MultiModeBrowseResponse].success(
                code=200,
                message="获取成功",
                data=MultiModeBrowseResponse(
                    mode=mode,
                    capsules=[capsule.to_api_basic() for capsule in capsules]
                )
            )
        else:
            # 路由参数已使用 pattern 限制，但为了健壮性保留此检查
            raise HTTPException(status_code=400, detail="不支持的浏览模式")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取胶囊时发生错误: {str(e)}")

@router.get(
    "/{capsule_id}",
    response_model=BaseResponse[CapsuleDetail],
    summary="获取胶囊详情",
    description="获取单个胶囊的详细信息"
)
@api_logging(logger)
async def get_capsule_detail(
    capsule_id: int = Path(..., description="胶囊ID"), # 路径参数：胶囊ID
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db), # 依赖注入：获取数据库会话
):
    """获取胶囊详情"""
    manager = CapsuleManager(db) # 🔥 修复：传递数据库会话
    # 调用 Service 层获取胶囊详情，Service 层会处理权限检查和解锁状态判断
    capsule_detail = manager.get_capsule_detail(capsule_id, user.user_id, user)

    if not capsule_detail:
        # 如果 Service 层返回空，则表示胶囊不存在或用户无权访问
        raise HTTPException(status_code=404, detail="胶囊不存在或无权访问")

    return BaseResponse[CapsuleDetail].success(
        code=200,
        message="获取成功",
        data=capsule_detail
    )

 

## 🔄 胶囊更新与删除 (CRUD)

@router.put(
    "/{capsule_id}",
    response_model=BaseResponse[CapsuleUpdateResponse],
    summary="编辑胶囊信息",
    description="编辑胶囊信息，仅限创建者或管理员操作"
)
@api_logging(logger)
async def update_capsule(
    capsule_id: int = Path(..., description="胶囊ID"),
    request: CapsuleUpdateRequest = ..., # 请求体模型
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db), # 依赖注入：获取数据库会话
):
    """更新胶囊"""
    try:
        manager = CapsuleManager(db)
        # 调用 Service 层执行更新操作，Service 负责权限验证和数据持久化
        success = manager.update_capsule(capsule_id, request, user.user_id)
        
        if not success:
            # Service 层返回 False 表示权限不足或胶囊不存在
            raise HTTPException(status_code=404, detail="胶囊不存在或无权限编辑")
        
        return BaseResponse[CapsuleUpdateResponse].success(
            code=200,
            message="更新成功",
            data=CapsuleUpdateResponse(
                capsule_id=str(capsule_id),
                updated_at=datetime.utcnow() # 返回更新时间
            )
        )

    except HTTPException:
        # 重新抛出已知的 HTTPException，避免被通用 Exception 捕获
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新胶囊时发生错误: {str(e)}")

@router.delete(
    "/{capsule_id}",
    response_model=BaseResponse,
    summary="删除胶囊",
    description="删除胶囊，仅限创建者或管理员操作"
)
@api_logging(logger)
async def delete_capsule(
    capsule_id: int = Path(..., description="胶囊ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db), # 依赖注入：获取数据库会话
):
    """删除胶囊"""
    try:
        manager = CapsuleManager(db)
        # 调用 Service 层执行删除操作，Service 负责权限验证和数据删除
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
        raise HTTPException(status_code=500, detail=f"删除胶囊时发生错误: {str(e)}")

 

## 💾 草稿保存

@router.post(
    "/drafts",
    response_model=BaseResponse[CapsuleDraftResponse],
    summary="保存草稿",
    description="保存胶囊草稿"
)
@api_logging(logger)
async def save_draft(
    request: CapsuleDraftRequest,
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db), # 依赖注入：获取数据库会话
):
    """保存草稿"""
    try:
        manager = CapsuleManager(db)
        # 调用 Service 层处理草稿保存逻辑
        response = manager.save_draft(request, user.user_id)

        return BaseResponse[CapsuleDraftResponse].success(
            code=200,
            message="草稿保存成功",
            data=response # 返回草稿ID和更新时间
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存草稿失败: {str(e)}")

 

