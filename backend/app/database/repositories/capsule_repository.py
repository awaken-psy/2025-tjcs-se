from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from app.utils.datetime_helper import beijing_now

from app.domain.capsule import Capsule as CapsuleDomain, CapsuleStatus, Visibility, ContentType
from app.database.orm.capsule import Capsule
from app.database.orm.unlock_record import UnlockRecord
from app.database.orm.user import User
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

    # ==================== 新增的数据库操作方法 ====================

    def check_capsule_exists(self, capsule_id: int) -> bool:
        """检查胶囊是否存在"""
        return self.db.query(Capsule).filter(Capsule.id == capsule_id).first() is not None

    def find_unlock_record(self, capsule_id: int, user_id: int) -> Optional[UnlockRecord]:
        """查找用户的解锁记录"""
        return self.db.query(UnlockRecord).filter(
            and_(
                UnlockRecord.capsule_id == capsule_id,
                UnlockRecord.user_id == user_id
            )
        ).first()

    def has_user_unlocked_capsule(self, capsule_id: int, user_id: int) -> bool:
        """检查用户是否已解锁胶囊"""
        return self.find_unlock_record(capsule_id, user_id) is not None

    def update_unlock_record_view_count(self, unlock_record: UnlockRecord) -> None:
        """更新解锁记录的查看次数"""
        unlock_record.view_count += 1
        unlock_record.last_viewed_at = beijing_now()
        self.db.commit()

    def get_capsule_with_full_details(self, capsule_id: int) -> Optional[Tuple[Capsule, Optional[UnlockRecord]]]:
        """获取胶囊及其解锁记录（用于详情查看）"""
        capsule = self.db.query(Capsule).options(
            joinedload(Capsule.unlock_conditions),
            joinedload(Capsule.media_files),
            joinedload(Capsule.unlock_records)
        ).filter(Capsule.id == capsule_id).first()

        if not capsule:
            return None

        # 这里需要传入user_id，但这个方法不应该依赖用户信息
        # 解锁记录的查找应该在Service层进行
        return capsule

    def get_capsule_basic_info(self, capsule_id: int) -> Optional[Dict[str, Any]]:
        """获取胶囊基本信息（用于权限检查）"""
        result = self.db.query(
            Capsule.id,
            Capsule.user_id,
            Capsule.visibility,
            Capsule.status,
            Capsule.title
        ).filter(Capsule.id == capsule_id).first()

        if not result:
            return None

        return {
            'id': result.id,
            'user_id': result.user_id,
            'visibility': result.visibility,
            'status': result.status,
            'title': result.title
        }

    def count_user_capsules(self, user_id: int, status_filter: Optional[str] = None) -> int:
        """统计用户胶囊数量"""
        query = self.db.query(Capsule).filter(Capsule.user_id == user_id)

        if status_filter and status_filter != "all":
            query = query.filter(Capsule.status == status_filter)

        return query.count()

    def find_nearby_capsules(self, latitude: float, longitude: float,
                           radius_meters: int, limit: int = 20) -> List[Dict[str, Any]]:
        """查找附近的胶囊（简化版本，使用边界框查询）"""
        # 计算边界框
        lat_delta = radius_meters / 111000  # 1度纬度约111km
        lon_delta = radius_meters / (111000 * abs(latitude))  # 经度随纬度变化

        min_lat = latitude - lat_delta
        max_lat = latitude + lat_delta
        min_lon = longitude - lon_delta
        max_lon = longitude + lon_delta

        # 查询附近的胶囊
        capsules = self.db.query(Capsule).options(
            joinedload(Capsule.unlock_conditions),
            joinedload(Capsule.media_files)
        ).filter(
            and_(
                Capsule.latitude >= min_lat,
                Capsule.latitude <= max_lat,
                Capsule.longitude >= min_lon,
                Capsule.longitude <= max_lon,
                Capsule.visibility.in_(['public', 'campus'])
            )
        ).limit(limit).all()

        return [
            {
                'capsule': self._orm_to_domain(capsule),
                'orm': capsule
            }
            for capsule in capsules
        ]

    def delete_capsule_by_id(self, capsule_id: int) -> bool:
        """根据ID删除胶囊"""
        capsule = self.db.query(Capsule).filter(Capsule.id == capsule_id).first()
        if capsule:
            self.db.delete(capsule)
            self.db.commit()
            return True
        return False

    def get_capsule_view_count(self, capsule_id: int) -> int:
        """获取胶囊的总浏览次数（通过统计解锁记录的查看次数）"""
        from app.database.orm.unlock_record import UnlockRecord

        # 查询所有解锁记录的查看次数总和
        result = self.db.query(func.sum(UnlockRecord.view_count)).filter(
            UnlockRecord.capsule_id == capsule_id
        ).first()

        # 如果结果为None，返回0；否则返回总和
        if result is None or result[0] is None:
            return 0
        return int(result[0])