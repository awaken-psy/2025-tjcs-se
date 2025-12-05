import json
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime

from app.domain.capsule import Capsule as CapsuleDomain, CapsuleStatus, Visibility, ContentType

if TYPE_CHECKING:
    from app.database.orm.capsule import Capsule
else:
    Capsule = None


class CapsuleRepository:
    """胶囊数据访问层 - 处理ORM与Domain对象的转换"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, capsule_id: str) -> Optional[CapsuleDomain]:
        """根据ID查找胶囊"""
        # 动态导入避免循环依赖
        from app.database.orm.capsule import Capsule

        # 处理字符串ID到整数ID的转换
        try:
            numeric_id = int(capsule_id)
        except ValueError:
            return None

        orm = self.db.query(Capsule).filter(Capsule.id == numeric_id).first()
        return self._orm_to_domain(orm) if orm else None
    
    def find_by_user_id(self, user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """分页查找用户的胶囊"""
        # 动态导入避免循环依赖
        from app.database.orm.capsule import Capsule

        offset = (page - 1) * limit
        query = self.db.query(Capsule).filter(Capsule.user_id == user_id)

        total = query.count()
        orms = query.order_by(Capsule.created_at.desc()).offset(offset).limit(limit).all()

        domains = []
        for orm in orms:
            domain = self._orm_to_domain(orm)
            if domain:
                domains.append(domain)

        return {
            'capsules': domains,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        }
    
    def save(self, domain: CapsuleDomain) -> CapsuleDomain:
        """保存Domain对象到数据库"""
        from app.database.orm.capsule import Capsule

        # 检查是否是更新（通过字符串ID查询）或新创建
        if domain.capsule_id and domain.capsule_id.startswith("capsule_"):
            # 尝试查找现有记录（假设capsule_id对应某个整数ID）
            try:
                # 如果capsule_id是格式化的ID，我们需要提取实际的数据库ID
                # 或者我们需要一种方式来映射字符串ID到整数ID
                existing_orm = self.db.query(Capsule).filter(Capsule.id == int(domain.capsule_id.replace("capsule_", ""))).first()
                if existing_orm:
                    orm = existing_orm
                else:
                    orm = Capsule()
            except (ValueError, IndexError):
                orm = Capsule()
        elif domain.capsule_id and domain.capsule_id.isdigit():
            # 如果是纯数字ID
            try:
                existing_orm = self.db.query(Capsule).filter(Capsule.id == int(domain.capsule_id)).first()
                if existing_orm:
                    orm = existing_orm
                else:
                    orm = Capsule()
            except ValueError:
                orm = Capsule()
        else:
            orm = Capsule()

        # 设置基本ORM属性（暂时不处理解锁条件）
        self._update_orm_basic_fields(orm, domain)

        self.db.add(orm)
        self.db.flush()
        self.db.commit()
        self.db.refresh(orm)

        saved_domain = self._orm_to_domain(orm)
        if saved_domain is None:
            raise ValueError("Failed to convert saved ORM to Domain")
        return saved_domain

    def _update_orm_basic_fields(self, orm, domain: CapsuleDomain):
        """更新ORM对象基本字段从Domain对象（不处理解锁条件）"""
        # 基本字段映射
        orm.user_id = int(domain.owner_id)
        orm.title = domain.title
        orm.text_content = domain.content
        orm.visibility = domain.visibility.value
        orm.status = domain.status.value
        orm.content_type = domain.content_type.value
        orm.created_at = domain.created_at
        orm.updated_at = domain.updated_at

        # 位置信息 - ORM中latitude和longitude是必需字段
        if domain.unlock_location:
            orm.latitude = float(domain.unlock_location[0])
            orm.longitude = float(domain.unlock_location[1])
        else:
            # 如果没有位置信息，设置默认值
            orm.latitude = 0.0
            orm.longitude = 0.0

    
    def delete_by_id(self, capsule_id: str) -> bool:
        """根据ID删除胶囊"""
        # 动态导入避免循环依赖
        from app.database.orm.capsule import Capsule

        # 处理字符串ID到整数ID的转换
        if capsule_id.startswith("capsule_"):
            try:
                # 提取数字部分
                numeric_id = int(capsule_id.replace("capsule_", ""))
                orm = self.db.query(Capsule).filter(Capsule.id == numeric_id).first()
            except (ValueError, IndexError):
                return False
        else:
            try:
                # 尝试直接转换为整数
                numeric_id = int(capsule_id)
                orm = self.db.query(Capsule).filter(Capsule.id == numeric_id).first()
            except ValueError:
                return False

        if orm:
            self.db.delete(orm)
            self.db.commit()
            return True
        return False
    
    def find_by_user_with_location(self, user_id: int, page: int = 1, limit: int = 20) -> List[CapsuleDomain]:
        """查找带位置信息的用户胶囊"""
        # 动态导入避免循环依赖
        from app.database.orm.capsule import Capsule

        offset = (page - 1) * limit
        orms = self.db.query(Capsule).filter(
            Capsule.user_id == user_id,
            Capsule.latitude.isnot(None),
            Capsule.longitude.isnot(None)
        ).offset(offset).limit(limit).all()

        domains = []
        for orm in orms:
            domain = self._orm_to_domain(orm)
            if domain:
                domains.append(domain)
        return domains
    
    def find_by_user_timeline(self, user_id: int) -> List[CapsuleDomain]:
        """按时间轴获取用户胶囊"""
        # 动态导入避免循环依赖
        from app.database.orm.capsule import Capsule

        orms = self.db.query(Capsule).filter(
            Capsule.user_id == user_id
        ).order_by(Capsule.created_at.desc()).all()

        domains = []
        for orm in orms:
            domain = self._orm_to_domain(orm)
            if domain:
                domains.append(domain)
        return domains
    
    def find_by_user_with_tags(self, user_id: int, page: int = 1, limit: int = 20) -> List[CapsuleDomain]:
        """获取带标签的用户胶囊"""
        # 动态导入避免循环依赖
        from app.database.orm.capsule import Capsule

        offset = (page - 1) * limit
        orms = self.db.query(Capsule).filter(
            Capsule.user_id == user_id,
            Capsule.tag_json.isnot(None)
        ).offset(offset).limit(limit).all()

        domains = []
        for orm in orms:
            domain = self._orm_to_domain(orm)
            if domain:
                domains.append(domain)
        return domains
    
    def _orm_to_domain(self, orm: 'Capsule') -> Optional[CapsuleDomain]:
        """ORM对象转Domain对象"""
        if not orm:
            return None

        # 解析标签
        tags = []
        tag_json = getattr(orm, 'tag_json', None)
        if tag_json:
            try:
                tags = json.loads(tag_json)
            except (json.JSONDecodeError, TypeError):
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
        latitude = getattr(orm, 'latitude', None)
        longitude = getattr(orm, 'longitude', None)
        if latitude and longitude and latitude != 0.0 and longitude != 0.0:
            try:
                unlock_location = (float(latitude), float(longitude))
            except (TypeError, ValueError):
                unlock_location = None

        # 处理时间字段，确保是datetime对象
        created_at = getattr(orm, 'created_at', datetime.now())
        if not isinstance(created_at, datetime):
            created_at = datetime.now()

        updated_at = getattr(orm, 'updated_at', created_at)
        if not isinstance(updated_at, datetime):
            updated_at = created_at

        # 尝试从unlock_conditions表获取解锁条件
        unlock_time = None
        unlock_radius = 100  # 默认100米

        if hasattr(orm, 'unlock_conditions') and orm.unlock_conditions:
            condition = orm.unlock_conditions
            if condition.unlock_time:
                unlock_time = condition.unlock_time
            if condition.radius_meters:
                unlock_radius = condition.radius_meters

        return CapsuleDomain(
            capsule_id=str(orm.id) if orm.id else "",
            owner_id=str(orm.user_id) if hasattr(orm, 'user_id') and orm.user_id else "",
            title=getattr(orm, 'title', ""),
            description=getattr(orm, 'text_content', "")[:100] if getattr(orm, 'text_content', None) else None,
            content=getattr(orm, 'text_content', ""),
            visibility=self._convert_visibility(getattr(orm, 'visibility', 'private')),
            status=self._convert_status(getattr(orm, 'status', 'locked')),
            content_type=content_type,
            created_at=created_at,
            updated_at=updated_at,
            unlock_location=unlock_location,
            unlock_time=unlock_time,
            unlock_radius=unlock_radius
        )
    
    @staticmethod
    def _domain_to_orm(domain: CapsuleDomain) -> 'Capsule':
        """Domain对象转ORM对象"""
        # 动态导入避免循环依赖
        from app.database.orm.capsule import Capsule

        orm = Capsule()

        # 注意：ORM的id是自增整数，不需要设置
        # 但如果是更新已有对象，可能需要根据capsule_id查找并更新

        # 基本字段映射
        orm.user_id = int(domain.owner_id)
        orm.title = domain.title
        orm.text_content = domain.content
        orm.visibility = domain.visibility.value
        orm.status = domain.status.value
        orm.content_type = domain.content_type.value
        orm.created_at = domain.created_at
        orm.updated_at = domain.updated_at

        # 位置信息 - ORM中latitude和longitude是必需字段
        if domain.unlock_location:
            orm.latitude = float(domain.unlock_location[0])
            orm.longitude = float(domain.unlock_location[1])
        else:
            # 如果没有位置信息，设置默认值或None
            orm.latitude = 0.0
            orm.longitude = 0.0

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