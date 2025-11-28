from pydantic import BaseModel, Field
from typing import Optional
import math

class Location(BaseModel):
    """地理位置"""
    latitude: float = Field(..., ge=-90, le=90, description="纬度")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    address: Optional[str] = Field(None, min_length=1, max_length=1024, description="详细地址")


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    使用Haversine公式计算两个地理坐标之间的距离（单位：米）

    Args:
        lat1, lon1: 第一个点的纬度和经度
        lat2, lon2: 第二个点的纬度和经度

    Returns:
        两点之间的距离（米）
    """
    # 地球半径（米）
    R = 6371000

    # 将纬度和经度转换为弧度
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # 计算差值
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine公式
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # 计算距离
    distance = R * c

    return distance


def is_within_radius(lat1: float, lon1: float, lat2: float, lon2: float, radius_meters: float) -> bool:
    """
    检查两个地理坐标是否在指定半径内

    Args:
        lat1, lon1: 第一个点的纬度和经度
        lat2, lon2: 第二个点的纬度和经度
        radius_meters: 半径（米）

    Returns:
        如果在半径内返回True，否则返回False
    """
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_meters


def find_nearby_locations(user_lat: float, user_lon: float, locations: list, radius_meters: float) -> list:
    """
    找出用户附近的位置

    Args:
        user_lat: 用户纬度
        user_lon: 用户经度
        locations: 位置列表，每个位置应包含latitude和longitude字段
        radius_meters: 搜索半径（米）

    Returns:
        附近的位置列表，每个位置包含原始数据和distance字段
    """
    nearby_locations = []

    for location in locations:
        lat = location.get('latitude')
        lon = location.get('longitude')

        if lat is not None and lon is not None:
            distance = calculate_distance(user_lat, user_lon, lat, lon)

            if distance <= radius_meters:
                # 添加距离信息
                location_with_distance = location.copy()
                location_with_distance['distance'] = distance
                nearby_locations.append(location_with_distance)

    # 按距离排序
    nearby_locations.sort(key=lambda x: x['distance'])

    return nearby_locations