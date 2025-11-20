"""
胶囊相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Query, Path, Depends, UploadFile, File
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from model.capsule_model import (
    CapsuleCreateRequest, CapsuleCreateRequestLegacy, CapsuleUpdateRequest,
    CapsuleCreatedResponse, CapsuleListResponse, CapsuleListResponseLegacy, CapsuleDetailResponse,
    CapsuleUpdateResponse, ErrorResponse, CapsuleDeleteResponse,
    CapsuleStatus, CapsuleVisibility, Location, UnlockConditions,
    CapsuleListItem, PaginationInfo, MediaFile, UserInfo, CapsuleStats,
    CapsuleDetailInfo
)

# 导入服务类
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from services.capsule import CapsuleManager
from services.file_manager import FileManager

capsule_router = APIRouter(prefix='/capsule', tags=['Capsule'])
router = capsule_router  # 为了兼容现有代码

# 临时模拟认证依赖
def login_required():
    class MockUser:
        def __init__(self):
            self.id = 1
            self.username = "test_user"
    return MockUser()

class RegisteredUser:
    pass


@router.post(
    "/",
    response_model=CapsuleCreatedResponse,
    summary="创建时光胶囊",
    description="创建新的时光胶囊，支持多媒体内容和多种解锁条件"
)
async def create_capsule(request: CapsuleCreateRequest, user: RegisteredUser = Depends(login_required)):
    """创建胶囊 (新版API)"""
    try:
        # 初始化胶囊管理器
        capsule_manager = CapsuleManager()

        # 转换请求数据 - 兼容两种格式
        capsule_data = {
            'title': request.title,
            'content': request.content,
            'visibility': request.visibility.value,
            'tags': request.tags if request.tags else [],
            'media_files': request.media_files if request.media_files else []
        }

        # 处理位置信息 - 兼容嵌套和扁平格式
        if request.location:
            # 嵌套格式: {latitude: xxx, longitude: xxx, address: xxx}
            capsule_data['location'] = request.location.address if hasattr(request.location, 'address') else str(request.location)
            capsule_data['lat'] = request.location.latitude if hasattr(request.location, 'latitude') else 0.0
            capsule_data['lng'] = request.location.longitude if hasattr(request.location, 'longitude') else 0.0
        else:
            capsule_data['location'] = None
            capsule_data['lat'] = 0.0
            capsule_data['lng'] = 0.0

        # 简化创建：返回模拟成功结果，避免数据库依赖
        mock_capsule_id = f"mock_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        return CapsuleCreatedResponse(
            success=True,
            message="胶囊创建成功",
            capsule_id=mock_capsule_id,
            title=capsule_data['title'],
            status=CapsuleStatus.PUBLISHED,
            created_at=datetime.utcnow()
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
async def create_capsule_legacy(request: CapsuleCreateRequestLegacy, user: RegisteredUser = Depends(login_required)):
    """创建胶囊"""
    try:
        # 初始化胶囊管理器
        capsule_manager = CapsuleManager()

        # 转换请求数据格式
        capsule_data = {
            'title': request.title,
            'content': request.content,
            'visibility': request.visibility,
            'tags': request.tags if request.tags else [],
            'location': request.location,
            'lat': request.lat or 0.0,
            'lng': request.lng or 0.0,
            'imageUrl': request.imageUrl,
            'createTime': request.createTime,
            'updateTime': request.updateTime
        }

        # 简化创建：返回模拟成功结果，避免数据库依赖
        mock_capsule_id = f"mock_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        return CapsuleCreatedResponse(
            success=True,
            message="胶囊创建成功",
            capsule_id=mock_capsule_id,
            title=capsule_data['title'],
            status=CapsuleStatus.PUBLISHED,
            created_at=datetime.utcnow()
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
        # 简化实现：暂时返回模拟数据，避免数据库问题
        capsule_items = []

        # 模拟数据 - 前端兼容格式
        mock_capsules = [
            {
                "capsule_id": "mock_1",
                "title": "毕业纪念胶囊",
                "content": "记录我们美好的毕业时光，这是我们在大学的最后一天，大家一起拍了很多照片，留下了珍贵的回忆。",
                "visibility": "public",
                "status": "published",
                "tags": ["毕业", "纪念", "校园"],
                "created_at": datetime(2024, 1, 15, 10, 30, 0),
                "updated_at": datetime(2024, 1, 16, 11, 30, 0),
                "location": {
                    "latitude": 31.2834,
                    "longitude": 121.5057,
                    "address": "上海市同济大学"
                },
                "media_count": 2
            },
            {
                "capsule_id": "mock_2",
                "title": "上海迪士尼之旅",
                "content": "第一次和朋友们一起来迪士尼，大家都玩得很开心！最喜欢的项目是飞跃地平线，看到了世界各地的美景。",
                "visibility": "public",
                "status": "published",
                "tags": ["迪士尼", "上海", "旅行"],
                "created_at": datetime(2024, 2, 14, 9, 15, 0),
                "updated_at": datetime(2024, 2, 14, 9, 15, 0),
                "location": {
                    "latitude": 31.1434,
                    "longitude": 121.6580,
                    "address": "上海迪士尼乐园"
                },
                "media_count": 1
            }
        ]

        for capsule_data in mock_capsules:
            capsule_item = CapsuleListItem(**capsule_data)
            capsule_items.append(capsule_item)

        # 构建分页信息
        pagination = PaginationInfo(
            page=page,
            page_size=limit,
            total=len(capsule_items),
            total_pages=1
        )

        return CapsuleListResponse(
            capsules=capsule_items,
            pagination=pagination
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取胶囊列表时发生错误: {str(e)}"
        )


@router.get(
    "/my",
    response_model=CapsuleListResponseLegacy,
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
        # 简化实现：返回模拟数据，格式匹配前端期望
        capsule_data = []

        # 模拟我的胶囊数据
        mock_my_capsules = [
            {
                "id": "my_mock_1",
                "capsule_id": "my_mock_1",
                "title": "我的毕业纪念",
                "time": "2024-01-15T10:30:00Z",
                "vis": "public",
                "desc": "这是我的毕业纪念胶囊，记录了美好的大学时光。",
                "tags": ["毕业", "纪念", "我的"],
                "likes": 25,
                "views": 150,
                "liked": True,
                "collected": False,
                "location": "上海市同济大学",
                "img": "/uploads/images/graduation.jpg",
                "status": "published",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-16T11:30:00Z"
            },
            {
                "id": "my_mock_2",
                "capsule_id": "my_mock_2",
                "title": "生日愿望",
                "time": "2024-03-20T18:30:00Z",
                "vis": "private",
                "desc": "今天我20岁了！感谢爸爸妈妈和朋友们为我准备的惊喜派对。",
                "tags": ["生日", "愿望", "家人"],
                "likes": 18,
                "views": 85,
                "liked": True,
                "collected": True,
                "location": "家里",
                "img": "/uploads/images/birthday.jpg",
                "status": "draft",
                "created_at": "2024-03-20T18:30:00Z",
                "updated_at": "2024-03-21T09:15:00Z"
            }
        ]

        capsule_data = mock_my_capsules

        # 数据已经是前端兼容格式，无需转换

        # 前端期望的分页对象格式
        response_data = {
            'list': capsule_data,
            'page': page,
            'size': limit,
            'total': len(capsule_data),
            'totalPages': 1
        }

        return CapsuleListResponseLegacy(
            code=200,
            message="success",
            data=response_data,
            total=len(capsule_data)
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
        # 验证文件类型
        if not img.content_type or not img.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="只能上传图片文件"
            )

        # 初始化文件管理器
        file_manager = FileManager()

        # 上传文件
        result = await file_manager.upload_capsule_file(img, 'image')

        # 返回兼容旧版格式的响应
        return {
            "success": True,
            "message": "图片上传成功",
            "data": {
                "url": result['data']['access_url'],
                "filename": result['data']['filename'],
                "size": result['data']['file_size']
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传图片时发生错误: {str(e)}"
        )


