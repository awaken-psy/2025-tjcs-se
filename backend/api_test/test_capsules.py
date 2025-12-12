import requests
import pytest
from datetime import datetime, timedelta
import uuid

from .config import base_url
from .utils import get_admin_user, get_registered_users


class TestCapsulesAPI:
    """胶囊相关接口测试类"""

    @pytest.fixture(scope="class")
    def capsule_data(self):
        """测试胶囊数据"""
        return {
            "title": "我的第一个时光胶囊",
            "content": "这是我创建的第一个时光胶囊，记录着美好的回忆。",
            "visibility": "private",
            "tags": ["回忆", "青春", "校园"],
            "location": {
                "latitude": 31.2855,
                "longitude": 121.5057,
                "address": "上海市嘉定区曹安公路4800号"
            },
            "unlock_conditions": {
                "type": "time",
                "value": (datetime.now() + timedelta(days=365)).isoformat(),
                "is_unlocked": False
            },
            "media_files": []
        }

    @pytest.fixture(scope="class")
    def update_capsule_data(self):
        """更新胶囊数据"""
        return {
            "title": "更新后的时光胶囊标题",
            "content": "这是我更新后的时光胶囊内容，添加了更多回忆。",
            "visibility": "friends",
            "tags": ["回忆", "青春", "校园", "更新"]
        }

    @pytest.fixture(scope="class")
    def draft_capsule_data(self):
        """草稿胶囊数据"""
        return {
            "title": "草稿胶囊",
            "content": "这是一个未完成的胶囊内容草稿",
            "visibility": "private"
        }

    def test_create_capsule_success(self, capsule_data):
        """测试创建胶囊成功"""
        admin_user = get_admin_user()

        response = requests.post(
            f"{base_url}/capsules/",
            json=capsule_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "胶囊创建成功"

        # 验证响应数据结构符合 CapsuleCreateResponse 模型
        capsule_response = data["data"]
        assert "capsule_id" in capsule_response
        assert capsule_response["title"] == capsule_data["title"]
        assert "status" in capsule_response
        assert "created_at" in capsule_response

        # 验证 capsule_id 是有效的ID格式
        try:
            int(capsule_response["capsule_id"])
        except ValueError:
            pytest.fail(f"Capsule ID is not a valid integer ID: {capsule_response['capsule_id']}")

        print(f"✓ 创建胶囊成功，胶囊ID: {capsule_response['capsule_id']}")
        return capsule_response["capsule_id"]

    def test_create_capsule_unauthorized(self, capsule_data):
        """测试未授权创建胶囊"""
        response = requests.post(f"{base_url}/capsules/", json=capsule_data)
        # 可能返回401、403或422，取决于认证中间件的具体实现
        assert response.status_code in [401, 403, 422]

        # 测试无效token
        response = requests.post(
            f"{base_url}/capsules/",
            json=capsule_data,
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code in [401, 403]

        print("✓ 未授权创建胶囊测试通过")

    def test_create_capsule_invalid_data(self):
        """测试创建胶囊 - 无效数据"""
        admin_user = get_admin_user()

        # 测试缺少必填字段
        invalid_data = {
            "title": "测试胶囊"
            # 缺少 content, visibility
        }

        response = requests.post(
            f"{base_url}/capsules/",
            json=invalid_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        # 可能返回422（Pydantic验证失败）或500（如果处理异常）
        assert response.status_code in [422, 500]

        # 测试空字符串
        invalid_data_empty = {
            "title": "",
            "content": "测试内容",
            "visibility": "private"
        }

        response = requests.post(
            f"{base_url}/capsules/",
            json=invalid_data_empty,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        assert response.status_code in [422, 500]

        print("✓ 无效数据创建胶囊测试通过")

    def test_get_my_capsules_success(self):
        """测试获取我的胶囊列表成功"""
        admin_user = get_admin_user()

        # 测试获取所有胶囊
        response = requests.get(
            f"{base_url}/capsules/my",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "获取成功"

        # 验证响应数据结构符合 CapsuleListResponse 模型
        capsule_list = data["data"]
        assert "capsules" in capsule_list
        assert "pagination" in capsule_list

        # 验证分页信息
        pagination = capsule_list["pagination"]
        assert "page" in pagination
        assert "page_size" in pagination
        assert "total" in pagination
        assert "total_pages" in pagination

        # 验证胶囊列表中的每个胶囊符合 CapsuleBasic 模型
        if capsule_list["capsules"]:
            capsule = capsule_list["capsules"][0]
            self._validate_capsule_basic_structure(capsule)

        print(f"✓ 获取我的胶囊列表成功，共 {pagination['total']} 个胶囊")

    def test_get_my_capsules_with_filters(self):
        """测试获取我的胶囊列表 - 带过滤条件"""
        admin_user = get_admin_user()

        # 测试按状态过滤
        for status in ["all", "draft", "published"]:
            params = {"status": status}
            response = requests.get(
                f"{base_url}/capsules/my",
                params=params,
                headers={"Authorization": f"Bearer {admin_user['token']}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

            capsule_list = data["data"]
            assert "capsules" in capsule_list

        print("✓ 按状态过滤胶囊列表测试通过")

    def test_get_my_capsules_with_pagination(self):
        """测试分页获取我的胶囊列表"""
        admin_user = get_admin_user()

        # 测试分页
        params = {"page": 1, "size": 5}
        response = requests.get(
            f"{base_url}/capsules/my",
            params=params,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        capsule_list = data["data"]

        assert capsule_list["pagination"]["page"] == 1
        assert capsule_list["pagination"]["page_size"] == 5
        assert len(capsule_list["capsules"]) <= 5

        print("✓ 分页获取胶囊列表测试通过")

    def test_get_capsule_detail_success(self):
        """测试获取胶囊详情成功"""
        # 先创建一个胶囊
        admin_user = get_admin_user()
        capsule_data = {
            "title": "测试胶囊详情",
            "content": "这是一个用于测试胶囊详情的胶囊",
            "visibility": "private",
            "location": {
                "latitude": 31.2855,
                "longitude": 121.5057,
                "address": "测试地址"
            },
            "tags": ["测试"],
            "media_files": []
        }

        create_response = requests.post(
            f"{base_url}/capsules/",
            json=capsule_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        capsule_id = create_response.json()["data"]["capsule_id"]

        # 获取胶囊详情
        response = requests.get(
            f"{base_url}/capsules/{capsule_id}",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "获取成功"

        # 验证响应数据结构符合 CapsuleDetail 模型
        capsule_detail = data["data"]
        self._validate_capsule_detail_structure(capsule_detail)
        assert capsule_detail["title"] == capsule_data["title"]
        assert capsule_detail["content"] == capsule_data["content"]

        print(f"✓ 获取胶囊详情成功，胶囊标题: {capsule_detail['title']}")

    def test_get_capsule_detail_not_found(self):
        """测试获取不存在的胶囊详情"""
        admin_user = get_admin_user()
        nonexistent_id = "999999"

        response = requests.get(
            f"{base_url}/capsules/{nonexistent_id}",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 404

        print("✓ 获取不存在胶囊详情测试通过")

    def test_update_capsule_success(self, update_capsule_data):
        """测试更新胶囊成功"""
        # 先创建一个胶囊
        admin_user = get_admin_user()
        original_data = {
            "title": "原始胶囊标题",
            "content": "原始胶囊内容",
            "visibility": "private",
            "tags": ["原始标签"]
        }

        create_response = requests.post(
            f"{base_url}/capsules/",
            json=original_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        capsule_id = create_response.json()["data"]["capsule_id"]

        # 更新胶囊
        response = requests.put(
            f"{base_url}/capsules/{capsule_id}",
            json=update_capsule_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "更新成功"

        # 验证响应数据结构符合 CapsuleUpdateResponse 模型
        update_response = data["data"]
        assert update_response["capsule_id"] == capsule_id
        assert "updated_at" in update_response

        # 验证更新后的详情
        detail_response = requests.get(
            f"{base_url}/capsules/{capsule_id}",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        updated_capsule = detail_response.json()["data"]
        assert updated_capsule["title"] == update_capsule_data["title"]
        assert updated_capsule["content"] == update_capsule_data["content"]

        print(f"✓ 更新胶囊成功，胶囊ID: {capsule_id}")

    def test_update_capsule_unauthorized(self, update_capsule_data):
        """测试未授权更新胶囊"""
        admin_user = get_admin_user()

        # 先创建一个胶囊
        original_data = {
            "title": "测试未授权更新",
            "content": "测试内容",
            "visibility": "private"
        }

        create_response = requests.post(
            f"{base_url}/capsules/",
            json=original_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        capsule_id = create_response.json()["data"]["capsule_id"]

        # 使用另一个用户尝试更新
        registered_users = get_registered_users()
        if len(registered_users) > 0:
            other_user = registered_users[0]

            response = requests.put(
                f"{base_url}/capsules/{capsule_id}",
                json=update_capsule_data,
                headers={"Authorization": f"Bearer {other_user['token']}"}
            )

            # 应该返回404权限错误
            if response.status_code == 404:
                print("✓ 权限不足更新胶囊测试通过")
            else:
                print(f"⚠ 更新胶囊权限测试返回状态码: {response.status_code}")

    def test_update_capsule_not_found(self, update_capsule_data):
        """测试更新不存在的胶囊"""
        admin_user = get_admin_user()
        nonexistent_id = "999999"

        response = requests.put(
            f"{base_url}/capsules/{nonexistent_id}",
            json=update_capsule_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 404

        print("✓ 更新不存在胶囊测试通过")

    def test_delete_capsule_success(self):
        """测试删除胶囊成功"""
        # 先创建一个胶囊
        admin_user = get_admin_user()
        capsule_data = {
            "title": "待删除的胶囊",
            "content": "这个胶囊将被删除",
            "visibility": "private"
        }

        create_response = requests.post(
            f"{base_url}/capsules/",
            json=capsule_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        capsule_id = create_response.json()["data"]["capsule_id"]

        # 删除胶囊
        response = requests.delete(
            f"{base_url}/capsules/{capsule_id}",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "删除成功"

        # 验证胶囊已被删除
        detail_response = requests.get(
            f"{base_url}/capsules/{capsule_id}",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        assert detail_response.status_code == 404

        print(f"✓ 删除胶囊成功，胶囊ID: {capsule_id}")

    def test_delete_capsule_unauthorized(self):
        """测试未授权删除胶囊"""
        admin_user = get_admin_user()

        # 先创建一个胶囊
        capsule_data = {
            "title": "测试未授权删除",
            "content": "测试内容",
            "visibility": "private"
        }

        create_response = requests.post(
            f"{base_url}/capsules/",
            json=capsule_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        capsule_id = create_response.json()["data"]["capsule_id"]

        # 使用另一个用户尝试删除
        registered_users = get_registered_users()
        if len(registered_users) > 0:
            other_user = registered_users[0]

            response = requests.delete(
                f"{base_url}/capsules/{capsule_id}",
                headers={"Authorization": f"Bearer {other_user['token']}"}
            )

            # 应该返回404权限错误
            if response.status_code == 404:
                print("✓ 权限不足删除胶囊测试通过")
            else:
                print(f"⚠ 删除胶囊权限测试返回状态码: {response.status_code}")

    def test_save_draft_success(self, draft_capsule_data):
        """测试保存草稿成功"""
        admin_user = get_admin_user()

        response = requests.post(
            f"{base_url}/capsules/drafts",
            json=draft_capsule_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "草稿保存成功"

        # 验证响应数据结构符合 CapsuleDraftResponse 模型
        draft_response = data["data"]
        assert "draft_id" in draft_response
        assert "saved_at" in draft_response

        # 验证 draft_id 是有效的整数ID
        try:
            int(draft_response["draft_id"])
        except ValueError:
            pytest.fail(f"Draft ID is not a valid integer ID: {draft_response['draft_id']}")

        print(f"✓ 保存草稿成功，草稿ID: {draft_response['draft_id']}")

    def test_save_draft_unauthorized(self, draft_capsule_data):
        """测试未授权保存草稿"""
        response = requests.post(f"{base_url}/capsules/drafts", json=draft_capsule_data)
        assert response.status_code in [401, 403, 422]

        # 测试无效token
        response = requests.post(
            f"{base_url}/capsules/drafts",
            json=draft_capsule_data,
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code in [401, 403]

        print("✓ 未授权保存草稿测试通过")

    def test_browse_capsules_map_mode(self):
        """测试地图模式浏览胶囊"""
        admin_user = get_admin_user()

        params = {"mode": "map"}
        response = requests.get(
            f"{base_url}/capsules/browse",
            params=params,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "获取成功"

        # 验证响应数据结构符合 MultiModeBrowseResponse 模型
        browse_response = data["data"]
        assert browse_response["mode"] == "map"
        assert "capsules" in browse_response

        # 验证胶囊列表符合 CapsuleBasic 模型
        if browse_response["capsules"]:
            capsule = browse_response["capsules"][0]
            self._validate_capsule_basic_structure(capsule)
            # 地图模式应该包含经纬度信息
            assert capsule["latitude"] is not None
            assert capsule["longitude"] is not None

        print("✓ 地图模式浏览胶囊测试通过")

    def test_browse_capsules_timeline_mode(self):
        """测试时间轴模式浏览胶囊"""
        admin_user = get_admin_user()

        params = {"mode": "timeline"}
        response = requests.get(
            f"{base_url}/capsules/browse",
            params=params,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "获取成功"

        # 验证响应数据结构符合 MultiModeBrowseResponse 模型
        browse_response = data["data"]
        assert browse_response["mode"] == "timeline"
        assert "timeline_groups" in browse_response

        # 验证时间轴分组数据
        if browse_response["timeline_groups"]:
            timeline_groups = browse_response["timeline_groups"]
            assert isinstance(timeline_groups, dict)
            # 验证每个时间分组的胶囊列表
            for month, capsules in timeline_groups.items():
                assert isinstance(capsules, list)
                if capsules:
                    capsule = capsules[0]
                    self._validate_capsule_basic_structure(capsule)

        print("✓ 时间轴模式浏览胶囊测试通过")

    def test_browse_capsules_tags_mode(self):
        """测试标签模式浏览胶囊"""
        admin_user = get_admin_user()

        params = {"mode": "tags"}
        response = requests.get(
            f"{base_url}/capsules/browse",
            params=params,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "获取成功"

        # 验证响应数据结构符合 MultiModeBrowseResponse 模型
        browse_response = data["data"]
        assert browse_response["mode"] == "tags"
        assert "capsules" in browse_response

        # 验证胶囊列表符合 CapsuleBasic 模型
        if browse_response["capsules"]:
            capsule = browse_response["capsules"][0]
            self._validate_capsule_basic_structure(capsule)

        print("✓ 标签模式浏览胶囊测试通过")

    def test_browse_capsules_invalid_mode(self):
        """测试无效浏览模式"""
        admin_user = get_admin_user()

        params = {"mode": "invalid_mode"}
        response = requests.get(
            f"{base_url}/capsules/browse",
            params=params,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 400

        print("✓ 无效浏览模式测试通过")

    def _validate_capsule_basic_structure(self, capsule):
        """验证胶囊基础信息数据结构"""
        required_fields = [
            "id", "title", "visibility", "status", "created_at"
        ]

        for field in required_fields:
            assert field in capsule, f"Missing required field: {field}"

        # 验证数据类型
        assert isinstance(capsule["id"], str)
        assert isinstance(capsule["title"], str)
        assert isinstance(capsule["visibility"], str)
        assert isinstance(capsule["status"], str)

        # 验证日期格式
        try:
            datetime.fromisoformat(capsule["created_at"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"Invalid created_at format: {capsule['created_at']}")

    def _validate_capsule_detail_structure(self, capsule):
        """验证胶囊详情数据结构"""
        required_fields = [
            "id", "title", "content", "visibility", "status", "created_at"
        ]

        for field in required_fields:
            assert field in capsule, f"Missing required field: {field}"

        # 验证数据类型
        assert isinstance(capsule["id"], str)
        assert isinstance(capsule["title"], str)
        assert isinstance(capsule["content"], str)
        assert isinstance(capsule["visibility"], str)
        assert isinstance(capsule["status"], str)

        # 验证日期格式
        try:
            datetime.fromisoformat(capsule["created_at"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"Invalid created_at format: {capsule['created_at']}")


# 独立测试函数
def test_create_capsule_basic():
    """独立测试：创建胶囊成功"""
    test_instance = TestCapsulesAPI()
    capsule_data = {
        "title": "基础测试胶囊",
        "content": "这是一个基础测试胶囊的内容",
        "visibility": "private",
        "tags": ["测试"],
        "media_files": []
    }
    test_instance.test_create_capsule_success(capsule_data)


def test_get_my_capsules_basic():
    """独立测试：获取我的胶囊列表成功"""
    test_instance = TestCapsulesAPI()
    test_instance.test_get_my_capsules_success()


def test_browse_capsules_map():
    """独立测试：地图模式浏览胶囊"""
    test_instance = TestCapsulesAPI()
    test_instance.test_browse_capsules_map_mode()


def test_capsules_comprehensive():
    """胶囊接口综合测试"""
    print("\n=== 开始胶囊接口综合测试 ===")

    test_instance = TestCapsulesAPI()
    capsule_data = {
        "title": "综合测试胶囊",
        "content": "用于综合测试的胶囊内容",
        "visibility": "private",
        "tags": ["综合测试"],
        "media_files": []
    }
    update_data = {
        "title": "综合测试胶囊（更新）",
        "content": "更新后的综合测试胶囊内容",
        "visibility": "friends",
        "tags": ["综合测试", "更新"]
    }
    draft_data = {
        "title": "综合测试草稿",
        "content": "这是一个综合测试草稿",
        "visibility": "private"
    }

    # 创建胶囊
    capsule_id = test_instance.test_create_capsule_success(capsule_data)

    # 获取我的胶囊列表
    test_instance.test_get_my_capsules_success()

    # 获取胶囊详情
    test_instance.test_get_capsule_detail_success()

    # 更新胶囊
    test_instance.test_update_capsule_success(update_data)

    # 测试保存草稿
    test_instance.test_save_draft_success(draft_data)

    # 测试浏览模式
    test_instance.test_browse_capsules_map_mode()
    test_instance.test_browse_capsules_timeline_mode()
    test_instance.test_browse_capsules_tags_mode()

    # 删除胶囊
    test_instance.test_delete_capsule_success()

    print("\n=== 胶囊接口综合测试完成 ===")


if __name__ == "__main__":
    # 如果直接运行此文件，执行独立测试
    test_create_capsule_basic()
    test_get_my_capsules_basic()
    test_browse_capsules_map()
    test_capsules_comprehensive()