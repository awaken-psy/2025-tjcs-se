from typing import Optional, Union

from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import math


class TimeCondition(ABC):
    """基于时间的解锁条件"""
    @abstractmethod
    def check(self, current_time: datetime) -> bool:
        return False


class UnlockDateCondition(BaseModel, TimeCondition):
    """指定时间之后解锁"""
    unlock_time: datetime = Field(..., description="解锁日期")
    end_time: Optional[datetime] = Field(None, description="结束日期")

    def check(self, current_time: datetime) -> bool:
        """检查是否满足时间条件"""
        # 检查是否达到解锁时间
        if current_time < self.unlock_time:
            return False

        # 检查是否超过结束时间（如果有）
        if self.end_time and current_time > self.end_time:
            return False

        return True

    def get_remaining_time(self, current_time: datetime) -> Optional[str]:
        """获取剩余时间"""
        if current_time < self.unlock_time:
            delta = self.unlock_time - current_time
            return f"{delta.days}天{delta.seconds // 3600}小时"
        return None


class PeriodType(str, Enum):
    """周期类型"""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class PeriodicUnlockCondition(BaseModel, TimeCondition):
    """在固定时间周期解锁"""
    base_time: datetime = Field(..., description="周期基准时间")
    period_type: PeriodType = Field(..., description="周期类型")
    time_of_duration: int = Field(..., ge=1, description="每次持续时间（单位：分钟）")
    period_count: Optional[int] = Field(None, ge=1, description="循环次数（无限循环则不设置）")

    def check(self, current_time: datetime) -> bool:
        """检查是否在周期解锁时间内"""
        # TODO: 实现具体的周期解锁逻辑
        # 这里简化实现，实际应该根据周期类型计算
        return False


class Location(BaseModel):
    """地理位置"""
    latitude: float = Field(..., ge=-90, le=90, description="纬度")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    address: Optional[str] = Field(None, min_length=1, max_length=1024, description="详细地址")


class LocationBasedCondition(BaseModel):
    """位置解锁条件"""
    trigger_latitude: float = Field(..., ge=-90, le=90, description="触发纬度")
    trigger_longitude: float = Field(..., ge=-180, le=180, description="触发经度")
    radius_meters: int = Field(100, ge=10, le=1000, description="触发半径（米）")

    def check(self, user_latitude: float, user_longitude: float) -> bool:
        """检查用户是否在触发范围内"""
        distance = self.calculate_distance(
            user_latitude, user_longitude,
            self.trigger_latitude, self.trigger_longitude
        )
        return distance <= self.radius_meters

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """计算两点之间的距离（米）使用Haversine公式"""
        # 将角度转换为弧度
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine公式
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # 地球半径（米）
        earth_radius = 6371000
        return c * earth_radius


TimeBasedCondition = Union[UnlockDateCondition, PeriodicUnlockCondition]


class UnlockConditions(BaseModel):
    """解锁条件组合"""
    time_based: Optional[TimeBasedCondition] = Field(None, description="时间条件")
    location_based: Optional[LocationBasedCondition] = Field(None, description="位置条件")

    def check_all_conditions(self, current_time: datetime, user_latitude: float, user_longitude: float) -> tuple[bool, list[str], list[str]]:
        """
        检查所有解锁条件

        Returns:
            tuple: (是否满足所有条件, 满足的条件列表, 未满足的条件列表)
        """
        met_conditions = []
        unmet_conditions = []

        # 检查时间条件
        if self.time_based:
            if self.time_based.check(current_time):
                met_conditions.append("time")
            else:
                unmet_conditions.append("time")

        # 检查位置条件
        if self.location_based:
            if self.location_based.check(user_latitude, user_longitude):
                met_conditions.append("location")
            else:
                unmet_conditions.append("location")

        # 如果没有设置任何条件，默认可以解锁
        if not self.time_based and not self.location_based:
            met_conditions.append("no_conditions")
            return True, met_conditions, unmet_conditions

        # 如果设置了条件，需要满足所有条件
        all_met = len(unmet_conditions) == 0
        return all_met, met_conditions, unmet_conditions

    def get_distance_to_trigger(self, user_latitude: float, user_longitude: float) -> Optional[float]:
        """获取到触发位置的距离（米）"""
        if self.location_based:
            return self.location_based.calculate_distance(
                user_latitude, user_longitude,
                self.location_based.trigger_latitude, self.location_based.trigger_longitude
            )
        return None