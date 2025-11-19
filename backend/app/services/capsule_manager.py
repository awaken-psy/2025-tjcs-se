try:
    from database.orm.capsule import Capsule as CapsuleDB
    from database.orm.user import User as UserDB
    from database.orm.unlock_condition import UnlockCondition as UnlockConditionDB
    from database.orm.unlock_record import UnlockRecord as UnlockRecordDB
    from database.orm.config import get_db
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"Database modules not available: {e}")
    DATABASE_AVAILABLE = False
from datetime import datetime
from typing import List, Dict, Any, Optional
import math
from utils.location import calculate_distance, is_within_radius


class CapsuleManager:
    def __init__(self):
        if DATABASE_AVAILABLE:
            self.db = next(get_db())  # 获取数据库会话
        else:
            self.db = None

    def __del__(self):
        """析构函数，确保数据库会话被正确关闭"""
        if hasattr(self, 'db') and self.db:
            self.db.close()

    def can_unlock_capsule(self, capsule_id: int, user_id: int, user_lat: float, user_lon: float, current_time: datetime = None) -> Dict[str, Any]:
        """
        检查用户是否可以解锁指定胶囊

        Args:
            capsule_id: 胶囊ID
            user_id: 用户ID
            user_lat: 用户当前纬度
            user_lon: 用户当前经度
            current_time: 当前时间，如果不提供则使用系统时间

        Returns:
            包含解锁条件和结果的字典
        """
        if current_time is None:
            current_time = datetime.now()

        # 查询胶囊和解锁条件
        capsule = self.db.query(CapsuleDB).filter(CapsuleDB.id == capsule_id).first()
        if not capsule:
            return {"can_unlock": False, "reason": "胶囊不存在"}

        unlock_condition = self.db.query(UnlockConditionDB).filter(UnlockConditionDB.capsule_id == capsule_id).first()
        if not unlock_condition:
            return {"can_unlock": False, "reason": "未设置解锁条件"}

        # 检查是否已经解锁过
        existing_unlock = self.db.query(UnlockRecordDB).filter(
            UnlockRecordDB.capsule_id == capsule_id,
            UnlockRecordDB.user_id == user_id
        ).first()

        if existing_unlock:
            return {"can_unlock": False, "reason": "已经解锁过此胶囊"}

        # 检查各种解锁条件
        time_met = False
        location_met = False

        conditions_met = []
        conditions_not_met = []

        # 时间条件检查
        if unlock_condition.condition_type in ["time", "combined"]:
            if unlock_condition.unlock_time and current_time >= unlock_condition.unlock_time:
                time_met = True
                conditions_met.append("时间条件满足")
            else:
                if unlock_condition.unlock_time:
                    remaining_time = unlock_condition.unlock_time - current_time
                    conditions_not_met.append(f"时间条件未满足（剩余{remaining_time.total_seconds():.0f}秒）")
                else:
                    conditions_not_met.append("未设置时间条件")

        # 位置条件检查
        if unlock_condition.condition_type in ["location", "combined"]:
            if (unlock_condition.trigger_latitude and unlock_condition.trigger_longitude and
                is_within_radius(user_lat, user_lon,
                               unlock_condition.trigger_latitude,
                               unlock_condition.trigger_longitude,
                               unlock_condition.radius_meters)):
                location_met = True
                conditions_met.append("位置条件满足")
            else:
                if unlock_condition.trigger_latitude and unlock_condition.trigger_longitude:
                    distance = calculate_distance(user_lat, user_lon,
                                                unlock_condition.trigger_latitude,
                                                unlock_condition.trigger_longitude)
                    conditions_not_met.append(f"位置条件未满足（当前距离{distance:.1f}米，需要{unlock_condition.radius_meters}米内）")
                else:
                    conditions_not_met.append("未设置位置条件")

        # 判断是否可以解锁
        can_unlock = False
        if unlock_condition.condition_type == "time":
            can_unlock = time_met
        elif unlock_condition.condition_type == "location":
            can_unlock = location_met
        elif unlock_condition.condition_type == "combined":
            can_unlock = time_met and location_met

        return {
            "can_unlock": can_unlock,
            "time_met": time_met,
            "location_met": location_met,
            "conditions_met": conditions_met,
            "conditions_not_met": conditions_not_met,
            "unlock_condition_type": unlock_condition.condition_type
        }

    def get_nearby_capsules(self, user_lat: float, user_lon: float, radius_meters: float, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户附近的胶囊

        Args:
            user_lat: 用户纬度
            user_lon: 用户经度
            radius_meters: 搜索半径（米）
            user_id: 用户ID

        Returns:
            附近胶囊列表，包含距离和解锁状态信息
        """
        if not DATABASE_AVAILABLE or not self.db:
            # 返回模拟数据用于测试
            print("Database not available, returning mock data")
            mock_data = [
                {
                    "id": "caps_001",
                    "title": "毕业纪念",
                    "created_at": datetime(2024, 10, 26, 10, 0, 0),
                    "creator_nickname": "小明",
                    "visibility": "public",
                    "is_unlocked": False,
                    "can_unlock": False,
                    "location": {
                        "latitude": 39.9042,
                        "longitude": 116.4074,
                        "distance": 150.5
                    }
                },
                {
                    "id": "caps_002",
                    "title": "足球比赛回忆",
                    "created_at": datetime(2024, 10, 25, 14, 30, 0),
                    "creator_nickname": "张三",
                    "visibility": "friends",
                    "is_unlocked": False,
                    "can_unlock": True,
                    "location": {
                        "latitude": 39.9052,
                        "longitude": 116.4084,
                        "distance": 320.8
                    }
                }
            ]

            # 过滤在半径内的胶囊
            result = []
            for capsule in mock_data:
                distance = calculate_distance(user_lat, user_lon, capsule["location"]["latitude"], capsule["location"]["longitude"])
                if distance <= radius_meters:
                    capsule["location"]["distance"] = distance
                    result.append(capsule)

            # 按距离排序
            result.sort(key=lambda x: x["location"]["distance"])
            return result

        # 查询半径内的所有胶囊（使用简单的边界框查询来优化性能）
        # 这里简化处理，实际生产环境可能需要更复杂的地理空间查询
        lat_delta = radius_meters / 111000  # 1度纬度约等于111km
        lon_delta = radius_meters / (111000 * abs(math.cos(math.radians(user_lat)))) if abs(math.cos(math.radians(user_lat))) > 0 else radius_meters / 111000

        nearby_capsules = self.db.query(CapsuleDB, UserDB.display_name).join(
            UserDB, CapsuleDB.user_id == UserDB.id
        ).filter(
            CapsuleDB.latitude >= user_lat - lat_delta,
            CapsuleDB.latitude <= user_lat + lat_delta,
            CapsuleDB.longitude >= user_lon - lon_delta,
            CapsuleDB.longitude <= user_lon + lon_delta
        ).all()

        result = []
        current_time = datetime.now()

        for capsule, creator_name in nearby_capsules:
            # 计算实际距离
            distance = calculate_distance(user_lat, user_lon, capsule.latitude, capsule.longitude)

            if distance <= radius_meters:
                # 检查解锁状态
                unlock_result = self.can_unlock_capsule(capsule.id, user_id, user_lat, user_lon, current_time)

                # 检查用户是否已经解锁过
                is_unlocked = self.db.query(UnlockRecordDB).filter(
                    UnlockRecordDB.capsule_id == capsule.id,
                    UnlockRecordDB.user_id == user_id
                ).first() is not None

                capsule_data = {
                    "id": str(capsule.id),  # 转换为字符串以匹配API规范
                    "title": capsule.title,
                    "created_at": capsule.created_at,
                    "creator_nickname": creator_name,
                    "visibility": capsule.visibility,
                    "is_unlocked": is_unlocked,
                    "can_unlock": unlock_result["can_unlock"],
                    "location": {
                        "latitude": capsule.latitude,
                        "longitude": capsule.longitude,
                        "distance": distance
                    }
                }
                result.append(capsule_data)

        # 按距离排序
        result.sort(key=lambda x: x["location"]["distance"])

        return result

    def verify_unlock_conditions(self, capsule_id: str, user_id: int, user_lat: float, user_lon: float, current_time: datetime = None) -> Dict[str, Any]:
        """
        验证解锁条件并执行解锁操作

        Args:
            capsule_id: 胶囊ID
            user_id: 用户ID
            user_lat: 用户当前纬度
            user_lon: 用户当前经度
            current_time: 当前时间，如果不提供则使用系统时间

        Returns:
            包含解锁结果的字典
        """
        if current_time is None:
            current_time = datetime.now()

        # 检查是否可以解锁
        unlock_result = self.can_unlock_capsule(int(capsule_id), user_id, user_lat, user_lon, current_time)

        if not unlock_result["can_unlock"]:
            return {
                "success": False,
                "reason": unlock_result.get("reason", "不满足解锁条件"),
                "conditions_met": unlock_result.get("conditions_met", []),
                "conditions_not_met": unlock_result.get("conditions_not_met", [])
            }

        # 执行解锁操作 - 创建解锁记录
        if DATABASE_AVAILABLE and self.db:
            try:
                unlock_record = UnlockRecordDB(
                    capsule_id=int(capsule_id),
                    user_id=user_id,
                    unlocked_at=current_time,
                    unlock_method="位置验证解锁",
                    unlock_latitude=user_lat,
                    unlock_longitude=user_lon
                )
                self.db.add(unlock_record)
                self.db.commit()

                # 生成访问令牌（简化版本，实际应该使用JWT）
                access_token = f"token_{capsule_id}_{user_id}_{int(current_time.timestamp())}"

                return {
                    "success": True,
                    "access_token": access_token,
                    "capsule_id": capsule_id,
                    "unlocked_at": current_time,
                    "conditions_met": unlock_result.get("conditions_met", [])
                }

            except Exception as e:
                self.db.rollback()
                return {
                    "success": False,
                    "reason": f"解锁失败: {str(e)}"
                }
        else:
            # 模拟解锁成功
            access_token = f"mock_token_{capsule_id}_{user_id}_{int(current_time.timestamp())}"
            return {
                "success": True,
                "access_token": access_token,
                "capsule_id": capsule_id,
                "unlocked_at": current_time,
                "conditions_met": unlock_result.get("conditions_met", ["模拟解锁条件"])
            }

    def create_capsule(self):
        pass        
        
