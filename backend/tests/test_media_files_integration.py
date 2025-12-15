"""
媒体文件路径一致性修复 - 综合集成测试

这个测试文件验证了媒体文件路径一致性问题是否已完全解决。

测试流程：
1. 用户登录获取认证token
2. 上传图片文件，验证返回的URL和缩略图路径
3. 创建包含媒体文件的胶囊
4. 获取胶囊详情，验证媒体文件路径是否与上传时一致

修复前问题：
- 上传时返回：/uploads/image/20251214/file_xxx.png
- 获取时返回：/api/files/file_xxx (错误路径，缺少扩展名，缩略图丢失)

修复后预期：
- 上传时和获取时返回完全一致的路径格式
- 缩略图正常返回
- 路径以/uploads/开头，包含完整文件名和扩展名

运行方式：
docker exec timecapsule_backend python tests/test_media_files_integration.py
"""

import requests
import tempfile
import json
import os

BASE_URL = "http://localhost:8000/api"

def create_test_image():
    """创建测试图片文件"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        # 写入一个简单的PNG文件头
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82'
        f.write(png_data)
        return f.name

def upload_file():
    """步骤1: 上传文件"""
    temp_path = create_test_image()

    try:
        with open(temp_path, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            data = {'type': 'image'}
            response = requests.post(f"{BASE_URL}/upload/", files=files, data=data, headers=headers)

        print(f"📤 上传响应状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 上传成功!")
            upload_data = data.get('data', {})
            file_id = upload_data.get('file_id')
            file_url = upload_data.get('url')
            thumbnail_url = upload_data.get('thumbnail_url')

            print(f"   文件ID: {file_id}")
            print(f"   文件URL: {file_url}")
            print(f"   缩略图URL: {thumbnail_url}")

            return file_id, file_url, thumbnail_url
        else:
            print(f"❌ 上传失败: {response.text}")
            return None, None, None

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def create_capsule_with_media(file_id, file_url, thumbnail_url):
    """步骤2: 创建包含媒体文件的胶囊"""
    capsule_data = {
        "title": "测试媒体文件胶囊",
        "content": "这是一个用于测试媒体文件路径的胶囊",
        "visibility": "public",
        "tags": ["测试", "媒体", "图片"],
        "location": {
            "latitude": 31.2304,
            "longitude": 121.4737,
            "address": "上海市同济大学"
        },
        "unlock_conditions": {
            "type": "public",
            "radius": 100.0
        },
        "media_files": [
            {
                "id": file_id,
                "type": "image",
                "url": file_url,
                "thumbnail": thumbnail_url
            }
        ]  # 使用上传的文件信息
    }

    response = requests.post(f"{BASE_URL}/capsules/", json=capsule_data, headers=headers)

    print(f"📝 创建胶囊响应状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 胶囊创建成功!")
        capsule_data = data.get('data', {})
        capsule_id = capsule_data.get('capsule_id')

        print(f"   胶囊ID: {capsule_id}")
        print(f"   标题: {capsule_data.get('title')}")
        print(f"   状态: {capsule_data.get('status')}")

        return capsule_id
    else:
        print(f"❌ 创建胶囊失败: {response.text}")
        return None

def get_capsule_detail(capsule_id):
    """步骤3: 获取胶囊详情"""
    response = requests.get(f"{BASE_URL}/capsules/{capsule_id}", headers=headers)

    print(f"🔍 获取胶囊详情响应状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 获取胶囊详情成功!")
        capsule_detail = data.get('data', {})

        print(f"   胶囊ID: {capsule_detail.get('id')}")
        print(f"   标题: {capsule_detail.get('title')}")
        print(f"   内容: {capsule_detail.get('content')}")

        # 步骤4: 检查媒体文件路径
        media_files = capsule_detail.get('media_files', [])
        print(f"   媒体文件数量: {len(media_files)}")

        if media_files:
            print("\n🎯 媒体文件详细信息:")
            for i, media in enumerate(media_files, 1):
                print(f"   媒体文件 {i}:")
                print(f"     ID: {media.get('id')}")
                print(f"     类型: {media.get('type')}")
                print(f"     URL: {media.get('url')}")
                print(f"     缩略图: {media.get('thumbnail')}")

                # 验证URL是否正确
                url = media.get('url', '')
                if url.startswith('/uploads/'):
                    print(f"     ✅ URL路径正确 (以/uploads/开头)")
                elif url.startswith('/api/files/'):
                    print(f"     ❌ URL路径错误 (应该是/uploads/，不是/api/files/)")
                else:
                    print(f"     ⚠️ URL路径格式未知")

                # 验证缩略图
                thumbnail = media.get('thumbnail')
                if thumbnail and thumbnail.startswith('/uploads/'):
                    print(f"     ✅ 缩略图路径正确")
                elif not thumbnail:
                    print(f"     ⚠️ 缩略图为空")
                else:
                    print(f"     ❌ 缩略图路径错误")

        return capsule_detail
    else:
        print(f"❌ 获取胶囊详情失败: {response.text}")
        return None

def login():
    """登录获取token"""
    login_data = {
        "email": "admin@admin.com",
        "password": "admin"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

    print(f"🔐 登录响应状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        token = data.get('data', {}).get('token')
        print(f"✅ 登录成功! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def main():
    """执行完整的测试流程"""
    print("🚀 开始完整测试流程...")
    print("=" * 60)

    # 先登录获取token
    print("\n🔐 步骤0: 登录获取认证token")
    token = login()
    if not token:
        print("❌ 登录失败，测试终止")
        return

    # 更新全局认证头
    global headers
    headers = {"Authorization": f"Bearer {token}"}

    # 步骤1: 上传文件
    print("\n📤 步骤1: 上传文件")
    file_id, file_url, thumbnail_url = upload_file()

    if not file_id:
        print("❌ 文件上传失败，测试终止")
        return

    # 步骤2: 创建胶囊
    print("\n📝 步骤2: 创建包含媒体文件的胶囊")
    capsule_id = create_capsule_with_media(file_id, file_url, thumbnail_url)

    if not capsule_id:
        print("❌ 胶囊创建失败，测试终止")
        return

    # 步骤3&4: 获取胶囊详情并检查媒体文件
    print("\n🔍 步骤3&4: 获取胶囊详情并检查媒体文件路径")
    capsule_detail = get_capsule_detail(capsule_id)

    if capsule_detail:
        print("\n🎉 完整测试流程完成!")
        print("=" * 60)
        print("总结:")
        print(f"- 上传的文件URL: {file_url}")
        print(f"- 胶囊详情中的文件URL: {capsule_detail['media_files'][0]['url'] if capsule_detail.get('media_files') else 'N/A'}")
        print(f"- 路径一致性: {'✅ 一致' if file_url == capsule_detail['media_files'][0]['url'] else '❌ 不一致'}")
    else:
        print("❌ 胶囊详情获取失败，无法验证修复效果")

if __name__ == "__main__":
    main()