from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from datetime import datetime

from app.domain.capsule import (
    Capsule as CapsuleDomain, CapsuleStatus, Visibility, ContentType
)
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
            status=CapsuleStatus.PUBLISHED,
            content_type=content_type,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            unlock_location=unlock_location
        )
        
        saved_domain = self.repository.save(capsule_domain)

        # 确保数据完整性并返回
        capsule_id = saved_domain.capsule_id
        if capsule_id is None:
            raise ValueError("胶囊创建失败：未获取到胶囊ID")

        # 保存解锁条件
        if request.unlock_conditions:
            self._save_unlock_conditions(capsule_id, request.unlock_conditions, unlock_location)

        # 保存媒体文件
        if request.media_files:
            self._save_media_files(capsule_id, request.media_files)

        return CapsuleCreateResponse(
            capsule_id=str(capsule_id),  # int转换为string，匹配新的模型定义
            title=saved_domain.title,
            status=self._convert_status_for_frontend(saved_domain.status.value),  # 状态转换
            created_at=saved_domain.created_at
        )

    def get_capsule_detail(self, capsule_id: int, user_id: int, user) -> tuple[bool, str, Optional['CapsuleDetail']]:
        """
        获取胶囊详情

        Returns:
            tuple: (是否成功, 信息, 胶囊详情对象或None)
        """
        # 1. 首先查找胶囊是否存在
        capsule_domain = self.repository.find_by_id(capsule_id)
        if not capsule_domain:
            return False, "胶囊不存在", None

        # 2. 检查用户权限
        permission_result = self._check_view_permission(capsule_domain, user_id, user)
        if not permission_result[0]:
            return *permission_result, None

        # 3. 查询解锁记录
        unlock_record = self.repository.find_unlock_record(capsule_id, user_id)
        is_unlocked = unlock_record is not None

        # 4. 构建胶囊详情，包含解锁状态信息
        capsule_detail = capsule_domain.to_api_detail(user)

        # 5. 添加解锁状态信息到响应中
        if hasattr(capsule_detail, 'unlock_conditions'):
            # 如果unlock_conditions是一个对象，设置is_unlocked属性
            if hasattr(capsule_detail.unlock_conditions, 'is_unlocked'):
                capsule_detail.unlock_conditions.is_unlocked = is_unlocked
            else:
                # 如果是字典格式，直接设置
                if isinstance(capsule_detail.unlock_conditions, dict):
                    capsule_detail.unlock_conditions['is_unlocked'] = is_unlocked

        # 6. 如果有解锁记录，更新查看次数
        if unlock_record:
            self.repository.update_unlock_record_view_count(unlock_record)

        return True, "获取胶囊详情成功", capsule_detail

    def _check_view_permission(self, capsule_domain, user_id: int, user) -> tuple[bool, str]:
        """
        检查用户查看权限

        Returns:
            tuple: (是否有权限, 拒绝信息或"允许访问")
        """
        is_owner = str(capsule_domain.owner_id) == str(user_id)
        is_admin = hasattr(user, 'role') and user.role.value == "admin"

        if is_owner:
            return True, "允许访问"
        elif is_admin:
            return True, "允许访问"

        # 检查是否已解锁
        is_unlocked = self.repository.has_user_unlocked_capsule(capsule_domain.capsule_id, user_id)

        if not is_unlocked:
            return False, "需要解锁后才能查看胶囊详情"

        return True, "允许访问"

    def has_user_unlocked_capsule(self, capsule_id: int, user_id: int) -> bool:
        """检查用户是否已解锁指定胶囊"""
        from app.database.orm.unlock_record import UnlockRecord

        unlock_record = self.repository.db.query(UnlockRecord).filter(
            UnlockRecord.capsule_id == capsule_id,
            UnlockRecord.user_id == user_id
        ).first()

        return unlock_record is not None

    def can_user_view_capsule(self, capsule_domain, user_id: int, user) -> bool:
        """检查用户是否可以查看指定胶囊"""
        if not capsule_domain:
            return False

        # 查询解锁记录
        is_unlocked = self.has_user_unlocked_capsule(capsule_domain.capsule_id, user_id)

        # 获取胶囊基本信息
        capsule_type = capsule_domain.visibility.value if capsule_domain.visibility else "private"
        is_owner = str(capsule_domain.owner_id) == str(user_id)
        is_admin = hasattr(user, 'role') and user.role.value == "admin"

        # 权限判断逻辑
        if is_owner:
            return True
        elif is_admin:
            return True
        elif capsule_type == "public":
            return is_unlocked or is_owner
        elif capsule_type == "private":
            return is_unlocked or is_owner
        elif capsule_type == "friends":
            # TODO: 添加好友关系检查
            return is_unlocked or is_owner
        elif capsule_type == "campus":
            # TODO: 添加校园验证
            return is_unlocked or is_owner
        else:
            return is_unlocked or is_owner

    def get_user_capsules(self, user_id: int, page: int = 1, limit: int = 20, status: str = "all", user=None):
        """获取用户胶囊列表"""
        result = self.repository.find_by_user_id(user_id, page, limit, status)

        # 由于CapsuleListResponse现在要求CapsuleDetail格式，需要使用to_api_detail()方法
        # 如果没有传入user对象，创建一个简单的对象用于基本信息展示
        if user is None:
            # 创建一个简单的对象来模拟用户，用于to_api_detail方法
            class SimpleUser:
                def __init__(self, user_id):
                    self.user_id = user_id
                    self.username = None
                    self.nickname = None
                    self.avatar_url = None
            user = SimpleUser(user_id)

        # 转换为CapsuleDetail格式
        detail_list = [domain.to_api_detail(user) for domain in result['capsules']]

        return {
            'capsules': detail_list,
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
            status=CapsuleStatus.DRAFT,
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

    def _convert_status_for_frontend(self, status: str) -> str:
        """转换状态为前端期望的格式"""
        # 数据库内部值 -> 前端API值
        status_mapping = {
            "locked": "published",    # 锁定状态对应已发布
            "unlocked": "published",  # 解锁状态也算已发布
            "draft": "draft",        # 草稿状态保持不变
            "expired": "published"    # 过期状态也算已发布
        }
        return status_mapping.get(status, "published")

    def _save_unlock_conditions(self, capsule_id: int, unlock_conditions, capsule_location=None):
        """保存解锁条件到数据库"""
        from app.database.orm.unlock_condition import UnlockCondition

        # unlock_conditions 可能是字典或 Pydantic UnlockConditions 对象
        if hasattr(unlock_conditions, 'type'):
            # Pydantic 对象
            condition_type = getattr(unlock_conditions, 'type', 'private')
            password = getattr(unlock_conditions, 'password', None)
            radius = getattr(unlock_conditions, 'radius', None)
            unlockable_time = getattr(unlock_conditions, 'unlockable_time', None)
        else:
            # 字典对象
            condition_type = unlock_conditions.get('type', 'private')
            password = unlock_conditions.get('password')
            radius = unlock_conditions.get('radius')
            unlockable_time = unlock_conditions.get('unlockable_time')

        # 处理时间字符串转换
        if unlockable_time and isinstance(unlockable_time, str):
            from datetime import datetime
            try:
                unlockable_time = datetime.strptime(unlockable_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    # 尝试ISO格式
                    unlockable_time = datetime.fromisoformat(unlockable_time.replace('Z', '+00:00'))
                except ValueError:
                    unlockable_time = None

        # 从胶囊位置信息中获取触发位置
        trigger_latitude = None
        trigger_longitude = None
        if capsule_location and len(capsule_location) >= 2:
            trigger_latitude = float(capsule_location[0])
            trigger_longitude = float(capsule_location[1])

        # 创建解锁条件对象
        condition = UnlockCondition(
            capsule_id=capsule_id,
            condition_type=condition_type,
            password=password,
            trigger_latitude=trigger_latitude,
            trigger_longitude=trigger_longitude,
            radius_meters=int(radius) if radius else None,
            unlockable_time=unlockable_time
        )

        self.repository.db.add(condition)
        self.repository.db.commit()

    def _save_media_files(self, capsule_id: int, media_files: List):
        """保存媒体文件到数据库"""
        from app.database.orm.capsule import CapsuleMedia
        from app.model.capsule import MediaFile

        for index, media_file in enumerate(media_files):
            # 处理MediaFile对象
            if isinstance(media_file, MediaFile):
                # MediaFile对象格式
                file_id = media_file.id
                file_type = media_file.type or "unknown"
                file_url = media_file.url or ""
                thumbnail_url = media_file.thumbnail or None
                file_name = f"media_file_{index + 1}"  # 从URL或ID生成文件名
                if media_file.url:
                    file_name = media_file.url.split("/")[-1] if "/" in media_file.url else file_name
                file_size = 0  # MediaFile模型没有size字段
                mime_type = None  # MediaFile模型没有mime_type字段
            elif isinstance(media_file, dict):
                # 字典格式（向后兼容）
                file_id = media_file.get('id') or media_file.get('file_id')
                file_type = media_file.get('type', 'unknown')
                file_url = media_file.get('url', '')
                thumbnail_url = media_file.get('thumbnail')
                file_name = media_file.get('name', f"media_file_{index + 1}")
                file_size = media_file.get('size', 0)
                mime_type = media_file.get('mime_type')
            else:
                # 简单格式（向后兼容）
                file_id = str(media_file)
                file_type = "unknown"
                file_url = ""
                thumbnail_url = None
                file_name = f"media_file_{index + 1}"
                file_size = 0
                mime_type = None

            if not file_id:  # 跳过空值
                continue

            file_id_str = str(file_id)

            # 如果文件类型未知，尝试从文件扩展名推断
            if file_type == "unknown" and "." in file_id_str:
                extension = file_id_str.split(".")[-1].lower()
                if extension in ["jpg", "jpeg", "png", "gif", "webp"]:
                    file_type = "image"
                elif extension in ["mp4", "avi", "mov", "wmv", "flv"]:
                    file_type = "video"
                elif extension in ["mp3", "wav", "flac", "aac"]:
                    file_type = "audio"
                else:
                    file_type = "file"

            # 保存完整的文件URL路径，而不是仅保存文件ID
            # 如果URL为空，尝试通过文件ID构建路径
            if not file_url and file_id_str.startswith("file_"):
                # 从现有的uploads目录中查找文件
                file_url = self._find_file_by_id(file_id_str, file_type)

            # 构建缩略图URL
            thumbnail_path = None
            if thumbnail_url:
                thumbnail_path = thumbnail_url
            elif file_url and file_type == "image":
                # 尝试构建缩略图URL
                thumbnail_path = self._build_thumbnail_url(file_url)

            media_record = CapsuleMedia(
                capsule_id=capsule_id,
                file_type=file_type,
                file_name=file_name,
                file_path=file_url or file_id_str,  # 保存完整的文件URL路径
                file_size=file_size,
                mime_type=mime_type,
                upload_order=index
            )

            self.repository.db.add(media_record)

        self.repository.db.commit()

    def _find_file_by_id(self, file_id: str, file_type: str) -> str:
        """根据文件ID在uploads目录中查找文件"""
        import os
        import glob

        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        if file_type == "image":
            search_pattern = os.path.join(uploads_dir, 'image', '**', f"{file_id}.*")
        elif file_type == "audio":
            search_pattern = os.path.join(uploads_dir, 'audio', '**', f"{file_id}.*")
        else:
            search_pattern = os.path.join(uploads_dir, '**', f"{file_id}.*")

        files = glob.glob(search_pattern, recursive=True)
        if files:
            # 返回相对于uploads目录的路径
            file_path = files[0]
            relative_path = os.path.relpath(file_path, uploads_dir)
            return f"/uploads/{relative_path.replace(os.sep, '/')}"

        return ""

    def _build_thumbnail_url(self, file_url: str) -> str:
        """根据文件URL构建缩略图URL"""
        if "/uploads/image/" in file_url:
            # 从 /uploads/image/20251215/file_xxx.png 构建缩略图路径
            parts = file_url.split('/')
            if len(parts) >= 4:
                # 重新构建缩略图URL: /uploads/image/20251215/thumbnails/file_xxx_thumb.jpg
                thumbnail_url = f"/uploads/{parts[2]}/{parts[3]}/thumbnails/{parts[4].split('.')[0]}_thumb.jpg"
                return thumbnail_url

        return None


# 向后兼容别名
CapsuleManager = CapsuleService