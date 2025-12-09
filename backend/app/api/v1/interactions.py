"""
Interactions API interface
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import login_required
from app.model import (
    BaseResponse,
    LikeCapsuleResponse,
    AddCommentRequest,
    AddCommentResponse,
    CommentsListResponse,
    CollectCapsuleResponse,
    CommentsQuery
)
from app.services.interactions import InteractionService

router = APIRouter(prefix='/interactions', tags=['Interactions'])


@router.post("/{capsule_id}/like", response_model=BaseResponse[LikeCapsuleResponse])
async def like_capsule(
    capsule_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """点赞胶囊"""
    try:
        interaction_service = InteractionService(db)
        result = interaction_service.like_capsule(
            user_id=current_user.user_id,
            capsule_id=int(capsule_id)
        )

        return BaseResponse.success("点赞成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"点赞操作失败: {str(e)}"
        )


@router.delete("/{capsule_id}/like", response_model=BaseResponse[LikeCapsuleResponse])
async def unlike_capsule(
    capsule_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """取消点赞"""
    try:
        interaction_service = InteractionService(db)
        result = interaction_service.unlike_capsule(
            user_id=current_user.user_id,
            capsule_id=int(capsule_id)
        )

        return BaseResponse.success("取消点赞成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消点赞失败: {str(e)}"
        )


@router.post("/{capsule_id}/comments", response_model=BaseResponse[AddCommentResponse])
async def add_comment(
    capsule_id: str,
    request: AddCommentRequest,
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """添加评论"""
    try:
        interaction_service = InteractionService(db)
        result = interaction_service.add_comment(
            user_id=current_user.user_id,
            capsule_id=int(capsule_id),
            content=request.content,
            parent_id=int(request.parent_id) if request.parent_id and str(request.parent_id).strip() and str(request.parent_id) != "0" else None
        )

        return BaseResponse.success("添加评论成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加评论失败: {str(e)}"
        )


@router.get("/{capsule_id}/comments", response_model=BaseResponse[CommentsListResponse])
async def get_comments(
    capsule_id: str,
    query: CommentsQuery = Depends(),
    db: Session = Depends(get_db)
):
    """获取评论列表"""
    try:
        interaction_service = InteractionService(db)
        page = query.page or 1
        page_size = query.page_size or 20
        sort = query.sort or "latest"

        result = interaction_service.get_comments(
            capsule_id=int(capsule_id),
            page=page,
            page_size=page_size,
            sort=sort
        )

        return BaseResponse.success("获取评论成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评论失败: {str(e)}"
        )


@router.delete("/comments/{comment_id}", response_model=BaseResponse[None])
async def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """删除评论"""
    try:
        interaction_service = InteractionService(db)
        interaction_service.delete_comment(
            comment_id=int(comment_id),
            user_id=current_user.user_id
        )

        return BaseResponse.success("删除评论成功")
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除评论失败: {str(e)}"
        )


@router.post("/{capsule_id}/collect", response_model=BaseResponse[CollectCapsuleResponse])
async def collect_capsule(
    capsule_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """收藏胶囊"""
    try:
        interaction_service = InteractionService(db)
        result = interaction_service.collect_capsule(
            user_id=current_user.user_id,
            capsule_id=int(capsule_id)
        )

        message = "收藏成功" if result.is_collected else "取消收藏成功"
        return BaseResponse.success(message, data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"收藏操作失败: {str(e)}"
        )


@router.delete("/{capsule_id}/collect", response_model=BaseResponse[CollectCapsuleResponse])
async def uncollect_capsule(
    capsule_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """取消收藏"""
    try:
        interaction_service = InteractionService(db)
        result = interaction_service.uncollect_capsule(
            user_id=current_user.user_id,
            capsule_id=int(capsule_id)
        )

        return BaseResponse.success("取消收藏成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消收藏失败: {str(e)}"
        )
    
    