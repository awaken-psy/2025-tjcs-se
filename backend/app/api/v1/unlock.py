from typing import Optional
from datetime import datetime
from app.utils.datetime_helper import beijing_now
from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sqlalchemy.orm import Session
import secrets # 原始代码中导入了 secrets，但未在最终逻辑中使用，可忽略或用于替代 JWT 的临时令牌

# 导入数据模型 (Pydantic DTOs)
from app.model.unlock import (
    CurrentLocation, UnlockCapsuleRequest, UnlockCapsuleResponse,  # 解锁请求和响应模型
    NearbyCapsulesResponse  # 附近胶囊响应模型
)
from app.model.base import BaseResponse, Pagination # 基础响应结构和分页模型
from app.auth.dependencies import login_required # 认证依赖
from app.domain.user import AuthorizedUser # 认证后的用户领域模型
from app.domain.capsule import Capsule
from app.services.unlock_manager import UnlockManager # 核心解锁业务逻辑服务
from app.database.database import get_db # 数据库 Session 依赖
from app.auth.jwt_handler import JWTHandler # JWT 处理工具，用于生成 Token

from app.logger import get_logger, api_logging

# 初始化 FastAPI 路由
router = APIRouter(prefix='/unlock', tags=['Unlock'])
logger = get_logger(f"route<{__name__}>")


## 🔐 接口: 解锁胶囊 (Unlock Capsule)
@router.post(
    "/{capsule_id}",
    response_model=BaseResponse[UnlockCapsuleResponse],
    summary="解锁胶囊",
    description="根据位置或时间条件解锁时光胶囊"
)
@api_logging(logger)
async def unlock_capsule(
    request: UnlockCapsuleRequest, # 请求体：包含用户当前位置 (latitude, longitude)
    capsule_id: str = Path(..., description="胶囊ID"), # 路径参数：待解锁的胶囊 ID
    user: AuthorizedUser = Depends(login_required), # 依赖注入：确保用户已登录
    db: Session = Depends(get_db) # 依赖注入：获取数据库会话
):
    """
    解锁胶囊API：用户尝试对指定的胶囊执行解锁操作。
    """
    try:
        current_time = beijing_now()

        # 实例化服务层管理器
        unlock_manager = UnlockManager(db)

        # 调用 Service 层进行解锁的核心判断：
        # Service 负责：1. 获取胶囊信息；2. 检查位置/时间/好友等条件是否满足；3. 记录解锁日志
        result = unlock_manager.unlock_capsule(
            user_id=user.user_id,
            capsule_id=capsule_id,
            user_latitude=request.current_location.latitude,
            user_longitude=request.current_location.longitude,
            password=request.password
        )

        if result.get('success', False):
            # 解锁成功后的处理逻辑
            
            # --- 令牌生成逻辑（安全关键） ---
            # 目标：重新生成用户的 JWT Token 或生成一个特殊的 "解锁访问令牌"。
            # 这里的实现选择了重新生成用户当前的 JWT Token，以便后续请求能够携带最新的权限。
            access_token = JWTHandler.generate_access_token(
                user_id=user.user_id,
                username=user.username,
                role=user.role,
                permissions=list(user.permissions) if user.permissions else []
            )

            # 构造成功响应数据
            response_data = UnlockCapsuleResponse(
                capsule_id=str(capsule_id),  # 确保为字符串类型
                unlocked_at=current_time,
                access_token=access_token # 返回新的 Token，客户端应更新其存储的 Token
            )

            return BaseResponse[UnlockCapsuleResponse].success(
                code=200,
                message="胶囊解锁成功",
                data=response_data
            )
        else:
            # Service 层返回失败：解锁条件未满足
            raise HTTPException(
                status_code=400,
                detail=result.get('message', '解锁失败')
            )

    except HTTPException:
        # 重新抛出已知的 HTTPException
        raise
    except Exception as e:
        # 捕获其他异常，进行数据库回滚，并返回 500 错误
        db.rollback()
        raise HTTPException(status_code=500, detail=f"解锁失败: {str(e)}")


## 📍 接口: 获取附近胶囊 (Get Nearby Capsules)
@router.get(
    "/nearby",
    response_model=BaseResponse[NearbyCapsulesResponse],
    summary="获取附近胶囊",
    description="获取用户当前位置附近可解锁的时光胶囊"
)
@api_logging(logger)
async def get_nearby_capsules(
    latitude: float = Query(..., description="用户当前纬度"),
    longitude: float = Query(..., description="用户当前经度"),
    radius_meters: int = Query(100, ge=10, le=10000, description="搜索半径（米）"), # 搜索半径查询参数
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """
    获取附近可解锁胶囊API：用于地图展示，发现用户周围满足位置条件的胶囊。
    """
    try:
        # 实例化服务层管理器
        unlock_manager = UnlockManager(db)

        # 调用 Service 层获取附近胶囊列表
        # Service 负责：1. 执行地理空间查询 (如 PostGIS 或 GeoHash)；2. 过滤权限 (Public 或 Friends)；3. 返回胶囊、距离和是否可解锁状态
        result = unlock_manager.get_nearby_capsules(
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters,
            user_id=user.user_id,
            page=page,
            limit=limit
        )

        if result.get('success', False):
            from app.model.unlock import NearbyCapsule, NearbyCapsuleLocation

            capsules_data = []

            # 遍历 Service 层返回的原始数据，生成简化的NearbyCapsule格式
            for capsule_item in result.get('capsules', []):
                # 从Service层结果中获取Domain对象
                domain: Capsule= capsule_item.get('domain')
                if not domain:
                    continue

                # 只有当胶囊有位置信息时才创建NearbyCapsule对象
                if domain.unlock_location and len(domain.unlock_location) >= 2:
                    # 创建简化的位置信息对象
                    location = NearbyCapsuleLocation(
                        latitude=domain.unlock_location[0],
                        longitude=domain.unlock_location[1],
                        distance=capsule_item.get('distance', 0)
                    )

                    # 检查用户是否已解锁该胶囊
                    has_unlocked = unlock_manager.has_user_unlocked_capsule(user.user_id, str(domain.capsule_id))

                    # 检查解锁条件
                    unlock_conditions = unlock_manager.check_unlock_conditions(
                        domain=domain,
                        user_id=user.user_id
                    )
                    can_unlock = unlock_conditions.get('can_unlock', False)

                    # 创建简化的NearbyCapsule对象（符合APIFox规范）
                    nearby_capsule = NearbyCapsule(
                        id=str(domain.capsule_id),
                        owner_id=int(domain.owner_id),
                        title=domain.title,
                        location=location,
                        visibility=domain.visibility.value,
                        unlock_condition_type=domain.unlock_condition_type,
                        is_unlocked=has_unlocked,
                        can_unlock=can_unlock,
                        creator_nickname=domain.title,  # 暂时使用title作为nickname，实际应从用户数据获取
                        created_at=domain.created_at
                    )

                    capsules_data.append(nearby_capsule)

            # 创建符合APIFox规范的响应
            response_data = NearbyCapsulesResponse(capsules=capsules_data)

            return BaseResponse[NearbyCapsulesResponse].success(
                code=200,
                message=f"成功获取{len(capsules_data)}个附近胶囊",
                data=response_data
            )
        else:
            # Service 层执行失败，返回 500
            raise HTTPException(
                status_code=500,
                detail=result.get('message', '获取附近胶囊失败')
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取附近胶囊时发生错误: {str(e)}"
        )


## 👁️ 接口: 获取胶囊解锁状态 (Get Unlock Status)
@router.get(
    "/{capsule_id}/status",
    response_model=BaseResponse[dict],
    summary="获取胶囊解锁状态",
    description="检查指定胶囊的解锁状态和解锁条件"
)
@api_logging(logger)
async def get_unlock_status(
    capsule_id: str = Path(..., description="胶囊ID"),
    user: AuthorizedUser = Depends(login_required),
    db: Session = Depends(get_db)
):
    """获取解锁状态：用于在详情页展示胶囊的解锁进度"""
    try:
        unlock_manager = UnlockManager(db)

        # 检查用户是否已解锁该胶囊 (硬状态)
        has_unlocked = unlock_manager.has_user_unlocked_capsule(user.user_id, capsule_id)

        # 获取胶囊领域模型对象 (Domain Object)
        capsule_domain = unlock_manager.repository.find_by_id(capsule_id)

        if not capsule_domain:
            raise HTTPException(status_code=404, detail="胶囊不存在")

        # 检查实时解锁条件 (软状态)
        # Service 负责：对比当前时间、好友关系等，返回满足和未满足的条件列表
        unlock_conditions = unlock_manager.check_unlock_conditions(
            domain=capsule_domain,
            user_id=user.user_id
        )

        # 构造响应数据
        response_data = {
            "capsule_id": capsule_id,
            "is_unlocked": has_unlocked, # 是否已解锁 (True/False)
            "can_unlock": unlock_conditions.get('can_unlock', False), # 是否现在可解锁 (Ture/False)
            "unlock_time": capsule_domain.unlock_time.isoformat() if capsule_domain.unlock_time else None, # 设定的解锁时间
            "failed_conditions": unlock_conditions.get('failed_conditions', []), # 未满足的条件列表
            "conditions_met": unlock_conditions.get('conditions_met', []) # 已满足的条件列表
        }

        return BaseResponse[dict].success(
            code=200,
            message="获取解锁状态成功",
            data=response_data
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取解锁状态失败: {str(e)}"
        )