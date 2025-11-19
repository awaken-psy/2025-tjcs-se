from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import math

from database.orm.capsule import Capsule, CapsuleMedia
from database.orm.unlock_condition import UnlockCondition
from database.orm.unlock_record import UnlockRecord, UnlockAttempt
from database.orm.user import User
from database.orm.config import get_db


class CapsuleManager:
    """胶囊业务管理类"""

    def __init__(self, db: Session = None):
        self.db = db or next(get_db())

    def create_capsule(self, capsule_data: Dict[str, Any], user_id: int) -> Capsule:
        """
        创建新胶囊

        Args:
            capsule_data: 胶囊数据字典
            user_id: 创建者用户ID

        Returns:
            Capsule: 创建的胶囊对象
        """
        try:
            # 创建胶囊主体
            lat = capsule_data.get('lat')
            lng = capsule_data.get('lng')

            # 如果没有提供经纬度，使用默认值
            if lat is None or lat == 0.0:
                lat = 39.9005  # 默认纬度
            if lng is None or lng == 0.0:
                lng = 116.3020  # 默认经度

            capsule = Capsule(
                title=capsule_data['title'],
                text_content=capsule_data['content'],
                user_id=user_id,
                latitude=lat,
                longitude=lng,
                address=capsule_data.get('location', ''),
                visibility=capsule_data.get('visibility', 'private'),
                status='locked',
                content_type='mixed' if capsule_data.get('imageUrl') else 'text'
            )

            self.db.add(capsule)
            self.db.flush()  # 获取胶囊ID

            # 处理媒体文件
            if capsule_data.get('imageUrl'):
                # 从imageUrl中提取文件名
                image_url = capsule_data['imageUrl']
                file_name = 'image.jpg'  # 默认文件名
                if image_url.startswith('/uploads/images/'):
                    file_name = image_url.replace('/uploads/images/', '')

                media = CapsuleMedia(
                    capsule_id=capsule.id,
                    file_type='image',
                    file_name=file_name,
                    file_path=capsule_data['imageUrl'],
                    file_size=capsule_data.get('fileSize', 0),
                    mime_type='image/jpeg',
                    upload_order=1
                )
                self.db.add(media)

            # 处理标签 - 存储在JSON字段中
            if capsule_data.get('tags'):
                # 这里可以将标签存储为JSON格式，或者创建单独的标签表
                capsule.tag_json = json.dumps(capsule_data['tags'])

            # 创建解锁条件（默认基于时间）
            unlock_condition = UnlockCondition(
                capsule_id=capsule.id,
                condition_type='time',
                unlock_time=datetime.now(),  # 立即可解锁用于测试
                radius_meters=100  # 默认100米触发半径
            )
            self.db.add(unlock_condition)

            self.db.commit()
            self.db.refresh(capsule)

            return capsule

        except Exception as e:
            self.db.rollback()
            raise Exception(f"创建胶囊失败: {str(e)}")

    def get_capsule_by_id(self, capsule_id: int, user_id: Optional[int] = None) -> Optional[Capsule]:
        """
        根据ID获取胶囊

        Args:
            capsule_id: 胶囊ID
            user_id: 当前用户ID（用于权限检查）

        Returns:
            Optional[Capsule]: 胶囊对象或None
        """
        try:
            capsule = self.db.query(Capsule).filter(Capsule.id == capsule_id).first()

            if capsule:
                # 简化权限检查：创建者或公开胶囊可以访问
                if capsule.user_id == user_id or capsule.visibility == 'public':
                    return capsule

            return None

        except Exception as e:
            raise Exception(f"获取胶囊失败: {str(e)}")

    def get_user_capsules(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20,
        status_filter: Optional[str] = None,
        visibility_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取用户的胶囊列表

        Args:
            user_id: 用户ID
            page: 页码
            limit: 每页数量
            status_filter: 状态筛选
            visibility_filter: 可见性筛选

        Returns:
            Dict: 包含胶囊列表和分页信息的字典
        """
        try:
            # 基础查询
            query = self.db.query(Capsule).filter(Capsule.user_id == user_id)

            # 简化筛选条件
            if status_filter and status_filter != 'all':
                query = query.filter(Capsule.status == status_filter)
            if visibility_filter and visibility_filter != 'all':
                query = query.filter(Capsule.visibility == visibility_filter)

            # 按创建时间倒序排列
            query = query.order_by(desc(Capsule.created_at))

            # 获取总数
            total = query.count()

            # 分页查询
            offset = (page - 1) * limit if page > 1 else 0
            capsules = query.offset(offset).limit(limit).all()

            return {
                'capsules': capsules,
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': math.ceil(total / limit) if limit > 0 else 0
            }

        except Exception as e:
            raise Exception(f"获取用户胶囊列表失败: {str(e)}")

    def get_accessible_capsules(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户可访问的胶囊列表（简化版本）

        Args:
            user_id: 用户ID
            page: 页码
            limit: 每页数量

        Returns:
            Dict: 包含胶囊列表和分页信息的字典
        """
        try:
            # 简化实现：暂时只返回用户自己的胶囊
            query = self.db.query(Capsule).filter(Capsule.user_id == user_id)

            # 按创建时间倒序排列
            query = query.order_by(desc(Capsule.created_at))

            # 获取总数
            total = query.count()

            # 分页查询
            offset = (page - 1) * limit if page > 1 else 0
            capsules = query.offset(offset).limit(limit).all()

            return {
                'capsules': capsules,
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': math.ceil(total / limit) if limit > 0 else 0
            }

        except Exception as e:
            raise Exception(f"获取可访问胶囊列表失败: {str(e)}")

    def update_capsule(self, capsule_id: int, update_data: Dict[str, Any], user_id: int) -> bool:
        """
        更新胶囊信息

        Args:
            capsule_id: 胶囊ID
            update_data: 更新数据
            user_id: 操作用户ID

        Returns:
            bool: 是否更新成功
        """
        try:
            capsule = self.db.query(Capsule).filter(
                and_(Capsule.id == capsule_id, Capsule.user_id == user_id)
            ).first()

            if not capsule:
                return False

            # 更新允许的字段
            if 'title' in update_data:
                capsule.title = update_data['title']
            if 'content' in update_data:
                capsule.text_content = update_data['content']
            if 'visibility' in update_data:
                capsule.visibility = update_data['visibility']
            if 'location' in update_data:
                capsule.address = update_data['location']
            if 'lat' in update_data:
                capsule.latitude = update_data['lat']
            if 'lng' in update_data:
                capsule.longitude = update_data['lng']
            if 'tags' in update_data:
                capsule.tag_json = json.dumps(update_data['tags'])

            capsule.updated_at = datetime.now()

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise Exception(f"更新胶囊失败: {str(e)}")

    def delete_capsule(self, capsule_id: int, user_id: int) -> bool:
        """
        删除胶囊

        Args:
            capsule_id: 胶囊ID
            user_id: 操作用户ID

        Returns:
            bool: 是否删除成功
        """
        try:
            capsule = self.db.query(Capsule).filter(
                and_(Capsule.id == capsule_id, Capsule.user_id == user_id)
            ).first()

            if not capsule:
                return False

            # 删除胶囊（级联删除相关记录）
            self.db.delete(capsule)
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise Exception(f"删除胶囊失败: {str(e)}")

    def _can_access_capsule(self, capsule: Capsule, user_id: Optional[int]) -> bool:
        """
        简化的权限检查

        Args:
            capsule: 胶囊对象
            user_id: 用户ID

        Returns:
            bool: 是否有访问权限
        """
        # 胶囊创建者可以访问
        if capsule.user_id == user_id:
            return True

        # 公开胶囊任何人都可以访问
        if capsule.visibility == 'public':
            return True

        # 简化处理：其他情况暂时不允许访问
        return False

    def _are_friends(self, user_id1: int, user_id2: int) -> bool:
        """
        简化的好友关系检查（暂时返回False）

        Args:
            user_id1: 用户1 ID
            user_id2: 用户2 ID

        Returns:
            bool: 是否为好友（暂时返回False）
        """
        return False