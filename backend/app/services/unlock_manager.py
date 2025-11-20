from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from database.orm.capsule import Capsule
from database.orm.unlock_condition import UnlockCondition
from database.orm.unlock_record import UnlockRecord
from database.orm.config import get_db


class UnlockManager:
    """胶囊解锁业务管理类（简化版）"""

    def __init__(self, db: Session = None):
        self.db = db or next(get_db())

    def check_unlockable_capsules(
        self,
        user_id: int,
        user_latitude: float,
        user_longitude: float,
        max_distance_meters: int = 1000,
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        简化版：检查用户当前位置可解锁的胶囊
        """
        if not current_time:
            current_time = datetime.now()

        try:
            # 获取用户的所有胶囊
            capsules = self.db.query(Capsule).filter(
                Capsule.user_id == user_id
            ).all()

            unlockable_capsules = []

            for capsule in capsules:
                # 简化：所有胶囊都可解锁
                distance = 100  # 固定距离
                unlockable_capsules.append({
                    'capsule_id': capsule.id,
                    'title': capsule.title,
                    'created_at': capsule.created_at,
                    'position': {
                        'latitude': capsule.latitude,
                        'longitude': capsule.longitude,
                        'address': capsule.address or '未知位置'
                    },
                    'distance': distance,
                    'unlock_method': '自动解锁'
                })

            return {
                'success': True,
                'message': f"找到 {len(capsules)} 个胶囊，其中 {len(unlockable_capsules)} 个可以解锁",
                'unlockable_capsules': unlockable_capsules,
                'total_capsules_found': len(capsules),
                'unlockable_count': len(unlockable_capsules),
                'user_location': {
                    'latitude': user_latitude,
                    'longitude': user_longitude,
                    'address': '用户当前位置'
                },
                'check_time': current_time.isoformat()
            }

        except Exception as e:
            raise Exception(f"检查可解锁胶囊失败: {str(e)}")

    def unlock_capsule(
        self,
        user_id: int,
        capsule_id: int,
        user_latitude: Optional[float] = None,
        user_longitude: Optional[float] = None,
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        简化版：解锁胶囊
        """
        if not current_time:
            current_time = datetime.now()

        try:
            # 检查胶囊是否存在
            capsule = self.db.query(Capsule).filter(Capsule.id == capsule_id).first()
            if not capsule:
                return {
                    'success': False,
                    'message': f"胶囊 {capsule_id} 不存在"
                }

            # 简化：直接解锁
            capsule.status = 'unlocked'
            self.db.commit()

            # 构建胶囊详细信息
            capsule_detail = {
                'capsule_id': capsule.id,
                'title': capsule.title,
                'content': capsule.text_content,
                'location': {
                    'latitude': capsule.latitude,
                    'longitude': capsule.longitude,
                    'address': capsule.address
                },
                'visibility': capsule.visibility,
                'created_at': capsule.created_at.isoformat()
            }

            return {
                'success': True,
                'message': '解锁成功',
                'capsule_id': capsule_id,
                'unlocked_at': current_time.isoformat(),
                'capsule_context': capsule_detail,
                'unlock_method': '手动解锁',
                'unlock_conditions_met': ['简化条件']
            }

        except Exception as e:
            self.db.rollback()
            raise Exception(f"解锁胶囊失败: {str(e)}")

    def get_user_unlock_history(self, user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        获取用户解锁历史（简化版）
        """
        try:
            # 简化：返回空历史记录
            return {
                'records': [],
                'total': 0,
                'page': page,
                'limit': limit,
                'total_pages': 0
            }

        except Exception as e:
            raise Exception(f"获取解锁历史失败: {str(e)}")