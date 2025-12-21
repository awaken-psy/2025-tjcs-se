"""
多媒体文件处理工具
支持图片格式转换、文件验证等功能
"""
import os
import uuid
import tempfile
import secrets
from typing import Optional, Tuple, Union
from pathlib import Path
from PIL import Image

# 尝试导入 magic，如果失败则使用备用方案
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

# 支持的图片格式
SUPPORTED_IMAGE_FORMATS = {
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'
}

# 支持的音频格式
SUPPORTED_AUDIO_FORMATS = {
    'mp3', 'wav', 'aac', 'flac', 'm4a', 'ogg'
}

# 支持的视频格式
SUPPORTED_VIDEO_FORMATS = {
    'mp4', 'avi', 'mov', 'wmv', 'webm', 'mkv', 'flv'
}

# 需要转换的图片格式（转换为标准格式）
CONVERT_IMAGE_FORMATS = {
    'bmp': 'jpg',
    'tiff': 'jpg',
    'tif': 'jpg',
    'webp': 'jpg'
}

def get_file_type_from_content(content: bytes) -> str:
    """通过文件内容检测真实的文件类型"""
    if MAGIC_AVAILABLE:
        try:
            mime = magic.from_buffer(content, mime=True)
            if mime.startswith('image/'):
                return 'image'
            elif mime.startswith('audio/'):
                return 'audio'
            elif mime.startswith('video/'):
                return 'video'
            else:
                return 'unknown'
        except:
            pass

    # 备用方案：通过文件头检测
    if len(content) >= 8:
        # 检测图片文件头
        if content.startswith(b'\xFF\xD8\xFF'):
            return 'image'  # JPEG
        elif content.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'image'  # PNG
        elif content.startswith(b'GIF8'):
            return 'image'  # GIF
        elif content.startswith(b'BM'):
            return 'image'  # BMP
        elif content.startswith(b'RIFF') and len(content) >= 12:
            # 检测 WebP, AVI, WAV
            if content[8:12] == b'WEBP':
                return 'image'  # WebP
            elif content[8:12] == b'AVI ':
                return 'video'  # AVI
            elif content[8:12] == b'WAVE':
                return 'audio'  # WAV
        # 检测 MP3
        elif content[0:2] in [b'ID3', b'\xFF\xFB', b'\xFF\xF3', b'\xFF\xF2']:
            return 'audio'  # MP3
        # 检测 MP4/QuickTime
        elif content[4:8] in [b'ftyp', b'mdat']:
            # 进一步检测文件类型
            if len(content) >= 16:
                # 检查 ftyp 盒子来确定具体格式
                if content[4:8] == b'ftyp':
                    brand = content[8:12]
                    if brand in [b'qt  ', b'moov']:  # QuickTime
                        return 'video'  # MOV
                    elif brand in [b'isom', b'iso2', b'iso3', b'iso4', b'iso5', b'iso6',
                                   b'mp41', b'mp42', b'avc1', b'hvc1', b'hevc']:  # MP4
                        return 'video'  # MP4
            return 'video'  # 默认视频

    return 'unknown'

def get_file_format_from_content(content: bytes, filename: str) -> str:
    """通过文件内容检测真实的文件格式"""
    if MAGIC_AVAILABLE:
        try:
            # 使用 magic 检测文件类型
            mime = magic.from_buffer(content, mime=True)

            # 映射 MIME 类型到文件扩展名
            mime_to_format = {
                'image/jpeg': 'jpg',
                'image/jpg': 'jpg',
                'image/png': 'png',
                'image/gif': 'gif',
                'image/bmp': 'bmp',
                'image/webp': 'webp',
                'image/tiff': 'tiff',
                'audio/mpeg': 'mp3',
                'audio/wav': 'wav',
                'audio/mp4': 'm4a',
                'audio/aac': 'aac',
                'audio/flac': 'flac',
                'audio/ogg': 'ogg',
                'video/mp4': 'mp4',
                'video/avi': 'avi',
                'video/quicktime': 'mov',
                'video/x-ms-wmv': 'wmv',
                'video/webm': 'webm',
                'video/x-matroska': 'mkv',
                'video/x-flv': 'flv'
            }

            file_format = mime_to_format.get(mime)
            if file_format:
                return file_format

        except:
            pass

    # 备用方案：通过文件头检测格式
    if len(content) >= 8:
        if content.startswith(b'\xFF\xD8\xFF'):
            return 'jpg'
        elif content.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'png'
        elif content.startswith(b'GIF8'):
            return 'gif'
        elif content.startswith(b'BM'):
            return 'bmp'
        elif content.startswith(b'RIFF') and len(content) >= 12:
            if content[8:12] == b'WEBP':
                return 'webp'
            elif content[8:12] == b'AVI ':
                return 'avi'
            elif content[8:12] == b'WAVE':
                return 'wav'
        elif content[0:2] in [b'ID3', b'\xFF\xFB', b'\xFF\xF3', b'\xFF\xF2']:
            return 'mp3'
        elif content[4:8] in [b'ftyp', b'mdat']:
            # 进一步检测MP4 vs MOV
            if len(content) >= 16 and content[4:8] == b'ftyp':
                brand = content[8:12]
                if brand in [b'qt  ', b'moov']:  # QuickTime
                    return 'mov'
                elif brand in [b'isom', b'iso2', b'iso3', b'iso4', b'iso5', b'iso6',
                               b'mp41', b'mp42', b'avc1', b'hvc1', b'hevc']:  # MP4
                    return 'mp4'
            return 'mp4'  # 默认MP4

    # 如果检测失败，使用文件扩展名
    return Path(filename).suffix.lower().lstrip('.')

def is_supported_image_format(format_str: str) -> bool:
    """检查是否为支持的图片格式"""
    return format_str.lower() in SUPPORTED_IMAGE_FORMATS

def is_supported_audio_format(format_str: str) -> bool:
    """检查是否为支持的音频格式"""
    return format_str.lower() in SUPPORTED_AUDIO_FORMATS

def is_supported_video_format(format_str: str) -> bool:
    """检查是否为支持的视频格式"""
    return format_str.lower() in SUPPORTED_VIDEO_FORMATS

def convert_image_format(input_path: str, output_path: str, target_format: str = 'jpg', quality: int = 85) -> Tuple[bool, str]:
    """
    转换图片格式

    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        target_format: 目标格式 (jpg, png, webp)
        quality: 图片质量 (1-100)

    Returns:
        Tuple[bool, str]: (是否成功, 错误信息或成功信息)
    """
    try:
        with Image.open(input_path) as img:
            # 处理透明通道（JPG不支持透明度）
            if target_format.lower() in ['jpg', 'jpeg'] and img.mode in ['RGBA', 'LA']:
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])  # 使用 alpha 通道作为 mask
                else:
                    background.paste(img)
                img = background
            elif target_format.lower() == 'png' and img.mode not in ['RGBA', 'RGB', 'L']:
                img = img.convert('RGBA')
            elif img.mode not in ['RGB', 'RGBA', 'L']:
                img = img.convert('RGB')

            # 保存转换后的图片
            save_kwargs = {}
            if target_format.lower() in ['jpg', 'jpeg']:
                save_kwargs = {'quality': quality, 'optimize': True}
            elif target_format.lower() == 'png':
                save_kwargs = {'optimize': True}
            elif target_format.lower() == 'webp':
                save_kwargs = {'quality': quality, 'optimize': True}

            img.save(output_path, format=target_format.upper(), **save_kwargs)

        return True, f"图片格式已转换为 {target_format.upper()}"

    except Exception as e:
        return False, f"图片格式转换失败: {str(e)}"

def process_uploaded_file(
    content: bytes,
    filename: str,
    target_dir: Path,
    file_type: Optional[str] = None
) -> Tuple[bool, str, dict]:
    """
    处理上传的文件，包括格式验证和转换

    Args:
        content: 文件内容
        filename: 原始文件名
        target_dir: 目标保存目录
        file_type: 指定的文件类型 (image, audio, video)

    Returns:
        Tuple[bool, str, dict]: (是否成功, 消息, 文件信息)
    """
    try:
        # 检测真实文件类型
        detected_type = get_file_type_from_content(content)
        detected_format = get_file_format_from_content(content, filename)

        # 验证文件类型
        if file_type and detected_type != 'unknown' and detected_type != file_type:
            return False, f"文件类型不匹配，检测到类型: {detected_type}，期望类型: {file_type}", {}

        # 如果未检测到类型，使用指定类型或根据扩展名推断
        if detected_type == 'unknown':
            if file_type:
                detected_type = file_type
            else:
                # 根据扩展名推断
                ext = Path(filename).suffix.lower().lstrip('.')
                if ext in SUPPORTED_IMAGE_FORMATS:
                    detected_type = 'image'
                elif ext in SUPPORTED_AUDIO_FORMATS:
                    detected_type = 'audio'
                elif ext in SUPPORTED_VIDEO_FORMATS:
                    detected_type = 'video'
                else:
                    return False, f"不支持的文件格式: {ext}", {}

        # 生成文件ID和基础文件名
        file_id = f"file_{secrets.token_hex(8)}"
        base_filename = file_id
        final_format = detected_format
        converted = False
        conversion_message = ""

        # 处理图片格式转换
        if detected_type == 'image':
            if detected_format.lower() in CONVERT_IMAGE_FORMATS:
                # 需要转换的格式
                target_format = CONVERT_IMAGE_FORMATS[detected_format.lower()]
                temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{detected_format}')
                temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{target_format}')

                try:
                    # 写入临时文件
                    temp_input.write(content)
                    temp_input.close()
                    temp_output.close()

                    # 转换格式
                    success, message = convert_image_format(temp_input.name, temp_output.name, target_format)

                    if success:
                        # 读取转换后的文件
                        with open(temp_output.name, 'rb') as f:
                            converted_content = f.read()
                        content = converted_content
                        final_format = target_format
                        converted = True
                        conversion_message = message
                    else:
                        # 转换失败，使用原文件
                        conversion_message = f"格式转换失败，使用原格式: {message}"

                finally:
                    # 清理临时文件
                    try:
                        os.unlink(temp_input.name)
                        os.unlink(temp_output.name)
                    except:
                        pass

        # 生成最终文件名
        filename = f"{base_filename}.{final_format}"
        file_path = target_dir / filename
        relative_path = f"/uploads/{detected_type}/{target_dir.name}/{filename}"

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(content)

        # 获取文件信息
        file_size = len(content)
        duration = None

        # 对于音频/视频文件，可以在这里添加时长获取逻辑
        # 这里简化处理，实际可以使用 moviepy 等库获取时长

        file_info = {
            'file_id': file_id,
            'filename': filename,
            'file_path': str(file_path),
            'relative_path': relative_path,
            'file_size': file_size,
            'file_format': final_format,
            'file_type': detected_type,
            'converted': converted,
            'conversion_message': conversion_message,
            'duration': duration
        }

        success_message = f"文件上传成功"
        if converted:
            success_message += f"，{conversion_message}"

        return True, success_message, file_info

    except Exception as e:
        return False, f"文件处理失败: {str(e)}", {}

def validate_file_size(content: bytes, max_size: int = 50 * 1024 * 1024) -> Tuple[bool, str]:
    """验证文件大小"""
    file_size = len(content)
    if file_size > max_size:
        size_mb = file_size / (1024 * 1024)
        max_mb = max_size / (1024 * 1024)
        return False, f"文件大小超过限制，当前: {size_mb:.1f}MB，最大: {max_mb:.1f}MB"
    return True, ""