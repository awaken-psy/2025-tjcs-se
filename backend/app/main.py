"""
时光胶囊·校园 - FastAPI 应用入口
"""
import __init__
from fastapi import FastAPI, HTTPException, Query, Path, UploadFile, File
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from api.v1 import (
    auth_router,
    capsule_router,
    unlock_router,
    event_router,
    hub_router,
    map_router,
    user_router
)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="时光胶囊·校园",
    description="基于地理位置与时间触发的校园记忆数字化平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 注册 API 路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(capsule_router, prefix="/api/v1")
app.include_router(unlock_router, prefix="/api/v1")
app.include_router(event_router, prefix="/api/v1")
app.include_router(hub_router, prefix="/api/v1")
app.include_router(map_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")

# 数据模型（用于直接在main.py中定义的接口）
class CapsuleCreateRequest(BaseModel):
    """创建胶囊请求模型"""
    title: str
    content: str
    visibility: str  # private, friends, public
    tags: Optional[List[str]] = []

class CapsuleUpdateRequest(BaseModel):
    """更新胶囊请求模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    visibility: Optional[str] = None
    tags: Optional[List[str]] = None

class CapsuleListItem(BaseModel):
    """胶囊列表项模型"""
    capsule_id: str
    title: str
    content: str
    visibility: str
    status: str
    tags: List[str]
    created_at: str
    updated_at: Optional[str] = None
    media_count: int = 0

class PaginationInfo(BaseModel):
    """分页信息模型"""
    page: int
    page_size: int
    total: int
    total_pages: int

class CapsuleListResponse(BaseModel):
    """胶囊列表响应模型"""
    capsules: List[CapsuleListItem]
    pagination: PaginationInfo

class CapsuleDetailInfo(BaseModel):
    """胶囊详情信息模型"""
    id: str
    title: str
    content: str
    visibility: str
    status: str
    tags: List[str]
    created_at: str
    updated_at: Optional[str] = None

class CapsuleDetailResponse(BaseModel):
    """胶囊详情响应模型"""
    capsule: CapsuleDetailInfo

class CapsuleCreatedResponse(BaseModel):
    """创建胶囊成功响应模型"""
    success: bool
    message: str
    capsule_id: str
    title: str
    status: str
    created_at: str

class CapsuleUpdateResponse(BaseModel):
    """更新胶囊响应模型"""
    success: bool
    message: str
    capsule_id: str
    updated_at: str

class CapsuleDeleteResponse(BaseModel):
    """删除胶囊响应模型"""
    success: bool
    message: str

# 胶囊相关接口（前端实际使用的，直接定义在main.py中）
@app.post(
    "/api/v1/capsule/create",
    response_model=CapsuleCreatedResponse,
    summary="创建胶囊(旧版)",
    description="创建新的时光胶囊，兼容旧版前端API"
)
async def create_capsule_legacy(request: CapsuleCreateRequest):
    """创建胶囊 (旧版API)"""
    try:
        return CapsuleCreatedResponse(
            success=True,
            message="胶囊创建成功",
            capsule_id="caps_114514",
            title=request.title,
            status="published",
            created_at=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建胶囊时发生错误: {str(e)}"
        )

@app.get(
    "/api/v1/capsule/my",
    response_model=CapsuleListResponse,
    summary="获取我的胶囊列表",
    description="获取当前用户创建的胶囊列表"
)
async def get_my_capsules(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """获取我的胶囊列表"""
    try:
        # 模拟胶囊数据
        mock_capsules = [
            CapsuleListItem(
                capsule_id="caps_1",
                title="我的胶囊1",
                content="这是我的第一个胶囊",
                visibility="private",
                status="published",
                tags=["个人", "回忆"],
                created_at="2024-01-15T10:30:00Z",
                updated_at="2024-01-15T10:30:00Z",
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

@app.get(
    "/api/v1/capsule/detail/{capsule_id}",
    response_model=CapsuleDetailResponse,
    summary="获取胶囊详情(旧版)",
    description="获取单个胶囊的详细信息，兼容旧版前端API"
)
async def get_capsule_detail_legacy(capsule_id: str = Path(...)):
    """获取胶囊详情 (旧版API)"""
    try:
        capsule_detail = CapsuleDetailInfo(
            id=capsule_id,
            title="毕业纪念",
            content="记录我们美好的毕业时光，这是我们在大学的最后一天，大家一起拍了很多照片，留下了珍贵的回忆。",
            visibility="public",
            status="published",
            tags=["毕业", "纪念", "校园", "回忆"],
            created_at="2024-01-15T10:30:00Z",
            updated_at="2024-01-16T11:30:00Z"
        )

        return CapsuleDetailResponse(capsule=capsule_detail)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取胶囊详情时发生错误: {str(e)}"
        )

@app.post(
    "/api/v1/capsule/edit/{capsule_id}",
    response_model=CapsuleUpdateResponse,
    summary="编辑胶囊信息(旧版)",
    description="编辑胶囊信息，兼容旧版前端API"
)
async def edit_capsule_legacy(
    request: CapsuleUpdateRequest,
    capsule_id: str = Path(...)
):
    """编辑胶囊 (旧版API - POST方法)"""
    try:
        return CapsuleUpdateResponse(
            success=True,
            message="胶囊更新成功",
            capsule_id=capsule_id,
            updated_at=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新胶囊时发生错误: {str(e)}"
        )

@app.post(
    "/api/v1/capsule/delete/{capsule_id}",
    response_model=CapsuleDeleteResponse,
    summary="删除胶囊(旧版)",
    description="删除胶囊，兼容旧版前端API"
)
async def delete_capsule_legacy(capsule_id: str = Path(...)):
    """删除胶囊 (旧版API - POST方法)"""
    try:
        return CapsuleDeleteResponse(
            success=True,
            message="胶囊已删除"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除胶囊时发生错误: {str(e)}"
        )

@app.post(
    "/api/v1/capsule/upload-img",
    summary="上传胶囊图片(旧版)",
    description="上传胶囊图片，兼容旧版前端API"
)
async def upload_capsule_image_legacy(img: UploadFile = File(...)):
    """上传胶囊图片 (旧版API)"""
    try:
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
                "size": 0
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传图片时发生错误: {str(e)}"
        )

# 根路径
@app.get("/")
async def root():
    """根路径 - 返回应用信息"""
    return {
        "message": "欢迎使用时光胶囊·校园 API",
        "version": "1.0.0",
        "docs": "/docs",
        "available_endpoints": [
            "POST /api/v1/capsule/create - 创建胶囊",
            "GET /api/v1/capsule/my - 获取我的胶囊",
            "GET /api/v1/capsule/detail/{id} - 获取胶囊详情",
            "POST /api/v1/capsule/edit/{id} - 编辑胶囊",
            "POST /api/v1/capsule/delete/{id} - 删除胶囊",
            "POST /api/v1/capsule/upload-img - 上传图片"
        ]
    }

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动时光胶囊API服务...")
    print("📖 API文档地址: http://127.0.0.1:8000/docs")
    print("❤️ 健康检查地址: http://127.0.0.1:8000/health")
    print("=" * 50)

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
