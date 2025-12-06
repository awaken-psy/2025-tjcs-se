from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.repositories.friend_repository import FriendRepository
from app.domain.friend import (
    User, FriendRelation, FriendRequest, FriendStatus,
    FriendRequestAction, FriendRequestType
)
from app.model.friend import (
    UserSearchResponse, FriendRequestsResponse, FriendsListResponse,
    SearchedUser, FriendRequestItem, FriendItem
)


class FriendService:
    """好友相关业务逻辑"""

    def __init__(self, db: Session):
        self.friend_repo = FriendRepository(db)

    def search_users(self, current_user_id: int, query: str, page: int = 1, page_size: int = 20) -> UserSearchResponse:
        """搜索用户"""
        if not query or len(query.strip()) < 2:
            return UserSearchResponse(users=[])

        # 搜索用户
        users = self.friend_repo.search_users(query.strip(), page, page_size)

        # 为每个用户检查好友关系状态
        searched_users = []
        for user in users:
            # 跳过自己
            if user.user_id == current_user_id:
                continue

            # 获取与当前用户的关系状态
            friend_relation = self.friend_repo.get_friend_relation(current_user_id, user.user_id)

            if friend_relation:
                searched_user = friend_relation.to_api_searched_user(user)
            else:
                # 无关系
                searched_user = SearchedUser(
                    user_id=user.user_id,
                    nickname=user.nickname,
                    is_friend=False,
                    friend_status=FriendStatus.NONE.value,
                    avatar=user.avatar_url
                )

            searched_users.append(searched_user)

        return UserSearchResponse(users=searched_users)

    def send_friend_request(self, requester_id: int, target_user_id: int) -> None:
        """发送好友请求"""
        # 检查目标用户是否存在
        target_user = self.friend_repo.find_user_by_id(target_user_id)
        if not target_user:
            raise ValueError(f"用户 {target_user_id} 不存在")

        # 不能添加自己为好友
        if requester_id == target_user_id:
            raise ValueError("不能添加自己为好友")

        # 检查是否已经是好友或已有请求
        existing_relation = self.friend_repo.get_friend_relation(requester_id, target_user_id)
        if existing_relation:
            if existing_relation.status == FriendStatus.ACCEPTED:
                raise ValueError("已经是好友")
            elif existing_relation.status == FriendStatus.PENDING:
                # 如果已有待处理请求，更新为新的待处理状态
                return
            else:
                # 其他状态（拒绝、拉黑），重新发送请求
                friend_relation = self.friend_repo.send_friend_request(requester_id, target_user_id)
                return

        # 发送好友请求
        self.friend_repo.send_friend_request(requester_id, target_user_id)

    def get_friend_requests(self, current_user_id: int, request_type: str,
                           page: int = 1, page_size: int = 20,
                           status: Optional[str] = None) -> FriendRequestsResponse:
        """获取好友请求列表"""
        # 验证请求类型
        if request_type not in [FriendRequestType.RECEIVED.value, FriendRequestType.SENT.value]:
            raise ValueError(f"无效的请求类型: {request_type}")

        # 获取好友请求
        friend_requests = self.friend_repo.get_friend_requests(current_user_id, request_type, page, page_size)

        # 过滤状态（如果指定）
        if status:
            friend_requests = [req for req in friend_requests if req.status.value == status]

        # 转换为API模型
        request_items = []
        for friend_request in friend_requests:
            # 获取请求者或被请求者的用户信息
            if request_type == FriendRequestType.RECEIVED.value:
                user_id = friend_request.requester_id  # 收到的请求，显示请求者信息
                is_received = True
            else:
                user_id = friend_request.addressee_id  # 发送的请求，显示被请求者信息
                is_received = False

            user = self.friend_repo.find_user_by_id(user_id)
            if user:
                request_item = friend_request.to_api_friend_request_item(user, is_received)
                request_items.append(request_item)

        return FriendRequestsResponse(requests=request_items)

    def handle_friend_request(self, current_user_id: int, request_id: int, action: str) -> None:
        """处理好友请求"""
        # 验证操作类型
        if action not in [FriendRequestAction.ACCEPT.value, FriendRequestAction.REJECT.value]:
            raise ValueError(f"无效的操作: {action}")

        # 获取好友请求
        friend_requests = self.friend_repo.get_friend_requests(current_user_id, "received", 1, 1000)

        # 在收到的请求中查找对应的请求
        target_request = None
        for req in friend_requests:
            if req.id == request_id:
                target_request = req
                break

        if not target_request:
            raise ValueError(f"好友请求 {request_id} 不存在")

        # 验证被请求者是否是当前用户
        if target_request.addressee_id != current_user_id:
            raise ValueError("无权限处理此好友请求")

        # 处理请求
        updated_relation = self.friend_repo.handle_friend_request(request_id, action)
        if not updated_relation:
            raise ValueError("处理好友请求失败")

        # 如果接受好友请求，需要创建双向好友关系
        if action == FriendRequestAction.ACCEPT.value:
            # 检查是否需要创建反向关系
            reverse_relation = self.friend_repo.get_friend_relation(
                target_request.addressee_id, target_request.requester_id
            )
            if not reverse_relation:
                # 创建反向的好友关系
                self.friend_repo.send_friend_request(
                    target_request.addressee_id, target_request.requester_id
                )
                # 立即将反向关系设置为已接受
                reverse_requests = self.friend_repo.get_friend_requests(
                    target_request.addressee_id, "sent", 1, 1000
                )
                for req in reverse_requests:
                    if req.addressee_id == target_request.requester_id:
                        self.friend_repo.handle_friend_request(req.id, "accept")
                        break

    def get_friends_list(self, current_user_id: int, page: int = 1, page_size: int = 20) -> FriendsListResponse:
        """获取好友列表"""
        # 获取好友关系
        friend_relations = self.friend_repo.get_friends_list(current_user_id, page, page_size)

        # 转换为API模型
        friends = []
        for relation in friend_relations:
            # 确定好友ID（不是当前用户的那个）
            friend_id = relation.friend_id if relation.user_id == current_user_id else relation.user_id

            # 获取好友用户信息
            friend_user = self.friend_repo.find_user_by_id(friend_id)
            if friend_user:
                friend_item = relation.to_api_friend_item(friend_user)
                friends.append(friend_item)

        return FriendsListResponse(friends=friends)

    def remove_friend(self, current_user_id: int, friend_id: int) -> None:
        """删除好友"""
        # 检查好友是否存在
        friend_user = self.friend_repo.find_user_by_id(friend_id)
        if not friend_user:
            raise ValueError(f"用户 {friend_id} 不存在")

        # 检查是否是好友关系
        friend_relation = self.friend_repo.get_friend_relation(current_user_id, friend_id)
        if not friend_relation or friend_relation.status != FriendStatus.ACCEPTED:
            raise ValueError("不是好友关系")

        # 删除好友关系
        success = self.friend_repo.remove_friend(current_user_id, friend_id)
        if not success:
            raise ValueError("删除好友失败")

    def are_friends(self, user_id: int, friend_id: int) -> bool:
        """检查两个用户是否是好友"""
        friend_relation = self.friend_repo.get_friend_relation(user_id, friend_id)
        return friend_relation is not None and friend_relation.status == FriendStatus.ACCEPTED

    def get_friends_count(self, user_id: int) -> int:
        """获取用户好友数量"""
        return self.friend_repo.get_user_friends_count(user_id)