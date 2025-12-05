from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.domain.capsule import Capsule as CapsuleDomain, CapsuleStatus, Visibility, ContentType
from app.database.orm.capsule import Capsule
from app.database.database import get_db


class CapsuleRepository:
    """胶囊数据访问层 - 处理ORM与Domain对象的转换"""
    
    def __init__(self, db: Optional[Session]=None):
        try:
            if db is not None:
                self.db = db
            else:
                self.db = next(get_db())
        except Exception as e:
            raise Exception(f"数据库连接失败: {str(e)}")
    
    def find_by_id(self, capsule_id: str) -> Optional[CapsuleDomain]:
        """根据ID查找胶囊"""
        orm = self.db.query(Capsule).filter(Capsule.id == capsule_id).first()
        return self._orm_to_domain(orm) if orm else None
    
    def find_by_user_id(self, user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """分页查找用户的胶囊"""
        offset = (page - 1) * limit
        query = self.db.query(Capsule).filter(Capsule.user_id == user_id)
        
        total = query.count()
        orms = query.order_by(Capsule.created_at.desc()).offset(offset).limit(limit).all()
        
        domains = [self._orm_to_domain(orm) for orm in orms]
        
        return {
            'capsules': domains,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        }
    
    def save(self, domain: CapsuleDomain) -> CapsuleDomain:
        """保存Domain对象到数据库"""
        orm = self._domain_to_orm(domain)
        self.db.add(orm)
        self.db.flush()
        self.db.commit()
        self.db.refresh(orm)
        
        return self._orm_to_domain(orm)
    
    def delete_by_id(self, capsule_id: str) -> bool:
        """根据ID删除胶囊"""
        orm = self.db.query(Capsule).filter(Capsule.id == capsule_id).first()
        if orm:
            self.db.delete(orm)
            self.db.commit()
            return True
        return False
    
    def find_by_user_with_location(self, user_id: int, page: int = 1, limit: int = 20) -> List[CapsuleDomain]:
        """查找带位置信息的用户胶囊"""
        offset = (page - 1) * limit
        orms = self.db.query(Capsule).filter(
            Capsule.user_id == user_id,
            Capsule.latitude.isnot(None),
            Capsule.longitude.isnot(None)
        ).offset(offset).limit(limit).all()
        
        return [self._orm_to_domain(orm) for orm in orms]
    
    def find_by_user_timeline(self, user_id: int) -> List[CapsuleDomain]:
        """按时间轴获取用户胶囊"""
        orms = self.db.query(Capsule).filter(
            Capsule.user_id == user_id
        ).order_by(Capsule.created_at.desc()).all()
        
        return [self._orm_to_domain(orm) for orm in orms]
    
    def find_by_user_with_tags(self, user_id: int, page: int = 1, limit: int = 20) -> List[CapsuleDomain]:
        """获取带标签的用户胶囊"""
        offset = (page - 1) * limit
        orms = self.db.query(Capsule).filter(
            Capsule.user_id == user_id,
            Capsule.tag_json.isnot(None)
        ).offset(offset).limit(limit).all()
        
        return [self._orm_to_domain(orm) for orm in orms]
    
    @staticmethod
    def _orm_to_domain(orm: Capsule) -> CapsuleDomain:
        """ORM对象转Domain对象"""
        # 解析标签
        tags = []
        if orm.tag_json:
            try:
                import json
                tags = json.loads(orm.tag_json)
            except:
                tags = []
        
        # 确定内容类型
        content_type = ContentType.TEXT
        if tags:
            if any("image" in tag.lower() or "图片" in tag for tag in tags):
                content_type = ContentType.IMAGE
            elif any("audio" in tag.lower() or "音频" in tag for tag in tags):
                content_type = ContentType.AUDIO
            elif len(tags) > 1:
                content_type = ContentType.MIXED
        
        # 解析解锁位置
        unlock_location = None
        if orm.latitude and orm.longitude:
            unlock_location = (orm.latitude, orm.longitude)
        
        return CapsuleDomain(
            capsule_id=orm.id,
            owner_id=str(orm.user_id),
            title=orm.title,
            description=orm.text_content[:100] if orm.text_content else None,
            content=orm.text_content,
            visibility=CapsuleRepository._convert_visibility(orm.visibility),
            status=CapsuleRepository._convert_status(orm.status),
            content_type=content_type,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            unlock_location=unlock_location
        )
    
    @staticmethod
    def _domain_to_orm(domain: CapsuleDomain) -> Capsule:
        """Domain对象转ORM对象"""
        orm = Capsule()
        orm.id = domain.capsule_id
        orm.user_id = int(domain.owner_id)
        orm.title = domain.title
        orm.text_content = domain.content
        orm.visibility = domain.visibility.value
        orm.status = domain.status.value
        orm.created_at = domain.created_at
        orm.updated_at = domain.updated_at
        
        # 设置位置信息
        if domain.unlock_location:
            orm.latitude = domain.unlock_location[0]
            orm.longitude = domain.unlock_location[1]
        
        return orm
    
    @staticmethod
    def _convert_visibility(visibility: str) -> Visibility:
        """转换可见性枚举"""
        if visibility == "public":
            return Visibility.CAMPUS
        elif visibility == "friends":
            return Visibility.FRIENDS
        else:
            return Visibility.PRIVATE
    
    @staticmethod
    def _convert_status(status: str) -> CapsuleStatus:
        """转换状态枚举"""
        if status == "published":
            return CapsuleStatus.LOCKED
        elif status == "unlocked":
            return CapsuleStatus.UNLOCKED
        else:
            return CapsuleStatus.LOCKED