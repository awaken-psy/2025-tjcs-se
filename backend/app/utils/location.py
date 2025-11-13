from pydantic import BaseModel, Field
from typing import Optional

class Location(BaseModel):
    """地理位置"""
    latitude: float = Field(..., ge=-90, le=90, description="纬度")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    address: Optional[str] = Field(None, min_length=1, max_length=1024, description="详细地址")