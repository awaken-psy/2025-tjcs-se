# backend/app/services/capsule.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import math

from app.database.orm.capsule import Capsule, CapsuleMedia
from app.database.orm.unlock_condition import UnlockCondition
from app.database.orm.unlock_record import UnlockRecord, UnlockAttempt
from app.database.orm.user import User


class CapsuleManager:
    """胶囊业务管理类"""

    def __init__(self, db: Session):
        """直接接收db会话，不自行获取"""
        self.db = db

    def create_capsule_from_request(self, request, user_id: int) -> Capsule:
        """
        从CapsuleCreateRequest创建胶囊
        
        Args:
            request: CapsuleCreateRequest对象
            user_id: 创建者用户ID
            
        Returns:
            Capsule: 创建的胶囊对象
        """
        capsule = Capsule(
            title=request.title,
            text_content=request.content,
            user_id=user_id,
            visibility=request.visibility,
            latitude=request.location.latitude if request.location else 0.0,
            longitude=request.location.longitude if request.location else 0.0,
            address=request.location.address if request.location else "未指定位置",
            status='draft'
        )
        
        # 处理标签
        if request.tags:
            capsule.tag_json = json.dumps(request.tags)
        
        # 处理解锁条件
        if request.unlock_conditions:
            unlock_condition = UnlockCondition(
                capsule_id=None,  # 稍后设置
                condition_type=request.unlock_conditions.type,
                unlock_time=datetime.fromisoformat(request.unlock_conditions.value.replace('Z', '+00:00')) if request.unlock_conditions.type == 'time' else None,
                radius_meters=request.unlock_conditions.radius if request.unlock_conditions.radius else 100
            )
        
        self.db.add(capsule)
        self.db.flush()  # 获取胶囊ID
        
        # 设置解锁条件的胶囊ID
        if request.unlock_conditions:
            unlock_condition.capsule_id = capsule.id
            self.db.add(unlock_condition)
        
        # 处理媒体文件
        if request.media_files:
            for i, file_id in enumerate(request.media_files):
                media = CapsuleMedia(
                    capsule_id=capsule.id,
                    file_type='image',  # 假设都是图片，实际根据需要判断
                    file_name=file_id,
                    file_path=f"/uploads/{file_id}",
                    file_size=0,
                    mime_type='image/jpeg',
                    upload_order=i + 1
                )
                self.db.add(media)
        
        self.db.commit()
        self.db.refresh(capsule)
        return capsule

    def get_capsule_detail(self, capsule_id: str, user_id: int) -> Optional[Capsule]:
        """
        获取胶囊详情（带关联数据）
        
        Args:
            capsule_id: 胶囊ID
            user_id: 当前用户ID
            
        Returns:
            Optional[Capsule]: 胶囊对象或None
        """
        capsule = self.db.query(Capsule).filter(Capsule.id == capsule_id).first()
        
        if capsule:
            # 权限检查：创建者或公开胶囊可以访问
            if capsule.user_id == user_id or capsule.visibility == 'public':
                return capsule
        
        return None

    def get_capsules_with_location(self, user_id: int, page: int = 1, limit: int = 20) -> List[Capsule]:
        """
        获取带位置信息的胶囊（地图模式）
        
        Args:
            user_id: 用户ID
            page: 页码
            limit: 每页数量
            
        Returns:
            List[Capsule]: 胶囊列表
        """
        offset = (page - 1) * limit
        
        return self.db.query(Capsule).filter(
            and_(
                or_(Capsule.user_id == user_id, Capsule.visibility == 'public'),
                Capsule.latitude.isnot(None),
                Capsule.longitude.isnot(None)
            )
        ).offset(offset).limit(limit).all()

    def get_capsules_by_timeline(self, user_id: int) -> Dict[str, List[Capsule]]:
        """
        按时间轴分组获取胶囊
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, List[Capsule]]: 按月份分组的胶囊
        """
        capsules = self.db.query(Capsule).filter(
            or_(Capsule.user_id == user_id, Capsule.visibility == 'public')
        ).order_by(desc(Capsule.created_at)).all()
        
        timeline_groups = {}
        for capsule in capsules:
            month_key = capsule.created_at.strftime("%Y年%m月")
            if month_key not in timeline_groups:
                timeline_groups[month_key] = []
            timeline_groups[month_key].append(capsule)
            
        return timeline_groups

    def get_capsules_by_tags(self, user_id: int, page: int = 1, limit: int = 20) -> List[Capsule]:
        """
        按标签获取胶囊
        
        Args:
            user_id: 用户ID
            page: 页码
            limit: 每页数量
            
        Returns:
            List[Capsule]: 胶囊列表
        """
        offset = (page - 1) * limit
        
        return self.db.query(Capsule).filter(
            and_(
                or_(Capsule.user_id == user_id, Capsule.visibility == 'public'),
                Capsule.tag_json.isnot(None)
            )
        ).offset(offset).limit(limit).all()

    def update_capsule_from_request(self, capsule_id: str, request, user_id: int) -> bool:
        """
        从CapsuleUpdateRequest更新胶囊
        
        Args:
            capsule_id: 胶囊ID
            request: CapsuleUpdateRequest对象
            user_id: 操作用户ID
            
        Returns:
            bool: 是否更新成功
        """
        capsule = self.db.query(Capsule).filter(
            and_(Capsule.id == capsule_id, Capsule.user_id == user_id)
        ).first()
        
        if not capsule:
            return False
        
        # 更新允许的字段
        if request.title:
            capsule.title = request.title
        if request.content:
            capsule.text_content = request.content
        if request.visibility:
            capsule.visibility = request.visibility
        if request.tags:
            capsule.tag_json = json.dumps(request.tags)
        
        capsule.updated_at = datetime.now()
        
        self.db.commit()
        return True

    def delete_capsule(self, capsule_id: str, user_id: int) -> bool:
        """
        删除胶囊
        
        Args:
            capsule_id: 胶囊ID
            user_id: 操作用户ID
            
        Returns:
            bool: 是否删除成功
        """
        capsule = self.db.query(Capsule).filter(
            and_(Capsule.id == capsule_id, Capsule.user_id == user_id)
        ).first()
        
        if not capsule:
            return False
        
        # 删除胶囊（级联删除相关记录）
        self.db.delete(capsule)
        self.db.commit()
        return True

    def get_user_capsules(self, user_id: int, page: int = 1, limit: int = 20, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        获取用户的胶囊列表
        
        Args:
            user_id: 用户ID
            page: 页码
            limit: 每页数量
            status_filter: 状态筛选
            
        Returns:
            Dict: 包含胶囊列表和分页信息的字典
        """
        # 基础查询
        query = self.db.query(Capsule).filter(Capsule.user_id == user_id)
        
        # 状态筛选
        if status_filter and status_filter != 'all':
            query = query.filter(Capsule.status == status_filter)
        
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

    def save_draft_from_request(self, request, user_id: int) -> Capsule:
        """
        从CapsuleDraftRequest保存草稿
        
        Args:
            request: CapsuleDraftRequest对象
            user_id: 创建者用户ID
            
        Returns:
            Capsule: 保存的胶囊对象
        """
        capsule = Capsule(
            title=request.title or "未命名草稿",
            text_content=request.content or "",
            user_id=user_id,
            visibility=request.visibility or 'private',
            latitude=0.0,
            longitude=0.0,
            address="未指定位置",
            status='draft'
        )
        
        self.db.add(capsule)
        self.db.commit()
        self.db.refresh(capsule)
        
        return capsule

    def _can_access_capsule(self, capsule: Capsule, user_id: Optional[int]) -> bool:
        """
        权限检查
        
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