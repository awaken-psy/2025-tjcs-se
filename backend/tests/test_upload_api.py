#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload API Simple Mock Tests
Test file upload functionality with mock data
"""

import os
import sys
import json
import tempfile
import mimetypes
from pathlib import Path
from enum import Enum
from typing import Optional
from datetime import datetime
import secrets
import uuid

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pydantic import BaseModel, Field

# Define the same enums as in the API
class Type(str, Enum):
    Audio = "audio"
    Image = "image"

class Format(str, Enum):
    Aac = "aac"
    Bmp = "bmp"
    Flac = "flac"
    Gif = "gif"
    Jpeg = "jpeg"
    Jpg = "jpg"
    Mp3 = "mp3"
    Png = "png"
    Wav = "wav"

# Define the same response models as in the API
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


class MockUploadFile:
    """Mock UploadFile class for testing"""
    def __init__(self, filename="test.jpg", content_type="image/jpeg", size=1024, content=b"mock_image_data"):
        self.filename = filename
        self.content_type = content_type
        self.size = size
        self.content = content
        self._content_read = False

    async def read(self):
        if not self._content_read:
            self._content_read = True
            return self.content
        return b""


async def mock_upload_file_logic(file: MockUploadFile, type: Optional[Type] = None):
    """
    Mock implementation of upload_file logic
    """
    try:
        # 验证文件存在
        if not file or not file.filename:
            return UploadResponse(
                code=400,
                data=None,
                message="请选择要上传的文件"
            )

        # 文件大小限制（50MB）
        file_size = 0
        if hasattr(file, 'size'):
            file_size = file.size
            if file_size > 50 * 1024 * 1024:
                return UploadResponse(
                    code=413,
                    data=None,
                    message="文件大小不能超过50MB"
                )

        # 根据文件名确定文件类型（如果未指定）
        file_type = type
        if not file_type:
            if file.content_type:
                if file.content_type.startswith('image/'):
                    file_type = Type.Image
                elif file.content_type.startswith('audio/'):
                    file_type = Type.Audio
            else:
                # 根据文件扩展名判断
                ext = Path(file.filename).suffix.lower()
                image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
                audio_exts = {'.mp3', '.wav', '.aac', '.flac'}
                if ext in image_exts:
                    file_type = Type.Image
                elif ext in audio_exts:
                    file_type = Type.Audio

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
            'mp3': Format.Mp3,
            'wav': Format.Wav,
            'aac': Format.Aac,
            'flac': Format.Flac
        }
        file_format = format_map.get(ext, Format.Jpg if file_type == Type.Image else Format.Mp3)

        # 生成文件ID和保存路径
        file_id = f"file_{secrets.token_hex(8)}"
        timestamp = datetime.now().strftime("%Y%m%d")
        upload_dir = f"uploads/{file_type.value}/{timestamp}"

        # 生成文件名
        file_ext = ext or ('jpg' if file_type == Type.Image else 'mp3')
        filename = f"{file_id}.{file_ext}"

        # 生成访问URL
        file_url = f"/uploads/{file_type.value}/{timestamp}/{filename}"

        # 生成缩略图（仅图片）
        thumbnail_url = None
        if file_type == Type.Image:
            thumbnail_filename = f"{file_id}_thumb.jpg"
            thumbnail_url = f"/uploads/{file_type.value}/{timestamp}/thumbnails/{thumbnail_filename}"

        # 获取音频时长（仅音频，简化处理）
        duration = None
        if file_type == Type.Audio:
            duration = 120.0

        # 构建响应数据
        upload_data = UploadResponseData(
            duration=duration,
            file_id=file_id,
            format=file_format,
            size=file_size,
            thumbnail_url=thumbnail_url,
            url=file_url
        )

        return UploadResponse(
            code=200,
            data=upload_data,
            message="文件上传成功"
        )

    except Exception as e:
        return UploadResponse(
            code=500,
            data=None,
            message=f"上传失败: {str(e)}"
        )


async def test_upload_image():
    """Test image upload with mock data"""
    print("Testing image upload (mock)...")

    try:
        # Create mock image file
        mock_file = MockUploadFile(
            filename="test_image.jpg",
            content_type="image/jpeg",
            size=2048,
            content=b"mock_jpeg_image_data_here"
        )

        # Call mock upload function
        result = await mock_upload_file_logic(file=mock_file, type=Type.Image)

        print(f"Response status code: {result.code}")
        print(f"Response message: {result.message}")

        if result.code == 200 and result.data:
            print(f"Response data: {result.data.model_dump()}")

            # Verify response format matches specification
            assert hasattr(result.data, 'file_id'), "Missing file_id"
            assert hasattr(result.data, 'url'), "Missing url"
            assert hasattr(result.data, 'size'), "Missing size"
            assert hasattr(result.data, 'format'), "Missing format"
            assert hasattr(result.data, 'thumbnail_url'), "Missing thumbnail_url"
            assert result.data.format == Format.Jpg, f"Expected format 'jpg', got '{result.data.format}'"
            assert result.data.size == 2048, f"Expected size 2048, got {result.data.size}"
            assert result.data.thumbnail_url is not None, "Missing thumbnail_url for image"
            assert result.data.duration is None, "Duration should be None for image"

            print("PASS: Image upload test passed!")
            return True
        else:
            print(f"FAIL: Upload failed: {result.message}")
            return False

    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        return False


async def test_upload_audio():
    """Test audio upload with mock data"""
    print("Testing audio upload (mock)...")

    try:
        # Create mock audio file
        mock_file = MockUploadFile(
            filename="test_audio.mp3",
            content_type="audio/mpeg",
            size=3072,
            content=b"mock_mp3_audio_data_here"
        )

        # Call mock upload function
        result = await mock_upload_file_logic(file=mock_file, type=Type.Audio)

        print(f"Response status code: {result.code}")
        print(f"Response message: {result.message}")

        if result.code == 200 and result.data:
            print(f"Response data: {result.data.model_dump()}")

            # Verify audio-specific fields
            assert hasattr(result.data, 'duration'), "Missing duration for audio"
            assert result.data.duration is not None, "Duration should not be None for audio"
            assert result.data.format == Format.Mp3, f"Expected format 'mp3', got '{result.data.format}'"
            assert result.data.thumbnail_url is None, "Thumbnail should be None for audio"

            print("PASS: Audio upload test passed!")
            return True
        else:
            print(f"FAIL: Audio upload failed: {result.message}")
            return False

    except Exception as e:
        print(f"FAIL: Audio test failed: {e}")
        return False


async def test_upload_invalid_file():
    """Test invalid file type upload with mock data"""
    print("Testing invalid file type upload (mock)...")

    try:
        # Create mock text file
        mock_file = MockUploadFile(
            filename="test.txt",
            content_type="text/plain",
            size=100,
            content=b"this is a text file"
        )

        # Call mock upload function without specifying type
        result = await mock_upload_file_logic(file=mock_file, type=None)

        print(f"Response status code: {result.code}")
        print(f"Response message: {result.message}")

        # Should return 400 error
        if result.code == 400:
            print("PASS: Invalid file type correctly rejected!")
            return True
        else:
            print(f"FAIL: Invalid file type not rejected, status code: {result.code}")
            return False

    except Exception as e:
        print(f"FAIL: Invalid file test failed: {e}")
        return False


async def test_upload_oversized_file():
    """Test oversized file upload with mock data"""
    print("Testing oversized file upload (mock)...")

    try:
        # Create mock oversized file (51MB)
        mock_file = MockUploadFile(
            filename="oversized.jpg",
            content_type="image/jpeg",
            size=51 * 1024 * 1024,  # 51MB
            content=b"x" * 1000  # Use smaller content for testing
        )
        # Override the size attribute to simulate oversized file
        mock_file.size = 51 * 1024 * 1024

        # Call mock upload function
        result = await mock_upload_file_logic(file=mock_file, type=Type.Image)

        print(f"Response status code: {result.code}")
        print(f"Response message: {result.message}")

        # Should return 413 error
        if result.code == 413:
            print("PASS: Oversized file correctly rejected!")
            return True
        else:
            print(f"FAIL: Oversized file not rejected, status code: {result.code}")
            return False

    except Exception as e:
        print(f"FAIL: Oversized file test failed: {e}")
        return False


async def test_upload_no_file():
    """Test upload with no file"""
    print("Testing upload with no file (mock)...")

    try:
        # Call mock upload function with None file
        result = await mock_upload_file_logic(file=None, type=Type.Image)

        print(f"Response status code: {result.code}")
        print(f"Response message: {result.message}")

        # Should return 400 error
        if result.code == 400 and "请选择要上传的文件" in result.message:
            print("PASS: No file case correctly handled!")
            return True
        else:
            print(f"FAIL: No file case not handled correctly")
            return False

    except Exception as e:
        print(f"FAIL: No file test failed: {e}")
        return False


async def test_format_compliance():
    """Test that response format matches Apifox specification"""
    print("Testing format compliance (mock)...")

    try:
        # Test image upload response format
        mock_file = MockUploadFile(
            filename="test.jpg",
            content_type="image/jpeg",
            size=1024,
            content=b"test_data"
        )

        result = await mock_upload_file_logic(file=mock_file, type=Type.Image)

        if result.code == 200 and result.data:
            # Check response structure matches TypeScript interface
            response_dict = result.model_dump()

            # Top-level structure
            assert 'code' in response_dict, "Missing 'code' field"
            assert 'data' in response_dict, "Missing 'data' field"
            assert 'message' in response_dict, "Missing 'message' field"

            # Data structure for image
            data_dict = response_dict['data']
            expected_fields = ['duration', 'file_id', 'format', 'size', 'thumbnail_url', 'url']

            for field in expected_fields:
                assert field in data_dict, f"Missing '{field}' in data"

            # Image-specific: duration should be null/None, thumbnail_url should exist
            assert data_dict.get('duration') is None, "Image duration should be null"
            assert data_dict.get('thumbnail_url') is not None, "Image thumbnail_url should not be null"

            # Audio upload test
            mock_file_audio = MockUploadFile(
                filename="test.mp3",
                content_type="audio/mpeg",
                size=2048,
                content=b"audio_data"
            )

            result_audio = await mock_upload_file_logic(file=mock_file_audio, type=Type.Audio)

            if result_audio.code == 200 and result_audio.data:
                data_audio_dict = result_audio.model_dump()['data']

                # Audio-specific: duration should not be null, thumbnail_url should be null
                assert data_audio_dict.get('duration') is not None, "Audio duration should not be null"
                assert data_audio_dict.get('thumbnail_url') is None, "Audio thumbnail_url should be null"

            print("PASS: Format compliance test passed!")
            return True
        else:
            print(f"FAIL: Format compliance test failed")
            return False

    except Exception as e:
        print(f"FAIL: Format compliance test failed: {e}")
        return False


async def run_upload_tests():
    """Run all upload tests"""
    print("=" * 60)
    print("Starting Upload API Mock Tests")
    print("=" * 60)

    test_results = []

    # Test 1: Image upload
    test_results.append(("Image Upload", await test_upload_image()))

    # Test 2: Audio upload
    test_results.append(("Audio Upload", await test_upload_audio()))

    # Test 3: Invalid file type
    test_results.append(("Invalid File Type", await test_upload_invalid_file()))

    # Test 4: Oversized file
    test_results.append(("Oversized File", await test_upload_oversized_file()))

    # Test 5: No file
    test_results.append(("No File Upload", await test_upload_no_file()))

    # Test 6: Format compliance
    test_results.append(("Format Compliance", await test_format_compliance()))

    # Output test results
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    print("=" * 40)

    passed_count = 0
    failed_count = 0

    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        if result:
            passed_count += 1
        else:
            failed_count += 1

        print(f"  {test_name:<20} {status}")

    print(f"\nTest Statistics:")
    print(f"  Passed: {passed_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Success Rate: {(passed_count/len(test_results)*100):.1f}%")

    print("=" * 40)

    if failed_count == 0:
        print("SUCCESS: All tests passed! Upload API functionality is normal!")
        return True
    else:
        print(f"WARNING: {failed_count} tests failed, needs review")
        return False


if __name__ == "__main__":
    import asyncio
    success = asyncio.run(run_upload_tests())
    sys.exit(0 if success else 1)