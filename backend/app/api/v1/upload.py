"""
Upload API interface
"""
from fastapi import APIRouter, UploadFile, File

from app.model import (
    BaseResponse,
    FileUploadResponse
)

router = APIRouter(prefix='/upload', tags=['Upload'])


@router.post("/file", response_model=BaseResponse[FileUploadResponse])
async def upload_file(
    file: UploadFile = File(...)
):
    """上传文件"""
    pass


@router.post("/image", response_model=BaseResponse[FileUploadResponse])
async def upload_image(
    file: UploadFile = File(...)
):
    """上传图片"""
    pass


@router.post("/audio", response_model=BaseResponse[FileUploadResponse])
async def upload_audio(
    file: UploadFile = File(...)
):
    """上传音频"""
    pass


@router.delete("/file/{file_id}", response_model=BaseResponse[None])
async def delete_file(
    file_id: str
):
    """删除文件"""
    pass