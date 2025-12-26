from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.database.orm.unlock_condition import UnlockCondition
from app.database.database import get_db
from app.logger import get_logger

unlock_condition_repository_log = get_logger(__name__)


class UnlockConditionRepository:
    """解锁条件数据访问层"""
    
    def __init__(self, db: Optional[Session]=None):
        try:
            if db is not None:
                self.db = db
            else:
                self.db = next(get_db())
        except Exception as e:
            raise Exception(f"数据库连接失败: {str(e)}")
    
    def find_by_capsule_id(self, capsule_id: int) -> Optional[UnlockCondition]:
        """根据胶囊ID查找解锁条件"""
        return self.db.query(UnlockCondition).filter(
            UnlockCondition.capsule_id == capsule_id
        ).first()
    
    def find_by_id(self, condition_id: int) -> Optional[UnlockCondition]:
        """根据ID查找解锁条件"""
        return self.db.query(UnlockCondition).filter(
            UnlockCondition.id == condition_id
        ).first()
    
    def save(self, condition: UnlockCondition) -> UnlockCondition:
        """保存解锁条件到数据库"""
        if condition.id is None:
            # 插入新记录
            self.db.add(condition)
        else:
            # 更新现有记录
            existing = self.find_by_id(condition.id)
            if existing is None:
                self.db.add(condition)
        
        self.db.flush()
        self.db.commit()
        self.db.refresh(condition)
        
        return condition
    
    def delete_by_capsule_id(self, capsule_id: int) -> bool:
        """根据胶囊ID删除解锁条件"""
        condition = self.find_by_capsule_id(capsule_id)
        if condition:
            self.db.delete(condition)
            self.db.commit()
            return True
        return False
    
    def delete_by_id(self, condition_id: int) -> bool:
        """根据ID删除解锁条件"""
        condition = self.find_by_id(condition_id)
        if condition:
            self.db.delete(condition)
            self.db.commit()
            return True
        return False
    
    def find_all(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """分页查找所有解锁条件"""
        offset = (page - 1) * limit
        query = self.db.query(UnlockCondition)
        
        total = query.count()
        conditions = query.order_by(UnlockCondition.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        
        return {
            'conditions': conditions,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        }
    
    def update_condition_type(self, capsule_id: int, condition_type: str) -> Optional[UnlockCondition]:
        """更新解锁条件类型"""
        condition = self.find_by_capsule_id(capsule_id)
        if condition:
            condition.condition_type = condition_type
            return self.save(condition)
        return None
    
    def update_password(self, capsule_id: int, password: str) -> Optional[UnlockCondition]:
        """更新解锁密码"""
        condition = self.find_by_capsule_id(capsule_id)
        if condition:
            condition.password = password
            return self.save(condition)
        return None
    
    def update_location_condition(self, capsule_id: int, latitude: float, longitude: float, radius: int = 100) -> Optional[UnlockCondition]:
        """更新位置条件"""
        condition = self.find_by_capsule_id(capsule_id)
        if condition:
            condition.trigger_latitude = latitude
            condition.trigger_longitude = longitude
            condition.radius_meters = radius
            return self.save(condition)
        return None
    
    def update_time_condition(self, capsule_id: int, unlockable_time: datetime) -> Optional[UnlockCondition]:
        """更新时间条件"""
        condition = self.find_by_capsule_id(capsule_id)
        if condition:
            condition.unlockable_time = unlockable_time
            return self.save(condition)
        return None