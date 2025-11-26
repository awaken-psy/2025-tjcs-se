"""
Interactions API interface
"""
from fastapi import APIRouter, Depends

from app.model import (
    BaseResponse,
    LikeCapsuleResponse,
    AddCommentRequest,
    AddCommentResponse,
    CommentsListResponse,
    CollectCapsuleResponse,
    CommentsQuery
)

router = APIRouter(prefix='/interactions', tags=['Interactions'])


@router.post("/{capsule_id}/like", response_model=BaseResponse[LikeCapsuleResponse])
async def like_capsule(
    capsule_id: str
):
    """点赞胶囊"""
    pass


@router.delete("/{capsule_id}/like", response_model=BaseResponse[LikeCapsuleResponse])
async def unlike_capsule(
    capsule_id: str
):
    """取消点赞"""
    pass


@router.post("/{capsule_id}/comments", response_model=BaseResponse[AddCommentResponse])
async def add_comment(
    capsule_id: str,
    request: AddCommentRequest
):
    """添加评论"""
    pass


@router.get("/{capsule_id}/comments", response_model=BaseResponse[CommentsListResponse])
async def get_comments(
    capsule_id: str,
    query: CommentsQuery = Depends()
):
    """获取评论列表"""
    pass


@router.delete("/comments/{comment_id}", response_model=BaseResponse[None])
async def delete_comment(
    comment_id: str
):
    """删除评论"""
    pass


@router.post("/{capsule_id}/collect", response_model=BaseResponse[CollectCapsuleResponse])
async def collect_capsule(
    capsule_id: str
):
    """收藏胶囊"""
    pass


@router.delete("/{capsule_id}/collect", response_model=BaseResponse[CollectCapsuleResponse])
async def uncollect_capsule(
    capsule_id: str
):
    """取消收藏"""
    pass