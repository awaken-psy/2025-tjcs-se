from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.database.orm.event import Event, EventRegistration
from app.database.database import get_db
from app.core.exceptions import RecordNotFoundException


class EventRepository:
    """活动数据访问层"""

    def __init__(self, db: Optional[Session]=None):
        try:
            if db is not None:
                self.db = db
            else:
                self.db = next(get_db())
        except Exception as e:
            raise Exception(f"数据库连接失败: {str(e)}")

    def find_by_id(self, event_id: int) -> Optional[Event]:
        """根据ID查找活动"""
        return self.db.query(Event).filter(Event.id == event_id).first()

    def find_by_user_id(self, user_id: int, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """分页查找用户创建的活动"""
        offset = (page - 1) * page_size
        query = self.db.query(Event).filter(Event.creator_id == user_id)

        total = query.count()
        events = query.order_by(Event.created_at.desc()).offset(offset).limit(page_size).all()

        return {
            'events': events,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def find_all(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """分页查找所有活动"""
        offset = (page - 1) * page_size
        query = self.db.query(Event)

        total = query.count()
        events = query.order_by(Event.created_at.desc()).offset(offset).limit(page_size).all()

        return {
            'events': events,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def save(self, event: Event) -> Event:
        """保存活动到数据库"""
        try:
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            return event
        except Exception as e:
            self.db.rollback()
            raise Exception(f"保存活动失败: {str(e)}")

    def update(self, event: Event) -> Event:
        """更新活动"""
        try:
            self.db.commit()
            self.db.refresh(event)
            return event
        except Exception as e:
            self.db.rollback()
            raise Exception(f"更新活动失败: {str(e)}")

    def delete(self, event: Event) -> bool:
        """删除活动"""
        try:
            self.db.delete(event)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"删除活动失败: {str(e)}")

    def find_registration(self, event_id: int, user_id: int) -> Optional[EventRegistration]:
        """查找用户报名记录"""
        return self.db.query(EventRegistration).filter(
            and_(EventRegistration.event_id == event_id,
                 EventRegistration.user_id == user_id)
        ).first()

    def create_registration(self, registration: EventRegistration) -> EventRegistration:
        """创建报名记录"""
        try:
            self.db.add(registration)
            self.db.commit()
            self.db.refresh(registration)
            return registration
        except Exception as e:
            self.db.rollback()
            raise Exception(f"创建报名记录失败: {str(e)}")

    def delete_registration(self, registration: EventRegistration) -> bool:
        """删除报名记录"""
        try:
            self.db.delete(registration)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"删除报名记录失败: {str(e)}")

    def find_user_registrations(self, user_id: int, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """查找用户报名的活动"""
        offset = (page - 1) * page_size
        query = self.db.query(Event).join(EventRegistration).filter(EventRegistration.user_id == user_id)

        total = query.count()
        events = query.order_by(Event.date.asc()).offset(offset).limit(page_size).all()

        return {
            'events': events,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def get_participant_count(self, event_id: int) -> int:
        """获取活动参与人数"""
        return self.db.query(EventRegistration).filter(EventRegistration.event_id == event_id).count()

    def is_user_registered(self, event_id: int, user_id: int) -> bool:
        """检查用户是否已报名"""
        return self.db.query(EventRegistration).filter(
            and_(EventRegistration.event_id == event_id,
                 EventRegistration.user_id == user_id)
        ).first() is not None