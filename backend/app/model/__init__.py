"""
Pydantic models for the Time Capsule API
"""

# Base models
from .base import BaseResponse, Pagination

# Authentication models
from .auth import UserRegisterRequest, UserLoginRequest, UserAuthResponse

# Capsule models
from .capsule import (
    Location,
    UnlockConditions,
    MediaFile,
    Creator,
    CapsuleStats,
    CapsuleBasic,
    CapsuleDetail,
    CapsuleCreateRequest,
    CapsuleUpdateRequest,
    CapsuleDraftRequest,
    CapsuleCreateResponse,
    CapsuleUpdateResponse,
    CapsuleDraftResponse,
    CapsuleListResponse,
    MyCapsulesQuery,
)

# Unlock models
from .unlock import (
    CurrentLocation,
    UnlockCapsuleRequest,
    UnlockCapsuleResponse,
    NearbyCapsule,
    NearbyCapsulesResponse,
    NearbyCapsulesQuery,
)

# Browse models
from .browse import (
    BrowseCapsulesQuery,
    TimelineGroup,
    BrowseCapsulesResponse,
)

# Interaction models
from .interaction import (
    CommentUser,
    CommentItem,
    LikeCapsuleResponse,
    AddCommentRequest,
    AddCommentResponse,
    CommentsListResponse,
    CollectCapsuleResponse,
    CommentsQuery,
)

# User models
from .user import (
    UserStats,
    UserProfile,
    UserHistoryItem,
    UserHistoryResponse,
    UpdateUserRequest,
    UserHistoryQuery,
)

# Friend models
from .friend import (
    SearchedUser,
    FriendRequestUser,
    FriendRequestItem,
    FriendItem,
    UserSearchResponse,
    FriendRequestsResponse,
    FriendsListResponse,
    SendFriendRequest,
    HandleFriendRequest,
    UserSearchQuery,
    FriendRequestsQuery,
)

# File models
from .file import (
    FileUploadResponse,
    ReportRequest,
)

# Admin models
from .admin import (
    PendingCapsule,
    ReportItem,
    ReviewCapsuleRequest,
    PendingCapsulesQuery,
    ReportsQuery,
    PendingCapsulesResponse,
    ReportsResponse,
)

__all__ = [
    # Base
    "BaseResponse", "Pagination",

    # Auth
    "UserRegisterRequest", "UserLoginRequest", "UserAuthResponse",

    # Capsule
    "Location", "UnlockConditions", "MediaFile", "Creator", "CapsuleStats",
    "CapsuleBasic", "CapsuleDetail", "CapsuleCreateRequest", "CapsuleUpdateRequest",
    "CapsuleDraftRequest", "CapsuleCreateResponse", "CapsuleUpdateResponse",
    "CapsuleDraftResponse", "CapsuleListResponse", "MyCapsulesQuery",

    # Unlock
    "CurrentLocation", "UnlockCapsuleRequest", "UnlockCapsuleResponse",
    "NearbyCapsule", "NearbyCapsulesResponse", "NearbyCapsulesQuery",

    # Browse
    "BrowseCapsulesQuery", "TimelineGroup", "BrowseCapsulesResponse",

    # Interaction
    "CommentUser", "CommentItem", "LikeCapsuleResponse", "AddCommentRequest",
    "AddCommentResponse", "CommentsListResponse", "CollectCapsuleResponse",
    "CommentsQuery",

    # User
    "UserStats", "UserProfile", "UserHistoryItem", "UserHistoryResponse",
    "UpdateUserRequest", "UserHistoryQuery",

    # Friend
    "SearchedUser", "FriendRequestUser", "FriendRequestItem", "FriendItem",
    "UserSearchResponse", "FriendRequestsResponse", "FriendsListResponse",
    "SendFriendRequest", "HandleFriendRequest", "UserSearchQuery", "FriendRequestsQuery",

    # File
    "FileUploadResponse", "ReportRequest",

    # Admin
    "PendingCapsule", "ReportItem", "ReviewCapsuleRequest", "PendingCapsulesQuery",
    "ReportsQuery", "PendingCapsulesResponse", "ReportsResponse",
]