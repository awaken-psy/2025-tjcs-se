"""
Unlock API interface - 解锁功能实现
"""
from fastapi import APIRouter, Depends, Path, Query
from typing import Optional
from datetime import datetime
import secrets

# 导入解锁相关的模型
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from model.unlock import (
        CurrentLocation,
        UnlockCapsuleRequest,
        UnlockCapsuleResponse,
        NearbyCapsuleLocation,
        NearbyCapsule,
        NearbyCapsulesResponse,
        NearbyCapsulesQuery
    )
except ImportError:
    # 如果导入失败，使用简化模型
    class CurrentLocation:
        latitude: float
        longitude: float

    class UnlockCapsuleRequest:
        current_location: CurrentLocation

try:
    from services.unlock_manager import UnlockManager
except ImportError:
    # 如果导入失败，使用模拟服务
    class UnlockManager:
        def check_unlockable_capsules(self, *args, **kwargs):
            return {
                'success': True,
                'message': '模拟数据',
                'unlockable_capsules': []
            }

        def unlock_capsule(self, *args, **kwargs):
            return {
                'success': True,
                'message': '模拟解锁成功',
                'unlocked_at': datetime.now().isoformat()
            }

# 简单的认证依赖
def login_required():
    class MockUser:
        def __init__(self):
            self.id = 1
            self.username = "test_user"
    return MockUser()

# 响应模型 - 匹配TypeScript接口规范
class APIResponse(BaseModel):
    """基础API响应模型"""
    code: int
    message: str
    data: Optional[dict] = None

router = APIRouter(prefix='/unlock', tags=['Unlock'])


@router.post("/{capsule_id}", response_model=APIResponse)
async def unlock_capsule(
    capsule_id: str = Path(..., description="胶囊ID"),
    request: UnlockCapsuleRequest = ...,
    user = Depends(login_required)
):
    """
    解锁胶囊API

    请求格式: { "current_location": { "latitude": 39.9042, "longitude": 116.4074 } }
    响应格式: {
      "code": 200,
      "data": {
        "access_token": "token_abc123...",
        "capsule_id": "abc123",
        "unlocked_at": "2024-11-26T10:30:00Z"
      },
      "message": "解锁成功"
    }
    """
    try:
        current_time = datetime.now()

        # 调用服务层进行解锁
        unlock_manager = UnlockManager()

        # 解锁胶囊
        result = unlock_manager.unlock_capsule(
            user_id=user.id,
            capsule_id=int(capsule_id) if capsule_id.isdigit() else hash(capsule_id) % 10000,
            user_latitude=request.current_location.latitude,
            user_longitude=request.current_location.longitude,
            current_time=current_time
        )

        if result.get('success', False):
            # 生成访问令牌
            access_token = f"unlock_{secrets.token_hex(16)}_{capsule_id}_{int(current_time.timestamp())}"

            return APIResponse(
                code=200,
                message="胶囊解锁成功",
                data={
                    "access_token": access_token,
                    "capsule_id": capsule_id,
                    "unlocked_at": result.get('unlocked_at', current_time.isoformat())
                }
            )
        else:
            return APIResponse(
                code=400,
                message=result.get('message', '解锁失败'),
                data={
                    "access_token": "",
                    "capsule_id": capsule_id,
                    "unlocked_at": current_time.isoformat()
                }
            )

    except Exception as e:
        return APIResponse(
            code=500,
            message=f"解锁失败: {str(e)}",
            data=None
        )


@router.get("/nearby")
async def get_nearby_capsules(
    latitude: float = Query(..., description="用户当前纬度"),
    longitude: float = Query(..., description="用户当前经度"),
    radius_meters: int = Query(1000, ge=10, le=10000, description="搜索半径（米）"),
    user = Depends(login_required)
):
    """
    获取附近可解锁胶囊API

    响应格式: {
      "code": 200,
      "data": {
        "capsules": [
          {
            "can_unlock": true,
            "created_at": "2024-10-25T14:30:00Z",
            "creator_nickname": "张三",
            "id": "caps_002",
            "is_unlocked": false,
            "location": {
              "distance": 320.8,
              "latitude": 39.9052,
              "longitude": 116.4084
            },
            "title": "足球比赛回忆",
            "visibility": "friends"
          }
        ]
      },
      "message": "成功获取1个附近胶囊"
    }
    """
    try:
        # 调用服务层获取附近可解锁胶囊
        unlock_manager = UnlockManager()

        result = unlock_manager.check_unlockable_capsules(
            user_id=user.id,
            user_latitude=latitude,
            user_longitude=longitude,
            max_distance_meters=radius_meters
        )

        if result.get('success', False):
            # 转换服务层数据为API响应格式
            capsules_data = []

            for capsule in result.get('unlockable_capsules', []):
                # 转换为API需要的格式
                capsule_api_data = {
                    "can_unlock": True,
                    "created_at": capsule.get('created_at', datetime.now()),
                    "creator_nickname": "用户",  # 服务层数据中没有此字段，使用默认值
                    "id": str(capsule.get('capsule_id', '')),
                    "is_unlocked": False,
                    "location": {
                        "distance": capsule.get('distance', 0),
                        "latitude": capsule['position']['latitude'],
                        "longitude": capsule['position']['longitude']
                    },
                    "title": capsule.get('title', '未知胶囊'),
                    "visibility": capsule.get('visibility', 'public')
                }
                capsules_data.append(capsule_api_data)

            return APIResponse(
                code=200,
                message=f"成功获取{len(capsules_data)}个附近胶囊",
                data={
                    "capsules": capsules_data
                }
            )
        else:
            return APIResponse(
                code=500,
                message=result.get('message', '获取附近胶囊失败'),
                data={"capsules": []}
            )

    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取附近胶囊时发生错误: {str(e)}",
            data={"capsules": []}
        )


@router.get("/{capsule_id}/status")
async def get_unlock_status(
    capsule_id: str = Path(..., description="胶囊ID"),
    user = Depends(login_required)
):
    """获取解锁状态"""
    try:
        # 简化的解锁状态检查
        return APIResponse(
            code=200,
            message="获取解锁状态成功",
            data={
                "capsule_id": capsule_id,
                "is_unlocked": False,
                "can_unlock": True,  # 简化逻辑
                "unlock_time": None
            }
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取解锁状态失败: {str(e)}",
            data=None
        )