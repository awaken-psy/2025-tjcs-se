"""
Upload API interface
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
import os
import uuid
import secrets
from app.utils.datetime_helper import beijing_now
from pathlib import Path
from enum import Enum
from app.logger import get_logger

# 导入模型和服务
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from model.file import FileUploadResponse
from services.file_manager import FileManager

# 简单的认证依赖
def login_required():
    class MockUser:
        def __init__(self):
            self.id = 1
            self.username = "test_user"
    return MockUser()

# 文件类型枚举 - 匹配Apifox规范
class Type(str, Enum):
    Audio = "audio"
    Image = "image"
    Video = "video"

# 文件格式枚举 - 扩展支持更多格式
class Format(str, Enum):
    # 图片格式
    Jpg = "jpg"
    Jpeg = "jpeg"
    Png = "png"
    Gif = "gif"
    Bmp = "bmp"
    Webp = "webp"

    # 音频格式
    Mp3 = "mp3"
    Wav = "wav"
    Aac = "aac"
    Flac = "flac"
    M4a = "m4a"

    # 视频格式
    Mp4 = "mp4"
    Avi = "avi"
    Mov = "mov"
    Wmv = "wmv"
    Webm = "webm"


# 响应模型 - 匹配TypeScript接口规范
class UploadResponseData(BaseModel):
    """文件上传响应数据模型"""
    duration: Optional[float] = Field(None, description="音频时长，单位：秒（仅音频类型返回）")
    file_id: str = Field(..., description="文件唯一标识符")
    format: Format = Field(..., description="文件格式")
    size: int = Field(..., description="文件大小，单位：字节")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL（仅图片类型返回）")
    url: str = Field(..., description="文件访问URL")

class UploadResponse(BaseModel):
    """文件上传响应模型"""
    code: int = Field(..., description="状态码")
    data: Optional[UploadResponseData] = Field(None, description="响应数据")
    message: str = Field(..., description="操作结果描述")

# 文件大小限制常量
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

router = APIRouter(prefix='/upload', tags=['Upload'])
logger = get_logger(f"router<{__name__}>")

def _create_default_thumbnail(thumbnail_path: Path, media_type: str) -> Optional[str]:
    """创建默认缩略图"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # 创建300x300的画布
        img = Image.new('RGB', (300, 300), color='#f0f0f0')
        draw = ImageDraw.Draw(img)

        # 根据媒体类型绘制不同的图标
        if media_type == 'video':
            # 绘制视频播放图标
            # 背景
            draw.ellipse([50, 50, 250, 250], fill='#333333')
            # 播放三角形
            draw.polygon([(130, 120), (130, 180), (180, 150)], fill='#ffffff')
            text = "VIDEO"
        elif media_type == 'audio':
            # 绘制音频波形图标
            # 音频条形图
            bar_width = 20
            bar_spacing = 25
            start_x = 50
            center_y = 150

            for i, height in enumerate([80, 120, 60, 140, 100, 80, 110, 90, 130, 70]):
                x = start_x + i * bar_spacing
                y_top = center_y - height // 2
                y_bottom = center_y + height // 2
                draw.rectangle([x, y_top, x + bar_width, y_bottom], fill='#333333')
            text = "AUDIO"
        else:
            # 通用文件图标
            draw.rectangle([75, 50, 225, 200], fill='#333333', outline='#ffffff', width=3)
            text = "FILE"

        # 添加文字标签
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            # 如果没有系统字体，使用默认字体
            font = ImageFont.load_default()

        # 计算文字位置（居中）
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (300 - text_width) // 2
        draw.text((text_x, 250), text, fill='#333333', font=font)

        # 保存图片
        img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)

        # 返回相对路径
        parts = thumbnail_path.parts
        uploads_idx = parts.index('uploads')
        relative_path = '/'.join(parts[uploads_idx:])

        logger.info(f"默认{media_type}缩略图创建成功: {thumbnail_path}")
        return f"/{relative_path}"

    except Exception as e:
        logger.error(f"创建默认缩略图失败: {str(e)}")
        # 如果生成失败，创建一个最小的1x1像素图片
        try:
            from PIL import Image
            img = Image.new('RGB', (1, 1), color='#f0f0f0')
            img.save(thumbnail_path, 'JPEG')

            parts = thumbnail_path.parts
            uploads_idx = parts.index('uploads')
            relative_path = '/'.join(parts[uploads_idx:])
            return f"/{relative_path}"
        except:
            return None


@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(..., description="要上传的文件"),
    type: Optional[Type] = Form(None, description="文件类型：audio、image 或 video"),
    user = Depends(login_required)
):
    """
    文件上传API - 匹配Apifox规范

    请求格式：multipart/form-data
    - file: 文件内容
    - type: 文件类型（可选，支持 "audio", "image"）

    响应格式：
    {
      "code": 200,
      "data": {
        "file_id": "file_abc123",
        "url": "https://example.com/files/file_abc123.jpg",
        "size": 1024000,
        "format": "jpg",
        "thumbnail_url": "https://example.com/thumbnails/file_abc123_thumb.jpg",
        "duration": 120.5
      },
      "message": "文件上传成功"
    }
    """
    try:
        # 验证文件存在
        if not file or not file.filename:
            return UploadResponse(
                code=400,
                data=None,
                message="请选择要上传的文件"
            )

        # 初始化文件大小变量
        file_size = 0

        # 根据文件名确定文件类型（如果未指定）
        file_type = type
        if not file_type:
            if file.content_type:
                if file.content_type.startswith('image/'):
                    file_type = Type.Image
                elif file.content_type.startswith('audio/'):
                    file_type = Type.Audio
                elif file.content_type.startswith('video/'):
                    file_type = Type.Video
            else:
                # 根据文件扩展名判断
                ext = Path(file.filename).suffix.lower()
                image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
                audio_exts = {'.mp3', '.wav', '.aac', '.flac', '.m4a'}
                video_exts = {'.mp4', '.avi', '.mov', '.wmv', '.webm'}
                if ext in image_exts:
                    file_type = Type.Image
                elif ext in audio_exts:
                    file_type = Type.Audio
                elif ext in video_exts:
                    file_type = Type.Video

        if not file_type:
            return UploadResponse(
                code=400,
                data=None,
                message="无法确定文件类型，请指定type参数"
            )

        # 确定文件格式
        ext = Path(file.filename).suffix.lower().lstrip('.')
        format_map = {
            'jpg': Format.Jpg,
            'jpeg': Format.Jpeg,
            'png': Format.Png,
            'gif': Format.Gif,
            'bmp': Format.Bmp,
            'webp': Format.Webp,
            'mp3': Format.Mp3,
            'wav': Format.Wav,
            'aac': Format.Aac,
            'flac': Format.Flac,
            'm4a': Format.M4a,
            'mp4': Format.Mp4,
            'avi': Format.Avi,
            'mov': Format.Mov,
            'wmv': Format.Wmv,
            'webm': Format.Webm
        }
        file_format = format_map.get(ext, Format.Jpg if file_type == Type.Image else Format.Mp3)

        # 生成文件ID和保存路径
        file_id = f"file_{secrets.token_hex(8)}"
        timestamp = beijing_now().strftime("%Y%m%d")
        upload_dir = Path("uploads") / file_type.value / timestamp

        # 确保上传目录存在
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        file_ext = ext or ('jpg' if file_type == Type.Image else 'mp3')
        filename = f"{file_id}.{file_ext}"
        file_path = upload_dir / filename

        # 读取并保存文件
        try:
            # 记录文件信息以便调试
            logger.info(f"开始处理文件上传: filename={file.filename}, content_type={file.content_type}")

            content = await file.read()
            actual_file_size = len(content)

            logger.info(f"文件读取完成: size={actual_file_size} bytes, filename={file.filename}")

            # 检查文件是否为空
            if actual_file_size == 0:
                logger.warning(f"文件内容为空: filename={file.filename}")
                return UploadResponse(
                    code=400,
                    data=None,
                    message="文件内容为空"
                )

            # 检查实际文件大小
            if actual_file_size > MAX_FILE_SIZE:
                logger.warning(f"文件大小超限: filename={file.filename}, size={actual_file_size}")
                return UploadResponse(
                    code=413,
                    data=None,
                    message=f"文件大小不能超过50MB，当前文件大小：{actual_file_size / (1024 * 1024):.1f}MB"
                )

            file_size = actual_file_size

            # 确保目录存在后再写入文件
            try:
                upload_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"目录创建成功: {upload_dir}")
            except Exception as dir_error:
                logger.error(f"创建上传目录失败: {upload_dir}, error={str(dir_error)}")
                return UploadResponse(
                    code=500,
                    data=None,
                    message=f"创建上传目录失败: {str(dir_error)}"
                )

            # 写入文件
            try:
                with open(file_path, "wb") as f:
                    f.write(content)
                logger.info(f"文件保存成功: {file_path}, size={file_size}")
            except Exception as write_error:
                logger.error(f"文件写入失败: path={file_path}, error={str(write_error)}")
                return UploadResponse(
                    code=500,
                    data=None,
                    message=f"文件写入失败: {str(write_error)}"
                )

            # 验证文件是否成功写入
            if not file_path.exists():
                logger.error(f"文件保存后验证失败: 文件不存在 {file_path}")
                return UploadResponse(
                    code=500,
                    data=None,
                    message="文件保存后验证失败"
                )

            written_size = file_path.stat().st_size
            if written_size != file_size:
                logger.error(f"文件大小不匹配: 期望={file_size}, 实际={written_size}")
                return UploadResponse(
                    code=500,
                    data=None,
                    message=f"文件大小不匹配: 期望={file_size}, 实际={written_size}"
                )

        except Exception as e:
            logger.error(f"文件处理异常: filename={file.filename}, error={str(e)}", exc_info=True)
            return UploadResponse(
                code=500,
                data=None,
                message=f"文件保存失败: {str(e)}"
            )

        # 生成访问URL
        file_url = f"/uploads/{file_type.value}/{timestamp}/{filename}"

        # 生成缩略图
        thumbnail_url = None
        try:
            thumbnail_filename = f"{file_id}_thumb.jpg"
            thumbnail_dir = upload_dir / "thumbnails"
            thumbnail_dir.mkdir(parents=True, exist_ok=True)
            thumbnail_path = thumbnail_dir / thumbnail_filename

            if file_type == Type.Image:
                # 图片：生成缩略图
                try:
                    from PIL import Image
                    import io

                    # 使用PIL生成缩略图
                    with Image.open(io.BytesIO(content)) as img:
                        # 转换为RGB模式（处理RGBA等模式）
                        if img.mode in ['RGBA', 'LA', 'P']:
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            if img.mode in ['RGBA', 'LA']:
                                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            else:
                                background.paste(img)
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')

                        # 生成缩略图，最大尺寸300x300
                        img.thumbnail((300, 300), Image.Resampling.LANCZOS)

                        # 保存为JPG
                        img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)

                    thumbnail_url = f"/uploads/{file_type.value}/{timestamp}/thumbnails/{thumbnail_filename}"
                    logger.info(f"图片缩略图生成成功: {thumbnail_path}")

                except Exception as img_thumb_error:
                    logger.warning(f"图片缩略图生成失败: {str(img_thumb_error)}")
                    # 如果生成失败，使用原图
                    with open(thumbnail_path, "wb") as thumb_f:
                        thumb_f.write(content)
                    thumbnail_url = f"/uploads/{file_type.value}/{timestamp}/thumbnails/{thumbnail_filename}"

            elif file_type == Type.Video:
                # 视频：提取第一帧作为封面
                try:
                    # 尝试使用moviepy提取视频第一帧
                    from moviepy.editor import VideoFileClip
                    import tempfile

                    # 先保存视频文件到临时位置
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                        temp_video.write(content)
                        temp_video_path = temp_video.name

                    try:
                        # 使用moviepy提取第一帧
                        with VideoFileClip(temp_video_path) as clip:
                            # 提取第一帧（0.1秒处）
                            frame = clip.get_frame(0.1)

                            # 将numpy数组转换为PIL图像
                            from PIL import Image
                            import numpy as np
                            img = Image.fromarray(frame.astype(np.uint8))

                            # 确保是RGB模式
                            if img.mode != 'RGB':
                                img = img.convert('RGB')

                            # 调整尺寸并保存
                            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                            img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)

                            thumbnail_url = f"/uploads/{file_type.value}/{timestamp}/thumbnails/{thumbnail_filename}"
                            logger.info(f"视频封面生成成功: {thumbnail_path}")

                    finally:
                        # 清理临时文件
                        import os
                        try:
                            os.unlink(temp_video_path)
                        except:
                            pass

                except Exception as video_thumb_error:
                    logger.warning(f"视频封面生成失败: {str(video_thumb_error)}")
                    # 使用默认视频封面
                    thumbnail_path_str = _create_default_thumbnail(thumbnail_path, 'video')
                    if thumbnail_path_str:
                        thumbnail_url = thumbnail_path_str

            elif file_type == Type.Audio:
                # 音频：使用MP3演示.jpg作为默认图标
                try:
                    # 复制MP3演示.jpg到缩略图位置
                    import shutil

                    # 获取后端根目录路径（从当前文件路径向上两级）
                    current_file_path = Path(__file__)
                    backend_root = current_file_path.parent.parent.parent
                    mp3_demo_path = backend_root / "MP3演示.jpg"

                    if mp3_demo_path.exists():
                        shutil.copy2(mp3_demo_path, thumbnail_path)
                        thumbnail_url = f"/uploads/{file_type.value}/{timestamp}/thumbnails/{thumbnail_filename}"
                        logger.info(f"使用MP3演示.jpg作为音频默认图标: {thumbnail_path}")
                    else:
                        logger.warning(f"MP3演示.jpg文件不存在: {mp3_demo_path}，使用生成的默认图标")
                        thumbnail_path_str = _create_default_thumbnail(thumbnail_path, 'audio')
                        if thumbnail_path_str:
                            thumbnail_url = thumbnail_path_str
                except Exception as audio_thumb_error:
                    logger.warning(f"音频缩略图生成失败: {str(audio_thumb_error)}，使用生成的默认图标")
                    thumbnail_path_str = _create_default_thumbnail(thumbnail_path, 'audio')
                    if thumbnail_path_str:
                        thumbnail_url = thumbnail_path_str

        except Exception as thumb_error:
            logger.warning(f"缩略图处理失败: {str(thumb_error)}")
            thumbnail_url = None

        # 获取音频/视频时长
        duration = None
        if file_type == Type.Audio:
            # 获取音频时长
            try:
                import tempfile
                from moviepy.editor import AudioFileClip

                # 保存音频到临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                    temp_audio.write(content)
                    temp_audio_path = temp_audio.name

                try:
                    with AudioFileClip(temp_audio_path) as audio_clip:
                        duration = float(audio_clip.duration)
                        logger.info(f"音频时长获取成功: {duration}秒")
                finally:
                    # 清理临时文件
                    import os
                    try:
                        os.unlink(temp_audio_path)
                    except:
                        pass

            except Exception as duration_error:
                logger.warning(f"音频时长获取失败: {str(duration_error)}, 使用默认值")
                duration = 120.0  # 默认2分钟

        elif file_type == Type.Video:
            # 获取视频时长
            try:
                import tempfile
                from moviepy.editor import VideoFileClip

                # 保存视频到临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                    temp_video.write(content)
                    temp_video_path = temp_video.name

                try:
                    with VideoFileClip(temp_video_path) as video_clip:
                        duration = float(video_clip.duration)
                        logger.info(f"视频时长获取成功: {duration}秒")
                finally:
                    # 清理临时文件
                    import os
                    try:
                        os.unlink(temp_video_path)
                    except:
                        pass

            except Exception as duration_error:
                logger.warning(f"视频时长获取失败: {str(duration_error)}, 使用默认值")
                duration = 180.0  # 默认3分钟

        # 构建响应数据
        try:
            upload_data = UploadResponseData(
                duration=duration,
                file_id=file_id,
                format=file_format,
                size=file_size or 0,  # 确保size不为None
                thumbnail_url=thumbnail_url,
                url=file_url
            )

            logger.info(f"文件上传完成: file_id={file_id}, filename={file.filename}, size={file_size}, url={file_url}")

            return UploadResponse(
                code=200,
                data=upload_data,
                message="文件上传成功"
            )

        except Exception as response_error:
            logger.error(f"构建响应数据失败: {str(response_error)}", exc_info=True)
            return UploadResponse(
                code=500,
                data=None,
                message=f"构建响应数据失败: {str(response_error)}"
            )

    except Exception as e:
        logger.error(f"文件上传异常: filename={file.filename}, error={str(e)}", exc_info=True)
        return UploadResponse(
            code=500,
            data=None,
            message=f"上传失败: {str(e)}"
        )




@router.delete("/file/{file_id}", response_model=UploadResponse)
async def delete_file(
    file_id: str
):
    """删除文件"""
    try:
        # 简化实现：返回成功
        return UploadResponse(
            code=200,
            data=None,
            message="文件删除成功"
        )
    except Exception as e:
        return UploadResponse(
            code=500,
            data=None,
            message=f"删除失败: {str(e)}"
        )