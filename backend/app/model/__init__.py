"""
Pydantic models for the Time Capsule API
"""

# Base models
from .base import *
# Authentication models
from .auth import *
# Capsule models
from .capsule import *
# Unlock models
from .unlock import *
# Browse models
from .browse import *
# Interaction models
from .interaction import *
# User models
from .user import *
# Friend models
from .friend import *
# File models
from .file import *
# Admin models
from .admin import *

__all__ = [
    # Base
    "BaseResponse", "Pagination",

    # Auth
    "UserRegisterRequest", "UserLoginRequest", "UserAuthResponse","UserRefreshTokenResponse","SendCodeRequest",

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