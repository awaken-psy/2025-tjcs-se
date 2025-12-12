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

    @classmethod
    def success(cls, message: str = "success", data: Optional[T] = None, code: int = 200) -> 'BaseResponse[T]':
        """成功响应"""
        return cls(code=code, message=message, data=data)

    @classmethod
    def fail(cls, message: str = "fail", data: Optional[T] = None, code: int = 400) -> 'BaseResponse[T]':
        """失败响应"""
        return cls(code=code, message=message, data=data)


class Pagination(BaseModel):
    """分页信息模型"""
    page: int
    page_size: int
    total: int
    total_pages: int