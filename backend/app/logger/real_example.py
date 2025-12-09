"""
在真实API接口中使用装饰器的示例
展示如何装饰现有的capsule API
"""
from typing import Optional, List, Dict
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session
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
from app.logger import api_logger, api_logging

# 创建带日志装饰的路由器示例
logged_router = APIRouter(prefix='/logged-capsules', tags=['带日志的胶囊API'])


@logged_router.post(
    "/create",
    response_model=BaseResponse[CapsuleCreateResponse],
    summary="创建时光胶囊（带日志）",
    description="创建新的时光胶囊，支持多媒体内容和多种解锁条件"
)
@api_logging(api_logger)  # 添加日志装饰器
async def logged_create_capsule(
    request: CapsuleCreateRequest,
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """创建胶囊 - 带日志记录"""
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


@logged_router.get(
    "/list",
    response_model=BaseResponse[CapsuleListResponse],
    summary="获取我的胶囊列表（带日志）",
    description="获取当前用户创建的胶囊列表"
)
@api_logging(api_logger)  # 添加日志装饰器
async def logged_get_my_capsules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query("all", regex="^(all|draft|published)$"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取我的胶囊列表 - 带日志记录"""
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


@logged_router.get(
    "/detail/{capsule_id}",
    response_model=BaseResponse[CapsuleDetail],
    summary="获取胶囊详情（带日志）",
    description="获取单个胶囊的详细信息"
)
@api_logging(api_logger)  # 添加日志装饰器
async def logged_get_capsule_detail(
    capsule_id: int = Path(..., description="胶囊ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取胶囊详情 - 带日志记录"""
    manager = CapsuleManager(db)
    capsule = manager.get_capsule_detail(capsule_id, user.user_id)

    if not capsule:
        raise HTTPException(status_code=404, detail="胶囊不存在")

    return BaseResponse[CapsuleDetail].success(
        code=200,
        message="获取成功",
        data=capsule
    )


"""
实际使用说明：

1. 在现有的API文件中添加装饰器非常简单：

   # 在文件顶部导入
   from app.logger import api_logger, api_logging

   # 在函数定义前添加装饰器
   @api_logging(api_logger)
   async def create_capsule(request: CapsuleCreateRequest, ...):
       # 原有的业务逻辑代码保持不变

2. 装饰器会自动记录：
   - 完整的函数名：app.api.v1.capsules.create_capsule
   - 所有参数：request (Pydantic模型)、user (AuthorizedUser对象)、db (Session对象)
   - Pydantic模型会自动转换为字典格式
   - 处理时间（毫秒）
   - 返回结果
   - 异常信息（如果有）

3. 日志输出示例：
   API请求开始: {
     "接口名称": "app.api.v1.capsules.create_capsule",
     "参数": {
       "request": {
         "title": "我的时光胶囊",
         "content": "这是胶囊内容",
         "location": {"latitude": 39.9042, "longitude": 116.4074}
       },
       "user": "<AuthorizedUser object>",
       "db": "<Session object>"
     }
   }

   API请求完成: {
     "接口名称": "app.api.v1.capsules.create_capsule",
     "处理状态": "成功",
     "处理总用时(毫秒)": 156.78,
     "响应内容": {
       "code": 200,
       "message": "胶囊创建成功",
       "data": {"capsule_id": 123, "status": "draft"}
     }
   }

4. 在生产环境中的建议：
   - 只对关键API添加装饰器，避免日志过多
   - 定期清理日志文件
   - 根据需要调整日志级别
"""