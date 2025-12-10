"""
Friends API interface

该文件定义了所有与用户好友关系管理相关的 API 接口 (社交功能)。
它实现了用户搜索、好友请求的发送与处理，以及好友列表的管理。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

# 导入依赖
from app.database.database import get_db            # 数据库 Session 依赖
from app.auth.dependencies import login_required    # 认证依赖，获取当前登录用户

# 导入数据模型 (Pydantic DTOs)
from app.model import (
    BaseResponse,               # 标准化的 API 响应模型
    UserSearchResponse,         # 用户搜索结果的响应模型 (包含分页和用户列表)
    FriendRequestsResponse,     # 好友请求列表的响应模型
    FriendsListResponse,        # 好友列表的响应模型
    SendFriendRequest,          # 发送好友请求的请求体模型 (目标用户ID)
    HandleFriendRequest,        # 处理好友请求的请求体模型 (接受/拒绝)
    UserSearchQuery,            # 用户搜索的查询参数模型 (包含关键词、分页)
    FriendRequestsQuery         # 获取好友请求的查询参数模型 (包含类型、状态、分页)
)
from app.services.friends import FriendService      # 核心好友业务逻辑服务

# 初始化 FastAPI 路由
router = APIRouter(prefix='/friends', tags=['Friends'])


## 🔎 搜索用户 (Search Users)
@router.get("/search", response_model=BaseResponse[UserSearchResponse])
async def search_users(
    query: UserSearchQuery = Depends(),             # 依赖注入：获取查询参数 (如 q, page, page_size)
    db: Session = Depends(get_db),
    current_user = Depends(login_required)          # 依赖注入：确保用户已登录，并获取用户信息
):
    """搜索用户：通过关键词 (昵称、学号等) 搜索其他用户，并排除自己"""
    try:
        friend_service = FriendService(db)
        page = query.page or 1
        page_size = query.page_size or 20

        # 调用 Service 层执行搜索逻辑
        result = friend_service.search_users(
            current_user_id=current_user.user_id,   # 排除当前用户自己
            query=query.q,                          # 搜索关键词
            page=page,
            page_size=page_size
        )

        return BaseResponse.success("搜索成功", data=result)
    except Exception as e:
        # 捕获并返回 500 服务器错误
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索用户失败: {str(e)}"
        )


## 💌 发送好友请求 (Send Friend Request)
@router.post("/requests", response_model=BaseResponse[None])
async def send_friend_request(
    request: SendFriendRequest,                     # 请求体：目标用户的 ID
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """发送好友请求：向指定用户发送好友申请"""
    try:
        friend_service = FriendService(db)
        # 调用 Service 层执行发送请求的业务逻辑
        # Service 负责：1. 检查目标用户是否存在；2. 检查是否已经是好友；3. 检查是否已存在未处理的请求；4. 创建请求记录
        friend_service.send_friend_request(
            requester_id=current_user.user_id,      # 发送者 ID
            target_user_id=request.target_user_id   # 接收者 ID
        )

        return BaseResponse.success("好友请求发送成功")
    except ValueError as e:
        # 捕获 Service 层抛出的业务逻辑错误 (如 "已经是好友", "用户不存在" 等)
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送好友请求失败: {str(e)}"
        )


## 📥 获取好友请求列表 (Get Friend Requests)
@router.get("/requests", response_model=BaseResponse[FriendRequestsResponse])
async def get_friend_requests(
    query: FriendRequestsQuery = Depends(),         # 查询参数：控制请求类型和状态 (如收到的/发出的，待处理的/已接受的)
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """获取好友请求列表：获取当前用户收到或发出的所有好友请求"""
    try:
        friend_service = FriendService(db)
        page = query.page or 1
        page_size = query.page_size or 20

        # 调用 Service 层获取请求列表
        result = friend_service.get_friend_requests(
            current_user_id=current_user.user_id,
            request_type=query.type,                # 请求类型 (如 'received' 或 'sent')
            page=page,
            page_size=page_size,
            status=query.status                     # 请求状态 (如 'pending', 'accepted', 'rejected')
        )

        return BaseResponse.success("获取好友请求成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取好友请求失败: {str(e)}"
        )


## ✅ 拒绝/接受好友请求 (Handle Friend Request)
@router.post("/requests/{request_id}", response_model=BaseResponse[None])
async def handle_friend_request(
    request_id: str,                                # 路径参数：待处理的请求 ID
    request: HandleFriendRequest,                   # 请求体：处理动作 ('accept' 或 'reject')
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """处理好友请求：接受或拒绝收到的好友请求"""
    try:
        friend_service = FriendService(db)
        # 调用 Service 层执行处理逻辑
        # Service 负责：1. 验证该请求是否由当前用户收到；2. 更新请求状态；3. 如果接受，在好友表中创建双向好友关系
        friend_service.handle_friend_request(
            current_user_id=current_user.user_id,
            request_id=int(request_id),
            action=request.action                   # 动作 ('accept' 或 'reject')
        )

        message = "接受好友请求成功" if request.action == "accept" else "拒绝好友请求成功"

        return BaseResponse.success(message)
    except ValueError as e:
        # 捕获业务错误 (如 "请求不存在", "无权操作" 等)
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理好友请求失败: {str(e)}"
        )


## 🧑‍🤝‍🧑 获取好友列表 (Get Friends List)
@router.get("/", response_model=BaseResponse[FriendsListResponse])
async def get_friends_list(
    page: int = 1,                                  # 查询参数：页码
    page_size: int = 20,                            # 查询参数：每页大小
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """获取好友列表：分页获取当前用户的所有好友"""
    try:
        friend_service = FriendService(db)
        # 调用 Service 层获取已建立的好友关系列表
        result = friend_service.get_friends_list(
            current_user_id=current_user.user_id,
            page=page,
            page_size=page_size
        )

        return BaseResponse.success("获取好友列表成功", data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取好友列表失败: {str(e)}"
        )


## 💔 删除好友 (Remove Friend)
@router.delete("/{friend_id}", response_model=BaseResponse[None])
async def remove_friend(
    friend_id: int,                                 # 路径参数：待删除的好友 ID
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """删除好友：解除与指定用户的好友关系"""
    try:
        friend_service = FriendService(db)
        # 调用 Service 层执行删除好友逻辑
        # Service 负责：1. 检查是否存在好友关系；2. 删除好友表中的双向记录
        friend_service.remove_friend(
            current_user_id=current_user.user_id,
            friend_id=friend_id
        )

        return BaseResponse.success("删除好友成功")
    except ValueError as e:
        # 捕获业务错误 (如 "该用户不是你的好友")
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除好友失败: {str(e)}"
        )