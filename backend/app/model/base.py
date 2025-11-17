"""
Base Pydantic models for the Time Capsule API
"""
from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int
    message: str
    data: Optional[T] = None


class Pagination(BaseModel):
    """分页信息模型"""
    page: int
    page_size: int
    total: int
    total_pages: int