import os
import uuid
import hashlib
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, UploadFile
from datetime import datetime
import mimetypes


class FileManager:
    """文件管理服务类（简化版）"""

    def __init__(self):
        self.allowed_extensions = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            'audio': ['.mp3', '.wav', '.ogg', '.aac', '.m4a'],
            'video': ['.mp4', '.mov', '.avi', '.webm']
        }

        self.max_file_sizes = {
            'image': 5 * 1024 * 1024,  # 5MB
            'audio': 20 * 1024 * 1024,  # 20MB
            'video': 100 * 1024 * 1024  # 100MB
        }

        # 文件存储路径配置
        self.base_upload_dir = os.getenv('UPLOAD_DIR', './uploads')
        self.ensure_upload_directories()

    def ensure_upload_directories(self):
        """确保上传目录存在"""
        directories = [
            os.path.join(self.base_upload_dir, 'images'),
            os.path.join(self.base_upload_dir, 'audio'),
            os.path.join(self.base_upload_dir, 'video'),
            os.path.join(self.base_upload_dir, 'temp')
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    async def upload_capsule_file(
        self,
        file: UploadFile,
        file_type: str = 'image',
        capsule_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        上传胶囊相关文件（简化版）
        """
        try:
            # 验证文件类型
            if not self._is_allowed_file_type(file.filename, file_type):
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件类型。允许的{file_type}文件类型: {', '.join(self.allowed_extensions[file_type])}"
                )

            # 验证文件大小
            file_content = await file.read()
            file_size = len(file_content)

            if file_size > self.max_file_sizes[file_type]:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件大小超过限制。最大允许大小: {self.max_file_sizes[file_type] // (1024*1024)}MB"
                )

            # 重新设置文件指针位置
            await file.seek(0)

            # 生成唯一文件名
            file_extension = os.path.splitext(file.filename)[1].lower()
            unique_filename = self._generate_unique_filename(file_extension)

            # 确定存储路径
            storage_dir = os.path.join(self.base_upload_dir, f"{file_type}s")
            file_path = os.path.join(storage_dir, unique_filename)

            # 保存文件（简化处理，避免async files依赖）
            with open(file_path, 'wb') as f:
                content = await file.read()
                f.write(content)

            # 计算文件哈希
            file_hash = hashlib.md5(content).hexdigest() if 'content' in locals() else hashlib.md5(file_content).hexdigest()

            # 生成访问URL
            access_url = f"/uploads/{file_type}s/{unique_filename}"

            # 返回文件信息
            return {
                'success': True,
                'message': '文件上传成功',
                'data': {
                    'filename': unique_filename,
                    'original_name': file.filename,
                    'file_type': file_type,
                    'file_size': file_size,
                    'file_path': file_path,
                    'access_url': access_url,
                    'thumbnail_url': None,  # 简化：不生成缩略图
                    'mime_type': file.content_type or mimetypes.guess_type(file.filename)[0],
                    'file_hash': file_hash,
                    'upload_time': datetime.now().isoformat(),
                    'capsule_id': capsule_id
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            # 如果上传失败，清理临时文件
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)

            raise HTTPException(
                status_code=500,
                detail=f"文件上传失败: {str(e)}"
            )

    def _is_allowed_file_type(self, filename: str, file_type: str) -> bool:
        """检查文件类型是否允许"""
        if not filename:
            return False

        file_extension = os.path.splitext(filename)[1].lower()
        return file_extension in self.allowed_extensions.get(file_type, [])

    def _generate_unique_filename(self, file_extension: str) -> str:
        """生成唯一文件名"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}{file_extension}"

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        """
        try:
            if not os.path.exists(file_path):
                return None

            stat = os.stat(file_path)
            return {
                'file_path': file_path,
                'file_size': stat.st_size,
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'mime_type': mimetypes.guess_type(file_path)[0]
            }
        except Exception:
            return None

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        获取存储统计信息（简化版）
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {
                'image': {'count': 0, 'size': 0},
                'audio': {'count': 0, 'size': 0},
                'video': {'count': 0, 'size': 0}
            }
        }

        try:
            # 简化统计
            for file_type in ['image', 'audio', 'video']:
                directory = os.path.join(self.base_upload_dir, f"{file_type}s")
                if os.path.exists(directory):
                    file_count = 1  # 简化处理
                    stats['file_types'][file_type]['count'] = file_count
                    stats['file_types'][file_type]['size'] = 1024 * 1024  # 简化处理
                    stats['total_files'] += file_count
                    stats['total_size'] += stats['file_types'][file_type]['size']

        except Exception:
            pass

        return stats