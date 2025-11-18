"""
胶囊上传相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Query, Path, Depends, UploadFile, File, Form
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from auth.dependencies import login_required
from domain.user import RegisteredUser
from model.capsule_model import BaseResponse, ErrorResponse, Location

from ..routes import upload_router as router


@router.post(
    "/media",
    response_model=BaseResponse,
    summary="上传媒体文件",
    description="单独上传媒体文件，返回文件ID供后续使用"
)
async def upload_media_files(
    files: List[UploadFile] = File(...),
    user: RegisteredUser = Depends(login_required)
):
    """上传媒体文件"""
    try:
        # TODO: 实现实际的文件上传和存储逻辑
        # 这里先返回模拟数据

        uploaded_files = []
        for file in files:
            # 模拟文件处理
            uploaded_files.append({
                "file_id": f"file_{datetime.now().timestamp()}",
                "file_name": file.filename,
                "file_type": file.content_type,
                "file_size": 0  # 实际应该获取文件大小
            })

        return BaseResponse(
            success=True,
            message=f"成功上传 {len(uploaded_files)} 个文件",
            data={"uploaded_files": uploaded_files}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传媒体文件时发生错误: {str(e)}"
        )


@router.post(
    "/complete",
    response_model=BaseResponse,
    summary="完成胶囊创建",
    description="使用已上传的文件完成胶囊创建"
)
async def complete_capsule_upload(
    title: str = Form(...),
    text_content: Optional[str] = Form(None),
    location_json: str = Form(...),  # JSON格式的location数据
    unlock_conditions_json: str = Form(...),  # JSON格式的unlock_conditions数据
    visibility_json: str = Form(...),  # JSON格式的visibility数据
    file_ids: Optional[str] = Form(None),  # 逗号分隔的文件ID列表
    user: RegisteredUser = Depends(login_required)
):
    """完成胶囊创建"""
    try:
        # TODO: 实现实际的胶囊创建逻辑
        # 这里先返回模拟数据

        # 解析JSON数据（实际实现时需要proper JSON parsing）
        # location = json.loads(location_json)
        # unlock_conditions = json.loads(unlock_conditions_json)
        # visibility = json.loads(visibility_json)
        # file_id_list = file_ids.split(',') if file_ids else []

        return BaseResponse(
            success=True,
            message="胶囊创建成功",
            data={"capsule_id": f"caps_{datetime.now().timestamp()}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"完成胶囊创建时发生错误: {str(e)}"
        )


@router.delete(
    "/media/{file_id}",
    response_model=BaseResponse,
    summary="删除已上传的媒体文件",
    description="删除之前上传但未使用的媒体文件"
)
async def delete_uploaded_media(
    file_id: str = Path(..., description="文件ID"),
    user: RegisteredUser = Depends(login_required)
):
    """删除已上传的媒体文件"""
    try:
        # TODO: 实现实际的文件删除逻辑
        # 这里先返回模拟数据

        return BaseResponse(
            success=True,
            message="媒体文件删除成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除媒体文件时发生错误: {str(e)}"
        )


@router.get(
    "/media/preview/{file_id}",
    response_model=BaseResponse,
    summary="预览媒体文件",
    description="获取已上传媒体文件的预览URL或缩略图"
)
async def get_media_preview(
    file_id: str = Path(..., description="文件ID"),
    user: RegisteredUser = Depends(login_required)
):
    """预览媒体文件"""
    try:
        # TODO: 实现实际的预览生成逻辑
        # 这里先返回模拟数据

        return BaseResponse(
            success=True,
            message="获取媒体预览成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取媒体预览时发生错误: {str(e)}"
        )