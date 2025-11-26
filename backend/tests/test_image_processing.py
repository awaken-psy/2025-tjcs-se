"""
图片处理服务测试
测试图片压缩、格式转换、缩略图生成等功能
"""

import pytest
import os
import io
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image
import asyncio

from app.services.image_service import ImageService
from app.storage.config import StorageConfig
from app.utils.image_utils import ImageUtils, ImageProcessingError, ImageFormatError
from app.utils.thumbnail_utils import ThumbnailUtils, ThumbnailGenerationError


class TestImageUtils:
    """图片工具类测试"""

    @pytest.fixture
    def sample_image(self):
        """创建测试用的示例图片"""
        img = Image.new('RGB', (800, 600), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        return img_buffer

    @pytest.fixture
    def sample_png_image(self):
        """创建测试用的PNG图片（带透明度）"""
        img = Image.new('RGBA', (400, 300), color=(255, 0, 0, 128))
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        return img_buffer

    def test_detect_image_format_jpeg(self, sample_image):
        """测试JPEG格式检测"""
        format, mime_type = ImageUtils.detect_image_format(sample_image)
        assert format == 'JPEG'
        assert mime_type == 'image/jpeg'

    def test_detect_image_format_invalid(self):
        """测试无效图片格式检测"""
        invalid_data = b"not an image"
        with pytest.raises(ImageFormatError):
            ImageUtils.detect_image_format(io.BytesIO(invalid_data))

    def test_get_image_info(self, sample_image):
        """测试获取图片信息"""
        info = ImageUtils.get_image_info(sample_image)
        assert info['format'] == 'JPEG'
        assert info['size'] == (800, 600)
        assert info['width'] == 800
        assert info['height'] == 600
        assert info['mode'] == 'RGB'
        assert info['has_transparency'] == False

    def test_compress_image_basic(self, sample_image):
        """测试基础图片压缩"""
        compressed_data, info = ImageUtils.compress_image(sample_image)

        assert isinstance(compressed_data, bytes)
        assert len(compressed_data) > 0
        assert info['format'] == 'JPEG'
        assert info['final_dimensions'] == (800, 600)
        assert 'compression_ratio' in info

    def test_compress_image_with_max_size(self, sample_image):
        """测试带最大尺寸限制的图片压缩"""
        compressed_data, info = ImageUtils.compress_image(
            sample_image,
            max_size=(400, 300)
        )

        assert info['final_dimensions'] == (400, 300)

    def test_compress_image_with_quality(self, sample_image):
        """测试指定质量的图片压缩"""
        compressed_data, info = ImageUtils.compress_image(
            sample_image,
            quality=50
        )

        assert info['quality_used'] == 50

    def test_convert_format_jpeg_to_png(self, sample_image):
        """测试JPEG到PNG格式转换"""
        converted_data, info = ImageUtils.convert_format(
            sample_image,
            'PNG'
        )

        assert isinstance(converted_data, bytes)
        assert len(converted_data) > 0
        assert info['original_format'] == 'JPEG'
        assert info['target_format'] == 'PNG'

    def test_convert_format_jpeg_to_webp(self, sample_image):
        """测试JPEG到WebP格式转换"""
        converted_data, info = ImageUtils.convert_format(
            sample_image,
            'WEBP',
            quality=80
        )

        assert info['target_format'] == 'WEBP'
        assert isinstance(converted_data, bytes)

    def test_convert_format_png_with_transparency(self, sample_png_image):
        """测试带透明度PNG的格式转换"""
        converted_data, info = ImageUtils.convert_format(
            sample_png_image,
            'JPEG'
        )

        # PNG转JPEG时应该处理透明度
        assert info['target_format'] == 'JPEG'
        assert isinstance(converted_data, bytes)

    def test_convert_format_unsupported(self, sample_image):
        """测试不支持的格式转换"""
        with pytest.raises(ImageProcessingError):
            ImageUtils.convert_format(sample_image, 'UNSUPPORTED')

    def test_calculate_file_hash(self, sample_image):
        """测试文件哈希计算"""
        file_data = sample_image.getvalue()
        hash_value = ImageUtils.calculate_file_hash(file_data)

        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256长度

    def test_is_valid_image_true(self, sample_image):
        """测试有效图片验证"""
        file_data = sample_image.getvalue()
        assert ImageUtils.is_valid_image(file_data) == True

    def test_is_valid_image_false(self):
        """测试无效图片验证"""
        invalid_data = b"not an image"
        assert ImageUtils.is_valid_image(invalid_data) == False

    def test_process_image_errors(self):
        """测试图片处理错误情况"""
        with pytest.raises(ImageProcessingError):
            ImageUtils.compress_image("non_existent_file.jpg")

    @patch('PIL.Image.open')
    def test_image_processing_with_corrupted_file(self, mock_open):
        """测试损坏文件的处理"""
        mock_open.side_effect = Exception("Corrupted image")

        with pytest.raises(ImageFormatError):
            ImageUtils.detect_image_format("corrupted.jpg")


class TestThumbnailUtils:
    """缩略图工具类测试"""

    @pytest.fixture
    def large_image(self):
        """创建大尺寸测试图片"""
        img = Image.new('RGB', (1200, 800), color='blue')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        return img_buffer

    def test_parse_size_standard(self):
        """测试标准尺寸解析"""
        assert ThumbnailUtils._parse_size('small') == (150, 150)
        assert ThumbnailUtils._parse_size('medium') == (300, 300)
        assert ThumbnailUtils._parse_size('large') == (600, 600)

    def test_parse_size_custom(self):
        """测试自定义尺寸解析"""
        assert ThumbnailUtils._parse_size('200x150') == (200, 150)
        assert ThumbnailUtils._parse_size((100, 100)) == (100, 100)

    def test_parse_size_invalid(self):
        """测试无效尺寸解析"""
        with pytest.raises(ThumbnailGenerationError):
            ThumbnailUtils._parse_size('invalid_size')

        with pytest.raises(ThumbnailGenerationError):
            ThumbnailUtils._parse_size('unknown_size')

    def test_generate_thumbnail_cover(self, large_image):
        """测试覆盖模式缩略图生成"""
        thumbnail_data = ThumbnailUtils.generate_thumbnail(
            large_image,
            size='small',
            crop_mode='cover'
        )

        assert isinstance(thumbnail_data, bytes)
        assert len(thumbnail_data) > 0

        # 验证缩略图尺寸
        thumb_img = Image.open(io.BytesIO(thumbnail_data))
        assert thumb_img.size == (150, 150)

    def test_generate_thumbnail_contain(self, large_image):
        """测试包含模式缩略图生成"""
        thumbnail_data = ThumbnailUtils.generate_thumbnail(
            large_image,
            size=(200, 200),
            crop_mode='contain'
        )

        assert isinstance(thumbnail_data, bytes)

        # 验证缩略图尺寸
        thumb_img = Image.open(io.BytesIO(thumbnail_data))
        assert thumb_img.size == (200, 200)

    def test_generate_thumbnail_stretch(self, large_image):
        """测试拉伸模式缩略图生成"""
        thumbnail_data = ThumbnailUtils.generate_thumbnail(
            large_image,
            size=(100, 200),
            crop_mode='stretch'
        )

        thumb_img = Image.open(io.BytesIO(thumbnail_data))
        assert thumb_img.size == (100, 200)

    def test_generate_multiple_thumbnails(self, large_image):
        """测试批量生成缩略图"""
        thumbnails = ThumbnailUtils.generate_multiple_thumbnails(
            large_image,
            sizes=['small', 'medium', 'large']
        )

        assert len(thumbnails) == 3
        assert 'small' in thumbnails
        assert 'medium' in thumbnails
        assert 'large' in thumbnails

        for size_name, thumb_data in thumbnails.items():
            assert isinstance(thumb_data, bytes)
            assert len(thumb_data) > 0

    def test_create_avatar_thumbnail(self, large_image):
        """测试头像缩略图生成"""
        avatar_data = ThumbnailUtils.create_avatar_thumbnail(
            large_image,
            size=100,
            circular=False
        )

        assert isinstance(avatar_data, bytes)

        avatar_img = Image.open(io.BytesIO(avatar_data))
        assert avatar_img.size == (100, 100)

    def test_create_circular_avatar_thumbnail(self, large_image):
        """测试圆形头像缩略图生成"""
        avatar_data = ThumbnailUtils.create_avatar_thumbnail(
            large_image,
            size=100,
            circular=True
        )

        assert isinstance(avatar_data, bytes)

        # 圆形头像应该保存为PNG以保持透明度
        avatar_img = Image.open(io.BytesIO(avatar_data))
        assert avatar_img.size == (100, 100)

    def test_smart_crop(self):
        """测试智能裁剪"""
        # 创建宽图片
        wide_img = Image.new('RGB', (800, 200), color='green')
        cropped = ThumbnailUtils.smart_crop(wide_img, (200, 200))

        assert cropped.size == (200, 200)

    def test_thumbnail_generation_error(self):
        """测试缩略图生成错误"""
        with pytest.raises(ThumbnailGenerationError):
            ThumbnailUtils.generate_thumbnail(
                "non_existent.jpg",
                size='small'
            )

    def test_invalid_crop_mode(self, large_image):
        """测试无效裁剪模式"""
        with pytest.raises(ThumbnailGenerationError):
            ThumbnailUtils.generate_thumbnail(
                large_image,
                size='small',
                crop_mode='invalid_mode'
            )


class TestImageService:
    """图片处理服务测试"""

    @pytest.fixture
    def temp_upload_dir(self):
        """创建临时上传目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def storage_config(self, temp_upload_dir):
        """创建存储配置"""
        config = StorageConfig()
        config.UPLOAD_DIR = temp_upload_dir
        config.STORAGE_PATH = temp_upload_dir
        config.CACHE_DIR = os.path.join(temp_upload_dir, 'cache')
        return config

    @pytest.fixture
    def image_service(self, storage_config):
        """创建图片服务实例"""
        return ImageService(storage_config)

    @pytest.fixture
    def sample_image_data(self):
        """创建示例图片数据"""
        img = Image.new('RGB', (800, 600), color='purple')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG', quality=95)
        img_buffer.seek(0)
        return img_buffer.getvalue()

    @pytest.mark.asyncio
    async def test_process_image_basic(self, image_service, sample_image_data):
        """测试基础图片处理流程"""
        result = await image_service.process_image(
            file_data=sample_image_data,
            original_filename="test.jpg",
            compress=True,
            convert_to_webp=True,
            generate_thumbnails=True
        )

        assert result['success'] == True
        assert 'file_hash' in result
        assert 'original_info' in result
        assert 'processed_files' in result
        assert 'thumbnails' in result
        assert 'cdn_urls' in result

        # 检查原图
        assert 'original' in result['processed_files']
        original_info = result['processed_files']['original']
        assert original_info['format'] == 'JPEG'

        # 检查压缩版本
        assert 'compressed' in result['processed_files']
        compressed_info = result['processed_files']['compressed']
        assert 'compression_ratio' in compressed_info

        # 检查WebP版本
        assert 'webp' in result['processed_files']
        webp_info = result['processed_files']['webp']
        assert webp_info['format'] == 'WEBP'

        # 检查缩略图
        thumbnails = result['thumbnails']
        assert len(thumbnails) > 0
        for size_name, thumb_info in thumbnails.items():
            assert 'path' in thumb_info
            assert 'size' in thumb_info
            assert 'dimensions' in thumb_info
            assert 'url' in thumb_info

    @pytest.mark.asyncio
    async def test_process_image_without_compression(self, image_service, sample_image_data):
        """测试不压缩的图片处理"""
        result = await image_service.process_image(
            file_data=sample_image_data,
            original_filename="test.jpg",
            compress=False,
            convert_to_webp=False,
            generate_thumbnails=False
        )

        assert result['success'] == True
        assert 'original' in result['processed_files']
        assert 'compressed' not in result['processed_files']
        assert 'webp' not in result['processed_files']
        assert len(result['thumbnails']) == 0

    @pytest.mark.asyncio
    async def test_process_image_invalid_data(self, image_service):
        """测试无效图片数据处理"""
        result = await image_service.process_image(
            file_data=b"invalid image data",
            original_filename="invalid.jpg"
        )

        assert result['success'] == False
        assert 'error' in result

    @pytest.mark.asyncio
    async def test_process_image_oversized(self, image_service):
        """测试超大图片文件处理"""
        # 创建超大文件数据
        large_data = b"x" * (100 * 1024 * 1024)  # 100MB

        result = await image_service.process_image(
            file_data=large_data,
            original_filename="large.jpg"
        )

        assert result['success'] == False
        assert '文件过大' in result['error']

    @pytest.mark.asyncio
    async def test_create_custom_thumbnail(self, image_service, sample_image_data):
        """测试自定义缩略图创建"""
        # 首先处理图片
        process_result = await image_service.process_image(
            file_data=sample_image_data,
            original_filename="test.jpg",
            generate_thumbnails=False
        )

        file_hash = process_result['file_hash']

        # 创建自定义缩略图
        thumbnail_result = await image_service.create_custom_thumbnail(
            file_hash=file_hash,
            size=(200, 200),
            crop_mode='cover',
            quality=90
        )

        assert thumbnail_result['success'] == True
        assert thumbnail_result['dimensions'] == (200, 200)
        assert thumbnail_result['crop_mode'] == 'cover'
        assert thumbnail_result['quality'] == 90

    @pytest.mark.asyncio
    async def test_create_custom_thumbnail_not_found(self, image_service):
        """测试不存在文件的自定义缩略图"""
        result = await image_service.create_custom_thumbnail(
            file_hash="nonexistent_hash",
            size='small'
        )

        assert result['success'] == False
        assert 'error' in result

    def test_find_original_file(self, image_service, sample_image_data):
        """测试查找原图文件"""
        # 这个测试需要实际的文件系统操作
        pass

    def test_is_image_file(self, image_service):
        """测试图片文件检查"""
        assert image_service._is_image_file("test.jpg") == True
        assert image_service._is_image_file("test.png") == True
        assert image_service._is_image_file("test.txt") == False

    @pytest.mark.asyncio
    async def test_get_image_info(self, image_service, sample_image_data):
        """测试获取图片信息"""
        # 先保存一个测试文件
        test_file_path = os.path.join(image_service.config.UPLOAD_DIR, "test.jpg")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
        with open(test_file_path, 'wb') as f:
            f.write(sample_image_data)

        info = await image_service.get_image_info(test_file_path)

        assert 'format' in info
        assert 'size' in info
        assert 'file_size' in info
        assert 'file_path' in info

    @pytest.mark.asyncio
    async def test_get_image_info_not_found(self, image_service):
        """测试获取不存在图片的信息"""
        info = await image_service.get_image_info("nonexistent.jpg")
        assert 'error' in info

    def test_get_storage_statistics(self, image_service, sample_image_data):
        """测试获取存储统计信息"""
        # 添加一些测试文件
        test_file_path = os.path.join(image_service.config.UPLOAD_DIR, "test.jpg")
        with open(test_file_path, 'wb') as f:
            f.write(sample_image_data)

        stats = image_service.get_storage_statistics()

        assert 'total_images' in stats
        assert 'total_size' in stats
        assert 'size_by_format' in stats
        assert 'size_by_type' in stats

    def test_clean_orphaned_thumbnails(self, image_service):
        """测试清理孤立缩略图"""
        result = image_service.clean_orphaned_thumbnails()

        assert 'deleted' in result
        assert 'kept' in result
        assert 'errors' in result
        assert isinstance(result['deleted'], int)
        assert isinstance(result['kept'], int)
        assert isinstance(result['errors'], list)


class TestImageProcessingIntegration:
    """图片处理集成测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_end_to_end_image_processing(self, temp_dir):
        """测试端到端图片处理流程"""
        # 创建测试图片
        img = Image.new('RGB', (1000, 800), color='yellow')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_data = img_buffer.getvalue()

        # 初始化服务
        config = StorageConfig()
        config.UPLOAD_DIR = temp_dir
        service = ImageService(config)

        # 运行异步处理
        async def run_processing():
            result = await service.process_image(
                file_data=img_data,
                original_filename="integration_test.jpg",
                compress=True,
                convert_to_webp=True,
                generate_thumbnails=True
            )
            return result

        # 在同步测试中运行异步代码
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_processing())
        finally:
            loop.close()

        # 验证结果
        assert result['success'] == True
        assert os.path.exists(os.path.join(temp_dir, result['processed_files']['original']['path']))
        assert os.path.exists(os.path.join(temp_dir, result['processed_files']['compressed']['path']))
        assert os.path.exists(os.path.join(temp_dir, result['processed_files']['webp']['path']))

        # 验证缩略图文件
        for size_name, thumb_info in result['thumbnails'].items():
            assert os.path.exists(os.path.join(temp_dir, thumb_info['path']))

    def test_error_handling_and_recovery(self, temp_dir):
        """测试错误处理和恢复"""
        config = StorageConfig()
        config.UPLOAD_DIR = temp_dir
        service = ImageService(config)

        # 测试各种错误情况
        async def test_errors():
            # 测试无效数据
            result1 = await service.process_image(
                file_data=b"invalid",
                original_filename="invalid.jpg"
            )
            assert result1['success'] == False

            # 测试空数据
            result2 = await service.process_image(
                file_data=b"",
                original_filename="empty.jpg"
            )
            assert result2['success'] == False

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_errors())
        finally:
            loop.close()


# 性能测试
class TestImageProcessingPerformance:
    """图片处理性能测试"""

    @pytest.fixture
    def large_test_image(self):
        """创建大尺寸测试图片"""
        img = Image.new('RGB', (4000, 3000), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG', quality=90)
        img_buffer.seek(0)
        return img_buffer.getvalue()

    @pytest.mark.asyncio
    async def test_large_image_processing_performance(self, large_test_image):
        """测试大图片处理性能"""
        import time

        config = StorageConfig()
        service = ImageService(config)

        start_time = time.time()

        result = await service.process_image(
            file_data=large_test_image,
            original_filename="large_test.jpg",
            compress=True,
            convert_to_webp=True,
            generate_thumbnails=False  # 跳过缩略图以专注测试压缩性能
        )

        end_time = time.time()
        processing_time = end_time - start_time

        assert result['success'] == True
        assert processing_time < 30.0  # 应该在30秒内完成

        # 验证压缩效果
        original_size = len(large_test_image)
        compressed_size = result['processed_files']['compressed']['size']
        compression_ratio = result['processed_files']['compressed']['compression_ratio']

        assert compressed_size < original_size
        assert compression_ratio > 0.1  # 至少10%的压缩率


if __name__ == "__main__":
    pytest.main([__file__, "-v"])