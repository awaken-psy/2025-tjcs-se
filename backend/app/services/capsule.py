from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.domain.capsule import Capsule as CapsuleDomain, CapsuleStatus, Visibility, ContentType
from app.database.repositories.capsule_repository import CapsuleRepository
from app.model.capsule import (
    CapsuleCreateRequest, CapsuleUpdateRequest, CapsuleDraftRequest,
    CapsuleCreateResponse, CapsuleUpdateResponse, CapsuleDraftResponse,CapsuleDetail
)
from app.core.exceptions import RecordNotFoundException


class CapsuleService:
    """胶囊业务服务类"""

    def __init__(self, db: Optional[Session] = None):
        self.repository = CapsuleRepository(db)

    def create_capsule(self, request: CapsuleCreateRequest, user_id: int) -> CapsuleCreateResponse:
        """创建胶囊"""
        # 不再生成自定义ID，让数据库自动分配Integer ID

        # 处理位置信息 - 标准3字段格式
        unlock_location = None
        if request.location:
            unlock_location = (
                request.location.latitude,
                request.location.longitude,
                request.location.address or ""  # 地址字段，空值时使用空字符串
            )

        # 确定内容类型
        content_type = ContentType.TEXT
        if request.tags:
            if any("image" in tag.lower() or "图片" in tag for tag in request.tags):
                content_type = ContentType.IMAGE
            elif any("audio" in tag.lower() or "音频" in tag for tag in request.tags):
                content_type = ContentType.AUDIO
            elif len(request.tags) > 1:
                content_type = ContentType.MIXED

        # 创建Domain对象（不设置capsule_id，让数据库自动分配）
        capsule_domain = CapsuleDomain(
            capsule_id=None,  # 让数据库自动分配ID
            owner_id=str(user_id),
            title=request.title,
            description=request.content[:100] if request.content else None,
            content=request.content,
            visibility=self._convert_visibility(request.visibility),
            status=CapsuleStatus.LOCKED,
            content_type=content_type,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            unlock_location=unlock_location
        )
        
        saved_domain = self.repository.save(capsule_domain)
        
        return CapsuleCreateResponse(
            capsule_id=saved_domain.capsule_id,
            title=saved_domain.title,
            status=saved_domain.status.value,
            created_at=saved_domain.created_at
        )

    def get_capsule_detail(self, capsule_id: int, user_id: int, user) -> Optional['CapsuleDetail']:
        """获取胶囊详情"""
        capsule_domain = self.repository.find_by_id(capsule_id)
        if capsule_domain and capsule_domain.can_view_by(str(user_id)):
            return capsule_domain.to_api_detail(user)
        return None

    def get_user_capsules(self, user_id: int, page: int = 1, limit: int = 20, status: str = "all"):
        """获取用户胶囊列表"""
        result = self.repository.find_by_user_id(user_id, page, limit, status)
        basic_list = [domain.to_api_basic() for domain in result['capsules']]
        
        return {
            'capsules': basic_list,
            'total': result['total'],
            'page': result['page'],
            'limit': result['limit'],
            'total_pages': result['total_pages']
        }

    def update_capsule(self, capsule_id: int, request: CapsuleUpdateRequest, user_id: int) -> bool:
        """更新胶囊"""
        capsule_domain = self.repository.find_by_id(capsule_id)
        if not capsule_domain or not capsule_domain.can_edit_by(str(user_id)):
            return False
        
        if request.title:
            capsule_domain.title = request.title
        if request.content:
            capsule_domain.content = request.content
            capsule_domain.description = request.content[:100]
        if request.visibility:
            capsule_domain.visibility = self._convert_visibility(request.visibility)
        
        capsule_domain.updated_at = datetime.utcnow()
        
        try:
            # 即使 find_by_id 成功，也使用 try-except 块以应对 Repository 内部的潜在异常
            self.repository.save(capsule_domain)
            return True
        except RecordNotFoundException:
            # 如果 repository.save 逻辑被重构为抛出此异常（例如，在 find_by_id 逻辑之外）
            # 捕获它并返回 False，符合原函数返回 bool 的约定
            return False

    def delete_capsule(self, capsule_id: int, user_id: int) -> bool:
        """删除胶囊"""
        capsule_domain = self.repository.find_by_id(capsule_id)
        if capsule_domain and capsule_domain.can_delete_by(str(user_id)):
            return self.repository.delete_by_id(capsule_id)
        return False

    def save_draft(self, request: CapsuleDraftRequest, user_id: int) -> CapsuleDraftResponse:
        """保存草稿"""
        # 让数据库自动分配Integer ID，不再生成字符串ID

        capsule_domain = CapsuleDomain(
            capsule_id=None,
            owner_id=str(user_id),
            title=request.title or "未命名草稿",
            description=request.content[:100] if request.content else None,
            content=request.content or "",
            visibility=self._convert_visibility(request.visibility or "private"),
            status=CapsuleStatus.LOCKED,
            content_type=ContentType.TEXT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        saved_domain = self.repository.save(capsule_domain)
        
        return CapsuleDraftResponse(
            draft_id=saved_domain.capsule_id,  # 现在是Integer ID
            saved_at=saved_domain.created_at
        )

    def get_capsules_with_location(self, user_id: int, page: int = 1, limit: int = 20):
        """获取带位置信息的胶囊"""
        return self.repository.find_by_user_with_location(user_id, page, limit)

    def get_capsules_by_timeline(self, user_id: int) -> Dict[str, List]:
        """按时间轴分组获取胶囊"""
        capsules = self.repository.find_by_user_timeline(user_id)
        
        timeline_groups = {}
        for capsule in capsules:
            month_key = capsule.created_at.strftime("%Y年%m月")
            if month_key not in timeline_groups:
                timeline_groups[month_key] = []
            timeline_groups[month_key].append(capsule)
        
        return timeline_groups

    def get_capsules_by_tags(self, user_id: int, page: int = 1, limit: int = 20):
        """按标签获取胶囊"""
        return self.repository.find_by_user_with_tags(user_id, page, limit)

    def _convert_visibility(self, visibility: str):
        """转换可见性枚举"""
        if visibility == "public":
            return Visibility.CAMPUS
        elif visibility in ["friends", "friend"]:
            return Visibility.FRIENDS
        elif visibility == "private":
            return Visibility.PRIVATE
        else:
            # 默认为私有
            return Visibility.PRIVATE


# 向后兼容别名
CapsuleManager = CapsuleService