"""
Capsule browsing related Pydantic models
"""
from typing import List, Dict, Any
from pydantic import BaseModel

from .capsule import CapsuleBasic


class BrowseCapsulesQuery(BaseModel):
    """浏览胶囊查询参数模型"""
    mode: str  # "map", "timeline", "tags"
    tags: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    page: int | None = None
    page_size: int | None = None


class TimelineGroup(BaseModel):
    """按时间分组模型"""
    group_key: str
    capsules: List[CapsuleBasic]


class BrowseCapsulesResponse(BaseModel):
    """浏览胶囊响应模型"""
    mode: str
    capsules: List[CapsuleBasic] | None = None
    timeline_groups: Dict[str, List[CapsuleBasic]] | None = None