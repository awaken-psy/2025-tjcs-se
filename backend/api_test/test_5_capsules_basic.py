import pytest
import requests
from datetime import datetime, timedelta

from .config import base_url
from .utils import get_admin_user, get_registered_users


class TestCapsuleCRUD:
    """胶囊基本CRUD操作测试"""

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
    def created_capsule_ids(self):
        """存储测试中创建的胶囊ID，用于清理"""
        return []

    def test_create_capsule_success(self, admin_token, created_capsule_ids):
        """测试成功创建胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 准备胶囊数据
        capsule_data = {
            "title": "测试胶囊标题",
            "content": "这是一个测试胶囊的内容，用于验证创建功能是否正常工作。",
            "visibility": "public",
            "tags": ["测试", "胶囊", "API"],
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737,
                "address": "上海市同济大学"
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0,
                "unlockable_time": (datetime.now() - timedelta(days=1)).isoformat()
            }
        }

        response = requests.post(f"{base_url}/capsules/", json=capsule_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "胶囊创建成功" in data["message"]

        capsule_response = data["data"]
        assert "capsule_id" in capsule_response
        assert capsule_response["title"] == capsule_data["title"]
        assert capsule_response["status"] == "published"
        assert "created_at" in capsule_response

        # 保存ID用于后续测试和清理
        created_capsule_ids.append(capsule_response["capsule_id"])

        print(f"✅ 创建胶囊成功: {capsule_response['capsule_id']}")

    def test_create_private_capsule(self, admin_token, created_capsule_ids):
        """测试创建私有胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        capsule_data = {
            "title": "私有测试胶囊",
            "content": "这是一个私有胶囊，只有创建者可见。",
            "visibility": "private",
            "tags": ["私有"],
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "private"
            }
        }

        response = requests.post(f"{base_url}/capsules/", json=capsule_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        created_capsule_ids.append(data["data"]["capsule_id"])
        print(f"✅ 创建私有胶囊成功: {data['data']['capsule_id']}")

    def test_create_friends_capsule(self, admin_token, created_capsule_ids):
        """测试创建好友可见胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        capsule_data = {
            "title": "好友可见胶囊",
            "content": "这是一个只有好友可见的胶囊。",
            "visibility": "friends",
            "tags": ["好友"],
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "public"
            }
        }

        response = requests.post(f"{base_url}/capsules/", json=capsule_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        created_capsule_ids.append(data["data"]["capsule_id"])
        print(f"✅ 创建好友胶囊成功: {data['data']['capsule_id']}")

    def test_create_password_protected_capsule(self, admin_token, created_capsule_ids):
        """测试创建密码保护胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        capsule_data = {
            "title": "密码保护胶囊",
            "content": "这是一个需要密码才能解锁的胶囊。",
            "visibility": "public",
            "tags": ["密码", "保护"],
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "password",
                "password": "test123",
                "radius": 50.0
            }
        }

        response = requests.post(f"{base_url}/capsules/", json=capsule_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        created_capsule_ids.append(data["data"]["capsule_id"])
        print(f"✅ 创建密码保护胶囊成功: {data['data']['capsule_id']}")

    def test_create_capsule_validation_errors(self, admin_token):
        """测试创建胶囊时的验证错误"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试缺少标题
        capsule_data_no_title = {
            "content": "没有标题的胶囊",
            "visibility": "public",
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "public"
            }
        }

        response = requests.post(f"{base_url}/capsules/", json=capsule_data_no_title, headers=headers)
        assert response.status_code == 422

        # 测试缺少内容
        capsule_data_no_content = {
            "title": "没有内容的胶囊",
            "visibility": "public",
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "public"
            }
        }

        response = requests.post(f"{base_url}/capsules/", json=capsule_data_no_content, headers=headers)
        assert response.status_code == 422

        # 测试无效的可见性设置
        capsule_data_invalid_visibility = {
            "title": "无效可见性胶囊",
            "content": "内容",
            "visibility": "invalid",
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "public"
            }
        }

        response = requests.post(f"{base_url}/capsules/", json=capsule_data_invalid_visibility, headers=headers)
        assert response.status_code == 422

        print("✅ 创建胶囊验证错误测试通过")

    def test_create_capsule_unauthorized(self):
        """测试未授权创建胶囊"""
        capsule_data = {
            "title": "未授权胶囊",
            "content": "没有token的胶囊",
            "visibility": "public",
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "public"
            }
        }

        response = requests.post(f"{base_url}/capsules/", json=capsule_data)
        assert response.status_code == 401

        print("✅ 未授权创建胶囊测试通过")

    def test_get_my_capsules(self, admin_token, created_capsule_ids):
        """测试获取我的胶囊列表"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 获取所有胶囊
        response = requests.get(f"{base_url}/capsules/my", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "capsules" in data["data"]
        assert "pagination" in data["data"]

        capsules = data["data"]["capsules"]
        pagination = data["data"]["pagination"]

        assert isinstance(capsules, list)
        assert "page" in pagination
        assert "page_size" in pagination
        assert "total" in pagination
        assert "total_pages" in pagination

        # 验证刚创建的胶囊在列表中
        capsule_ids = [capsule.get("id") for capsule in capsules]
        for created_id in created_capsule_ids:
            assert str(created_id) in capsule_ids or created_id in capsule_ids

        print(f"✅ 获取我的胶囊成功，共 {len(capsules)} 个胶囊")

    def test_get_my_capsules_with_filters(self, admin_token):
        """测试带过滤条件获取我的胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试获取已发布的胶囊
        params = {"status": "published", "page": 1, "size": 10}
        response = requests.get(f"{base_url}/capsules/my", headers=headers, params=params)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        # 测试分页
        params = {"page": 1, "size": 5}
        response = requests.get(f"{base_url}/capsules/my", headers=headers, params=params)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["capsules"]) <= 5

        print("✅ 获取我的胶囊过滤测试通过")

    def test_get_capsule_detail(self, admin_token, created_capsule_ids):
        """测试获取胶囊详情"""
        if not created_capsule_ids:
            pytest.skip("没有可用的胶囊ID进行测试")

        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = created_capsule_ids[0]

        response = requests.get(f"{base_url}/capsules/{capsule_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        capsule_detail = data["data"]
        assert "id" in capsule_detail
        assert "title" in capsule_detail
        assert "content" in capsule_detail
        assert "visibility" in capsule_detail
        assert "status" in capsule_detail
        assert "created_at" in capsule_detail
        assert "location" in capsule_detail
        assert "unlock_conditions" in capsule_detail
        assert "creator" in capsule_detail
        assert "stats" in capsule_detail

        # 验证地理位置信息
        location = capsule_detail["location"]
        assert "latitude" in location
        assert "longitude" in location

        # 验证解锁条件
        unlock_conditions = capsule_detail["unlock_conditions"]
        assert "type" in unlock_conditions
        assert "is_unlocked" in unlock_conditions

        # 验证创建者信息
        creator = capsule_detail["creator"]
        assert "user_id" in creator
        assert "nickname" in creator

        # 验证统计信息
        stats = capsule_detail["stats"]
        assert "view_count" in stats
        assert "like_count" in stats
        assert "comment_count" in stats
        assert "unlock_count" in stats

        print(f"✅ 获取胶囊详情成功: {capsule_detail['title']}")

    def test_get_nonexistent_capsule(self, admin_token):
        """测试获取不存在的胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        response = requests.get(f"{base_url}/capsules/999999", headers=headers)

        # 应该返回404或相应的错误状态码
        assert response.status_code in [404, 400]

        print("✅ 获取不存在胶囊测试通过")

    def test_update_capsule(self, admin_token, created_capsule_ids):
        """测试更新胶囊"""
        if not created_capsule_ids:
            pytest.skip("没有可用的胶囊ID进行测试")

        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = created_capsule_ids[0]

        # 更新数据
        update_data = {
            "title": "更新后的标题",
            "content": "更新后的内容",
            "visibility": "friends"
        }

        response = requests.put(f"{base_url}/capsules/{capsule_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "更新成功" in data["message"]

        update_response = data["data"]
        assert update_response["capsule_id"] == capsule_id
        assert "updated_at" in update_response

        print(f"✅ 更新胶囊成功: {capsule_id}")

    def test_update_capsule_partial(self, admin_token, created_capsule_ids):
        """测试部分更新胶囊"""
        if len(created_capsule_ids) < 2:
            pytest.skip("需要至少2个胶囊进行部分更新测试")

        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = created_capsule_ids[1]

        # 只更新标题
        update_data = {
            "title": "部分更新的标题"
        }

        response = requests.put(f"{base_url}/capsules/{capsule_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        print(f"✅ 部分更新胶囊成功: {capsule_id}")

    def test_update_capsule_validation_errors(self, admin_token, created_capsule_ids):
        """测试更新胶囊时的验证错误"""
        if not created_capsule_ids:
            pytest.skip("没有可用的胶囊ID进行测试")

        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = created_capsule_ids[0]

        # 测试空标题
        update_data = {
            "title": "",
            "content": "有效内容"
        }

        response = requests.put(f"{base_url}/capsules/{capsule_id}", json=update_data, headers=headers)
        assert response.status_code == 422

        # 测试空内容
        update_data = {
            "title": "有效标题",
            "content": ""
        }

        response = requests.put(f"{base_url}/capsules/{capsule_id}", json=update_data, headers=headers)
        assert response.status_code == 422

        print("✅ 更新胶囊验证错误测试通过")

    def test_delete_capsule(self, admin_token, created_capsule_ids):
        """测试删除胶囊"""
        if not created_capsule_ids:
            pytest.skip("没有可用的胶囊ID进行删除测试")

        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = created_capsule_ids.pop()  # 删除最后一个创建的胶囊

        response = requests.delete(f"{base_url}/capsules/{capsule_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "删除成功" in data["message"]

        # 验证胶囊已被删除
        response = requests.get(f"{base_url}/capsules/{capsule_id}", headers=headers)
        assert response.status_code in [404, 400]

        print(f"✅ 删除胶囊成功: {capsule_id}")

    def test_save_draft(self, admin_token):
        """测试保存草稿"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        draft_data = {
            "title": "草稿胶囊",
            "content": "这是一个草稿胶囊",
            "visibility": "private"
        }

        response = requests.post(f"{base_url}/capsules/drafts", json=draft_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "草稿保存成功" in data["message"]

        draft_response = data["data"]
        assert "draft_id" in draft_response
        assert "saved_at" in draft_response

        print(f"✅ 保存草稿成功: {draft_response['draft_id']}")

    def test_save_empty_draft(self, admin_token):
        """测试保存空草稿"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 只有标题的草稿
        draft_data = {
            "title": "只有标题的草稿"
        }

        response = requests.post(f"{base_url}/capsules/drafts", json=draft_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        print("✅ 保存空草稿成功")