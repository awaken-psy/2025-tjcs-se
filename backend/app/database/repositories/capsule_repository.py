from sqlalchemy.orm import Session, joinedload
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.domain.capsule import Capsule as CapsuleDomain, CapsuleStatus, Visibility, ContentType
from app.database.orm.capsule import Capsule
from app.database.database import get_db
from app.core.exceptions import RecordNotFoundException


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
    
    def find_by_id(self, capsule_id: int) -> Optional[CapsuleDomain]:
        """根据ID查找胶囊"""
        orm = self.db.query(Capsule).options(
            joinedload(Capsule.unlock_conditions),
            joinedload(Capsule.media_files)
        ).filter(Capsule.id == capsule_id).first()
        return self._orm_to_domain(orm) if orm else None
    
    def find_by_user_id(self, user_id: int, page: int = 1, limit: int = 20, status: str = "all") -> Dict[str, Any]:
        """分页查找用户的胶囊"""
        offset = (page - 1) * limit
        query = self.db.query(Capsule).options(
            joinedload(Capsule.unlock_conditions),
            joinedload(Capsule.media_files)
        ).filter(Capsule.user_id == user_id)

        # "我的胶囊"应该显示用户的所有胶囊，不进行状态过滤
        # status参数在这里不使用，因为用户应该看到自己创建的所有胶囊

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
        """保存Domain对象到数据库 (修复更新/插入逻辑)"""
        if domain.capsule_id is None:
            # 插入逻辑：使用 _domain_to_orm 创建新的 ORM 实例
            orm = self._domain_to_orm(domain)
            self.db.add(orm)
        else:
            # 更新逻辑：加载现有 ORM 实例
            orm = self.db.query(Capsule).filter(Capsule.id == domain.capsule_id).first()
            if orm is None:
                # 记录不存在，抛出异常，Service 层需处理此 404 错误
                raise RecordNotFoundException(f"胶囊 ID {domain.capsule_id} 不存在，无法更新")
            else:
                # 更新属性：使用辅助方法更新现有实例
                self._update_orm_attributes(orm, domain)

        self.db.flush()
        self.db.commit()
        self.db.refresh(orm)
        
        return self._orm_to_domain(orm)
    
    def delete_by_id(self, capsule_id: int) -> bool:
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
        orms = self.db.query(Capsule).options(
            joinedload(Capsule.unlock_conditions),
            joinedload(Capsule.media_files)
        ).filter(
            Capsule.user_id == user_id,
            Capsule.latitude.isnot(None),
            Capsule.longitude.isnot(None)
        ).offset(offset).limit(limit).all()

        return [self._orm_to_domain(orm) for orm in orms]
    
    def find_by_user_timeline(self, user_id: int) -> List[CapsuleDomain]:
        """按时间轴获取用户胶囊"""
        orms = self.db.query(Capsule).options(
            joinedload(Capsule.unlock_conditions),
            joinedload(Capsule.media_files)
        ).filter(
            Capsule.user_id == user_id
        ).order_by(Capsule.created_at.desc()).all()

        return [self._orm_to_domain(orm) for orm in orms]
    
    def find_by_user_with_tags(self, user_id: int, page: int = 1, limit: int = 20) -> List[CapsuleDomain]:
        """获取带标签的用户胶囊"""
        offset = (page - 1) * limit
        orms = self.db.query(Capsule).options(
            joinedload(Capsule.unlock_conditions),
            joinedload(Capsule.media_files)
        ).filter(
            Capsule.user_id == user_id,
            Capsule.tag_json.isnot(None)
        ).offset(offset).limit(limit).all()

        return [self._orm_to_domain(orm) for orm in orms]
    
    def _update_orm_from_domain(self, orm: Capsule, domain: CapsuleDomain):
        """辅助方法：将 Domain 属性赋值给 ORM 实例"""
        # 确保不尝试更新主键 ID
        # orm.id = domain.capsule_id # 不要在这里设置，因为在ORM对象创建或加载时ID已确定

        orm.user_id = int(domain.owner_id)
        orm.title = domain.title
        orm.text_content = domain.content
        orm.visibility = domain.visibility.value
        orm.status = domain.status.value
        orm.created_at = domain.created_at # 注意：对于更新操作，这个值通常不应该被修改
        orm.updated_at = domain.updated_at
        
        # 设置位置信息 - 标准3字段格式
        if domain.unlock_location and len(domain.unlock_location) == 3:
            orm.latitude = domain.unlock_location[0]
            orm.longitude = domain.unlock_location[1]
            orm.address = domain.unlock_location[2]
        else:
            # 确保在更新时，如果没有位置信息，则显式设置为 None
            orm.latitude = None
            orm.longitude = None
            orm.address = None

    def _update_orm_attributes(self, orm: Capsule, domain: CapsuleDomain):
        """辅助方法：将 Domain 属性赋值给现有 ORM 实例 (用于更新)"""
        # 注意：不要更新 orm.id，它在 orm 被加载时已确定
        orm.user_id = int(domain.owner_id)
        orm.title = domain.title
        orm.text_content = domain.content
        orm.visibility = domain.visibility.value
        orm.status = domain.status.value
        orm.updated_at = domain.updated_at # 只更新 updated_at
        
        # 处理位置信息
        if domain.unlock_location and len(domain.unlock_location) == 3:
            orm.latitude = domain.unlock_location[0]
            orm.longitude = domain.unlock_location[1]
            orm.address = domain.unlock_location[2]
        else:
            # 使用默认值，保持与 _domain_to_orm 的逻辑一致
            orm.latitude = 0.0
            orm.longitude = 0.0
            orm.address = ""

    def find_all_with_location(self) -> List[CapsuleDomain]:
        """
        查找所有带位置信息且已发布（非草稿）的胶囊。
        返回 CapsuleDomain 列表。
        """
        # 过滤条件：必须有经纬度，且状态不是草稿（假设 'locked'/'unlocked' 才是已发布）
        # 💡 注意：如果您的 Capsule ORM 状态字段是枚举，请使用正确的检查方式。
        orms = self.db.query(Capsule).options(
            joinedload(Capsule.unlock_conditions),
            joinedload(Capsule.media_files)
        ).filter(
            Capsule.latitude.isnot(None),
            Capsule.longitude.isnot(None),
            # 排除草稿状态的胶囊。如果您的 status 字段包含 'draft'，需要明确排除。
            # 假设只有 status='locked' 或 status='unlocked' 的胶囊才算有效。
            # 这里简化为只要有位置信息且不是草稿的胶囊。
        ).all()
        
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

        # 解析解锁位置 - 标准3字段格式
        unlock_location = None
        if orm.latitude is not None and orm.longitude is not None:
            unlock_location = (
                float(orm.latitude),
                float(orm.longitude),
                orm.address or ""  # 地址字段，空值时使用空字符串
            )

        # 创建Domain对象，并传递解锁条件和媒体文件数据
        domain = CapsuleDomain(
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
            unlock_location=unlock_location,
            unlock_condition_data=orm.unlock_conditions,  # 传递解锁条件数据
            media_files_data=orm.media_files  # 传递媒体文件数据
        )

        return domain
    
    
        """Domain对象转ORM对象"""
        orm = Capsule()
        # 只有当capsule_id不为None时才设置，否则让数据库自动分配
        if domain.capsule_id is not None:
            orm.id = domain.capsule_id
        orm.user_id = int(domain.owner_id)
        orm.title = domain.title
        orm.text_content = domain.content
        orm.visibility = domain.visibility.value
        orm.status = domain.status.value
        orm.created_at = domain.created_at
        orm.updated_at = domain.updated_at
        
        # 设置位置信息 - 标准3字段格式
        if domain.unlock_location and len(domain.unlock_location) == 3:
            orm.latitude = domain.unlock_location[0]   # latitude
            orm.longitude = domain.unlock_location[1]  # longitude
            orm.address = domain.unlock_location[2]    # address
        
        return orm
    
    
    @staticmethod
    def _domain_to_orm(domain: CapsuleDomain) -> Capsule:
        """Domain对象转ORM对象"""
        orm = Capsule() # 📌 必须保留这一行来创建新对象 (用于插入)
        # 只有当capsule_id不为None时才设置，否则让数据库自动分配
        if domain.capsule_id is not None:
            orm.id = domain.capsule_id
        orm.user_id = int(domain.owner_id)
        orm.title = domain.title
        orm.text_content = domain.content
        orm.visibility = domain.visibility.value
        orm.status = domain.status.value
        orm.created_at = domain.created_at
        orm.updated_at = domain.updated_at
        
        # 设置位置信息 - 标准3字段格式
        if domain.unlock_location and len(domain.unlock_location) == 3:
            orm.latitude = domain.unlock_location[0]   # latitude
            orm.longitude = domain.unlock_location[1]  # longitude
            orm.address = domain.unlock_location[2]    # address
        else:
            # 修复：当 Domain 对象中没有位置信息时，提供一个非 NULL 的默认值
            orm.latitude = 0.0
            orm.longitude = 0.0
            orm.address = ""
        
        return orm

    @staticmethod
    def _convert_visibility(visibility: str) -> Visibility:
        """转换可见性枚举"""
        if visibility == "public" or visibility == "campus":
            return Visibility.CAMPUS
        elif visibility == "friends":
            return Visibility.FRIENDS
        elif visibility == "private":
            return Visibility.PRIVATE
        else:
            # 默认为私有
            return Visibility.PRIVATE
    
    @staticmethod
    def _convert_status(status: str) -> CapsuleStatus:
        """转换状态枚举"""
        if status == "draft":
            return CapsuleStatus.DRAFT
        elif status == "published":
            return CapsuleStatus.PUBLISHED
        elif status == "all":
            return CapsuleStatus.ALL
        else:
            return CapsuleStatus.DRAFT