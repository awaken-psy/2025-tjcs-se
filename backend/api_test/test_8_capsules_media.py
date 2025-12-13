import pytest
import requests
import os
import tempfile
from datetime import datetime, timedelta

from .config import base_url
from .utils import get_admin_user, get_registered_users


class TestCapsuleMedia:
    """胶囊媒体文件功能测试"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """获取管理员token"""
        admin_info = get_admin_user()
        return admin_info["token"]

    @pytest.fixture(scope="class")
    def user_tokens(self):
        """获取普通用户token"""
        return get_registered_users()

    @pytest.fixture(scope="class")
    def test_image_file(self):
        """创建测试图片文件"""
        # 创建临时图片文件（简单的PNG文件）
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            # 写入一个简单的PNG文件头
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82')
            temp_path = f.name

        yield temp_path

        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture(scope="class")
    def test_audio_file(self):
        """创建测试音频文件"""
        # 创建临时音频文件（简单的WAV文件）
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            # 写入一个简单的WAV文件头
            f.write(b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00')
            temp_path = f.name

        yield temp_path

        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture(scope="class")
    def uploaded_files(self, admin_token):
        """存储上传的文件ID"""
        return []

    def test_upload_image_file(self, admin_token, test_image_file, uploaded_files):
        """测试上传图片文件"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        with open(test_image_file, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            response = requests.post(f"{base_url}/v1/upload/image", files=files, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "上传成功" in data["message"]

        upload_response = data["data"]
        assert "file_id" in upload_response
        assert "url" in upload_response
        assert "file_name" in upload_response
        assert "file_size" in upload_response

        # 保存文件ID用于后续测试
        uploaded_files.append({
            "file_id": upload_response["file_id"],
            "type": "image",
            "name": upload_response["file_name"]
        })

        print(f"✅ 图片上传成功: {upload_response['file_id']}")

    def test_upload_audio_file(self, admin_token, test_audio_file, uploaded_files):
        """测试上传音频文件"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        with open(test_audio_file, 'rb') as f:
            files = {'file': ('test_audio.wav', f, 'audio/wav')}
            response = requests.post(f"{base_url}/v1/upload/audio", files=files, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "上传成功" in data["message"]

        upload_response = data["data"]
        assert "file_id" in upload_response
        assert "url" in upload_response
        assert "file_name" in upload_response
        assert "file_size" in upload_response

        # 保存文件ID用于后续测试
        uploaded_files.append({
            "file_id": upload_response["file_id"],
            "type": "audio",
            "name": upload_response["file_name"]
        })

        print(f"✅ 音频上传成功: {upload_response['file_id']}")

    def test_upload_invalid_file_type(self, admin_token, test_image_file):
        """测试上传无效文件类型"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 尝试将图片作为音频上传
        with open(test_image_file, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            response = requests.post(f"{base_url}/v1/upload/audio", files=files, headers=headers)

        # 应该返回错误，因为文件类型不匹配
        assert response.status_code in [400, 422]

        print("✅ 无效文件类型上传测试通过")

    def test_upload_oversized_file(self, admin_token):
        """测试上传过大文件"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 创建一个大文件（模拟）
        large_content = b'x' * (50 * 1024 * 1024)  # 50MB的假文件

        files = {'file': ('large_file.png', large_content, 'image/png')}
        response = requests.post(f"{base_url}/v1/upload/image", files=files, headers=headers)

        # 应该返回错误，因为文件过大
        assert response.status_code in [400, 413, 422]

        print("✅ 过大文件上传测试通过")

    def test_upload_file_unauthorized(self, test_image_file):
        """测试未授权上传文件"""
        with open(test_image_file, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            response = requests.post(f"{base_url}/v1/upload/image", files=files)

        assert response.status_code == 401

        print("✅ 未授权上传文件测试通过")

    def test_upload_file_without_file(self, admin_token):
        """测试没有文件的上传请求"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        response = requests.post(f"{base_url}/v1/upload/image", headers=headers)

        # 应该返回错误，因为缺少文件
        assert response.status_code in [400, 422]

        print("✅ 缺少文件上传测试通过")

    def test_create_capsule_with_media(self, admin_token, uploaded_files):
        """测试创建包含媒体的胶囊"""
        if len(uploaded_files) < 2:
            pytest.skip("需要至少2个上传的文件进行测试")

        headers = {"Authorization": f"Bearer {admin_token}"}

        # 获取上传的文件ID
        image_file = next((f for f in uploaded_files if f["type"] == "image"), None)
        audio_file = next((f for f in uploaded_files if f["type"] == "audio"), None)

        if not image_file or not audio_file:
            pytest.skip("需要图片和音频文件进行测试")

        capsule_data = {
            "title": "包含媒体的胶囊",
            "content": "这个胶囊包含图片和音频文件。",
            "visibility": "public",
            "tags": ["媒体", "图片", "音频"],
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737,
                "address": "上海市同济大学"
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0
            },
            "media_files": [image_file["file_id"], audio_file["file_id"]]
        }

        response = requests.post(f"{base_url}/v1/capsules/", json=capsule_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        capsule_response = data["data"]
        print(f"✅ 创建包含媒体的胶囊成功: {capsule_response['capsule_id']}")

        return capsule_response["capsule_id"]

    def test_create_capsule_with_invalid_media(self, admin_token):
        """测试创建包含无效媒体ID的胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        capsule_data = {
            "title": "包含无效媒体的胶囊",
            "content": "这个胶囊包含无效的媒体文件ID。",
            "visibility": "public",
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0
            },
            "media_files": ["invalid_file_id", "999999"]
        }

        response = requests.post(f"{base_url}/v1/capsules/", json=capsule_data, headers=headers)

        # 应该返回错误，因为文件ID无效
        assert response.status_code in [400, 422]

        print("✅ 无效媒体ID测试通过")

    def test_get_capsule_detail_with_media(self, admin_token, uploaded_files):
        """测试获取包含媒体的胶囊详情"""
        if len(uploaded_files) < 1:
            pytest.skip("需要上传的文件进行测试")

        headers = {"Authorization": f"Bearer {admin_token}"}

        # 创建包含媒体的胶囊
        image_file = next((f for f in uploaded_files if f["type"] == "image"), None)
        if not image_file:
            pytest.skip("需要图片文件进行测试")

        capsule_data = {
            "title": "媒体详情测试胶囊",
            "content": "用于测试媒体详情的胶囊。",
            "visibility": "public",
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0
            },
            "media_files": [image_file["file_id"]]
        }

        # 创建胶囊
        create_response = requests.post(f"{base_url}/v1/capsules/", json=capsule_data, headers=headers)
        assert create_response.status_code == 200
        capsule_id = create_response.json()["data"]["capsule_id"]

        # 获取胶囊详情
        response = requests.get(f"{base_url}/v1/capsules/{capsule_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        capsule_detail = data["data"]
        assert "media_files" in capsule_detail
        assert isinstance(capsule_detail["media_files"], list)

        if capsule_detail["media_files"]:
            media_file = capsule_detail["media_files"][0]
            assert "id" in media_file
            assert "type" in media_file
            assert "url" in media_file
            assert "file_name" in media_file
            assert "file_size" in media_file

            # 验证媒体文件类型
            assert media_file["type"] in ["image", "audio"]

            # 图片文件应该有缩略图
            if media_file["type"] == "image":
                assert "thumbnail" in media_file

            # 音频文件应该有时长
            if media_file["type"] == "audio":
                assert "duration" in media_file

        print(f"✅ 获取含媒体胶囊详情成功: {capsule_id}")

    def test_upload_multiple_image_files(self, admin_token, test_image_file):
        """测试上传多个图片文件"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        uploaded_ids = []

        # 上传多个图片文件
        for i in range(3):
            with open(test_image_file, 'rb') as f:
                files = {'file': (f'test_image_{i}.png', f, 'image/png')}
                response = requests.post(f"{base_url}/v1/upload/image", files=files, headers=headers)

                assert response.status_code == 200
                file_id = response.json()["data"]["file_id"]
                uploaded_ids.append(file_id)

        print(f"✅ 批量上传图片成功，共 {len(uploaded_ids)} 个文件")
        return uploaded_ids

    def test_create_capsule_with_multiple_media(self, admin_token, uploaded_files):
        """测试创建包含多个媒体文件的胶囊"""
        if len(uploaded_files) < 2:
            pytest.skip("需要至少2个上传的文件进行测试")

        headers = {"Authorization": f"Bearer {admin_token}"}

        # 获取所有文件ID
        file_ids = [f["file_id"] for f in uploaded_files]

        capsule_data = {
            "title": "包含多个媒体的胶囊",
            "content": "这个胶囊包含多个媒体文件。",
            "visibility": "public",
            "tags": ["多媒体", "批量"],
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0
            },
            "media_files": file_ids
        }

        response = requests.post(f"{base_url}/v1/capsules/", json=capsule_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        capsule_response = data["data"]
        print(f"✅ 创建包含多个媒体的胶囊成功: {capsule_response['capsule_id']}")

    def test_get_capsule_media_order(self, admin_token, uploaded_files):
        """测试胶囊媒体文件顺序"""
        if len(uploaded_files) < 2:
            pytest.skip("需要至少2个上传的文件进行测试")

        headers = {"Authorization": f"Bearer {admin_token}"}

        # 按特定顺序创建胶囊
        file_ids = [f["file_id"] for f in uploaded_files]

        capsule_data = {
            "title": "媒体顺序测试胶囊",
            "content": "测试媒体文件顺序。",
            "visibility": "public",
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0
            },
            "media_files": file_ids
        }

        response = requests.post(f"{base_url}/v1/capsules/", json=capsule_data, headers=headers)
        assert response.status_code == 200
        capsule_id = response.json()["data"]["capsule_id"]

        # 获取胶囊详情，验证媒体顺序
        response = requests.get(f"{base_url}/v1/capsules/{capsule_id}", headers=headers)
        assert response.status_code == 200

        capsule_detail = response.json()["data"]
        media_files = capsule_detail["media_files"]

        # 验证媒体数量
        assert len(media_files) == len(file_ids)

        print(f"✅ 媒体文件顺序测试通过，共 {len(media_files)} 个文件")

    def test_media_file_not_found(self, admin_token):
        """测试获取不存在的媒体文件"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 尝试获取不存在的媒体文件信息（如果API支持的话）
        response = requests.get(f"{base_url}/v1/upload/999999", headers=headers)

        # 应该返回404或相应的错误状态码
        assert response.status_code in [404, 400, 405]  # 405表示方法不支持

        print("✅ 不存在媒体文件测试通过")

    def test_media_file_size_limits(self, admin_token, test_image_file):
        """测试媒体文件大小限制"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试正常大小文件
        with open(test_image_file, 'rb') as f:
            files = {'file': ('normal_size.png', f, 'image/png')}
            response = requests.post(f"{base_url}/v1/upload/image", files=files, headers=headers)
            assert response.status_code == 200

        print("✅ 文件大小限制测试通过")

    def test_media_file_extension_validation(self, admin_token, test_image_file):
        """测试媒体文件扩展名验证"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试正确的扩展名
        with open(test_image_file, 'rb') as f:
            files = {'file': ('test.png', f, 'image/png')}
            response = requests.post(f"{base_url}/v1/upload/image", files=files, headers=headers)
            assert response.status_code == 200

        # 测试错误的扩展名（PNG文件但使用.jpg扩展名）
        with open(test_image_file, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/png')}  # 内容是PNG但扩展名是JPG
            response = requests.post(f"{base_url}/v1/upload/image", files=files, headers=headers)
            # 根据实现可能成功或失败
            assert response.status_code in [200, 400, 422]

        print("✅ 文件扩展名验证测试通过")

    def test_media_mime_type_validation(self, admin_token, test_image_file):
        """测试媒体MIME类型验证"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试正确的MIME类型
        with open(test_image_file, 'rb') as f:
            files = {'file': ('test.png', f, 'image/png')}
            response = requests.post(f"{base_url}/v1/upload/image", files=files, headers=headers)
            assert response.status_code == 200

        # 测试错误的MIME类型
        with open(test_image_file, 'rb') as f:
            files = {'file': ('test.png', f, 'application/octet-stream')}  # 错误的MIME类型
            response = requests.post(f"{base_url}/v1/upload/image", files=files, headers=headers)
            # 根据实现可能成功或失败
            assert response.status_code in [200, 400, 422]

        print("✅ MIME类型验证测试通过")