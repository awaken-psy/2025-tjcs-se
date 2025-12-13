import pytest
import requests
from datetime import datetime, timedelta

from .config import base_url
from .utils import get_admin_user, get_registered_users


class TestCapsuleUnlock:
    """胶囊解锁功能测试"""

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
    def test_capsules(self, admin_token):
        """创建测试用的胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsules = {}

        # 创建公共胶囊（无需密码）
        public_capsule = {
            "title": "公共测试胶囊",
            "content": "这是一个公共胶囊，任何人都可以解锁。",
            "visibility": "public",
            "tags": ["公共", "解锁"],
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

        response = requests.post(f"{base_url}/v1/capsules/", json=public_capsule, headers=headers)
        assert response.status_code == 200
        capsules["public"] = response.json()["data"]["capsule_id"]

        # 创建密码保护胶囊
        password_capsule = {
            "title": "密码保护胶囊",
            "content": "这个胶囊需要密码才能解锁。",
            "visibility": "public",
            "tags": ["密码", "保护"],
            "location": {
                "latitude": 31.2404,
                "longitude": 121.4837,
                "address": "上海市复旦大学"
            },
            "unlock_conditions": {
                "type": "password",
                "password": "test123456",
                "radius": 50.0
            }
        }

        response = requests.post(f"{base_url}/v1/capsules/", json=password_capsule, headers=headers)
        assert response.status_code == 200
        capsules["password"] = response.json()["data"]["capsule_id"]

        # 创建时间锁定胶囊
        time_capsule = {
            "title": "时间锁定胶囊",
            "content": "这个胶囊在特定时间后才能解锁。",
            "visibility": "public",
            "tags": ["时间", "锁定"],
            "location": {
                "latitude": 31.2204,
                "longitude": 121.4637,
                "address": "上海市交通大学"
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0,
                "unlockable_time": (datetime.now() - timedelta(hours=1)).isoformat()
            }
        }

        response = requests.post(f"{base_url}/v1/capsules/", json=time_capsule, headers=headers)
        assert response.status_code == 200
        capsules["time"] = response.json()["data"]["capsule_id"]

        # 创建位置锁定胶囊
        location_capsule = {
            "title": "位置锁定胶囊",
            "content": "这个胶囊需要在特定位置才能解锁。",
            "visibility": "public",
            "tags": ["位置", "地理"],
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737,
                "address": "上海市同济大学"
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 10.0  # 很小的半径，需要精确位置
            }
        }

        response = requests.post(f"{base_url}/v1/capsules/", json=location_capsule, headers=headers)
        assert response.status_code == 200
        capsules["location"] = response.json()["data"]["capsule_id"]

        # 创建未来时间胶囊（暂时不能解锁）
        future_capsule = {
            "title": "未来时间胶囊",
            "content": "这个胶囊在未来才能解锁。",
            "visibility": "public",
            "tags": ["未来", "时间"],
            "location": {
                "latitude": 31.2504,
                "longitude": 121.4937,
                "address": "上海市华东理工大学"
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0,
                "unlockable_time": (datetime.now() + timedelta(days=1)).isoformat()
            }
        }

        response = requests.post(f"{base_url}/v1/capsules/", json=future_capsule, headers=headers)
        assert response.status_code == 200
        capsules["future"] = response.json()["data"]["capsule_id"]

        print(f"✅ 创建测试胶囊完成: {capsules}")
        return capsules

    def test_unlock_public_capsule(self, admin_token, test_capsules):
        """测试解锁公共胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["public"]

        unlock_data = {
            "current_location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            }
        }

        response = requests.post(f"{base_url}/v1/unlock/{capsule_id}", json=unlock_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "胶囊解锁成功" in data["message"]

        unlock_response = data["data"]
        assert unlock_response["capsule_id"] == capsule_id
        assert "unlocked_at" in unlock_response
        assert "access_token" in unlock_response

        print(f"✅ 公共胶囊解锁成功: {capsule_id}")

    def test_unlock_password_protected_capsule_correct_password(self, admin_token, test_capsules):
        """测试使用正确密码解锁密码保护胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["password"]

        unlock_data = {
            "current_location": {
                "latitude": 31.2404,
                "longitude": 121.4837
            },
            "password": "test123456"
        }

        response = requests.post(f"{base_url}/v1/unlock/{capsule_id}", json=unlock_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "胶囊解锁成功" in data["message"]

        print(f"✅ 密码保护胶囊解锁成功: {capsule_id}")

    def test_unlock_password_protected_capsule_wrong_password(self, admin_token, test_capsules):
        """测试使用错误密码解锁密码保护胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["password"]

        unlock_data = {
            "current_location": {
                "latitude": 31.2404,
                "longitude": 121.4837
            },
            "password": "wrong_password"
        }

        response = requests.post(f"{base_url}/v1/unlock/{capsule_id}", json=unlock_data, headers=headers)

        # 应该返回错误状态码
        assert response.status_code in [400, 403, 422]

        print(f"✅ 密码错误解锁失败测试通过: {capsule_id}")

    def test_unlock_time_locked_capsule_after_time(self, admin_token, test_capsules):
        """测试在解锁时间后解锁时间锁定胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["time"]

        unlock_data = {
            "current_location": {
                "latitude": 31.2204,
                "longitude": 121.4637
            }
        }

        response = requests.post(f"{base_url}/v1/unlock/{capsule_id}", json=unlock_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        print(f"✅ 时间锁定胶囊解锁成功: {capsule_id}")

    def test_unlock_future_time_capsule_before_time(self, admin_token, test_capsules):
        """测试在解锁时间前尝试解锁未来胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["future"]

        unlock_data = {
            "current_location": {
                "latitude": 31.2504,
                "longitude": 121.4937
            }
        }

        response = requests.post(f"{base_url}/v1/unlock/{capsule_id}", json=unlock_data, headers=headers)

        # 应该返回错误，因为时间未到
        assert response.status_code in [400, 403]

        print(f"✅ 未来胶囊时间未到解锁失败测试通过: {capsule_id}")

    def test_unlock_location_locked_capsule_within_radius(self, admin_token, test_capsules):
        """测试在指定半径内解锁位置锁定胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["location"]

        # 在胶囊位置的很小范围内
        unlock_data = {
            "current_location": {
                "latitude": 31.2304,
                "longitude": 121.4737  # 完全相同的位置
            }
        }

        response = requests.post(f"{base_url}/v1/unlock/{capsule_id}", json=unlock_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        print(f"✅ 位置锁定胶囊在范围内解锁成功: {capsule_id}")

    def test_unlock_location_locked_capsule_outside_radius(self, admin_token, test_capsules):
        """测试在指定半径外尝试解锁位置锁定胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["location"]

        # 在胶囊位置很远的地方
        unlock_data = {
            "current_location": {
                "latitude": 31.0304,
                "longitude": 121.2737  # 很远的位置
            }
        }

        response = requests.post(f"{base_url}/v1/unlock/{capsule_id}", json=unlock_data, headers=headers)

        # 应该返回错误，因为位置太远
        assert response.status_code in [400, 403]

        print(f"✅ 位置锁定胶囊范围外解锁失败测试通过: {capsule_id}")

    def test_unlock_capsule_without_location(self, admin_token, test_capsules):
        """测试不提供位置信息解锁胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["public"]

        unlock_data = {}

        response = requests.post(f"{base_url}/v1/unlock/{capsule_id}", json=unlock_data, headers=headers)

        # 应该返回错误，因为缺少位置信息
        assert response.status_code in [400, 422]

        print("✅ 缺少位置信息解锁失败测试通过")

    def test_unlock_nonexistent_capsule(self, admin_token):
        """测试解锁不存在的胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        unlock_data = {
            "current_location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            }
        }

        response = requests.post(f"{base_url}/v1/unlock/999999", json=unlock_data, headers=headers)

        # 应该返回404或相应的错误状态码
        assert response.status_code in [404, 400]

        print("✅ 解锁不存在胶囊测试通过")

    def test_unlock_capsule_unauthorized(self, test_capsules):
        """测试未授权解锁胶囊"""
        capsule_id = test_capsules["public"]

        unlock_data = {
            "current_location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            }
        }

        response = requests.post(f"{base_url}/v1/unlock/{capsule_id}", json=unlock_data)

        assert response.status_code == 401

        print("✅ 未授权解锁胶囊测试通过")

    def test_get_nearby_capsules(self, admin_token, test_capsules):
        """测试获取附近胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        params = {
            "latitude": 31.2304,
            "longitude": 121.4737,
            "radius_meters": 1000,
            "page": 1,
            "limit": 10
        }

        response = requests.get(f"{base_url}/v1/unlock/nearby", headers=headers, params=params)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "capsules" in data["data"]

        capsules = data["data"]["capsules"]
        assert isinstance(capsules, list)

        # 验证胶囊信息结构
        if capsules:
            capsule = capsules[0]
            assert "id" in capsule
            assert "title" in capsule
            assert "location" in capsule
            assert "visibility" in capsule
            assert "is_unlocked" in capsule
            assert "can_unlock" in capsule
            assert "creator_nickname" in capsule
            assert "created_at" in capsule

            # 验证位置信息包含距离
            location = capsule["location"]
            assert "latitude" in location
            assert "longitude" in location
            assert "distance" in location  # 距离应该包含在内

        print(f"✅ 获取附近胶囊成功，找到 {len(capsules)} 个胶囊")

    def test_get_nearby_capsules_with_different_radius(self, admin_token):
        """测试使用不同半径获取附近胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试小半径
        params = {
            "latitude": 31.2304,
            "longitude": 121.4737,
            "radius_meters": 10,
            "page": 1,
            "limit": 5
        }

        response = requests.get(f"{base_url}/v1/unlock/nearby", headers=headers, params=params)
        assert response.status_code == 200

        # 测试大半径
        params["radius_meters"] = 10000
        response = requests.get(f"{base_url}/v1/unlock/nearby", headers=headers, params=params)
        assert response.status_code == 200

        print("✅ 不同半径获取附近胶囊测试通过")

    def test_get_nearby_capsules_pagination(self, admin_token):
        """测试附近胶囊分页"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 第一页
        params = {
            "latitude": 31.2304,
            "longitude": 121.4737,
            "radius_meters": 1000,
            "page": 1,
            "limit": 3
        }

        response = requests.get(f"{base_url}/v1/unlock/nearby", headers=headers, params=params)
        assert response.status_code == 200

        # 第二页
        params["page"] = 2
        response = requests.get(f"{base_url}/v1/unlock/nearby", headers=headers, params=params)
        assert response.status_code == 200

        print("✅ 附近胶囊分页测试通过")

    def test_get_unlock_status(self, admin_token, test_capsules):
        """测试获取胶囊解锁状态"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["public"]

        response = requests.get(f"{base_url}/v1/unlock/{capsule_id}/status", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data

        status_data = data["data"]
        assert "capsule_id" in status_data
        assert "is_unlocked" in status_data
        assert "can_unlock" in status_data
        assert "unlock_time" in status_data
        assert "failed_conditions" in status_data
        assert "conditions_met" in status_data

        print(f"✅ 获取解锁状态成功: {capsule_id}")

    def test_get_unlock_status_future_capsule(self, admin_token, test_capsules):
        """测试获取未来胶囊的解锁状态"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["future"]

        response = requests.get(f"{base_url}/v1/unlock/{capsule_id}/status", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        status_data = data["data"]
        # 未来胶囊应该显示未解锁
        assert status_data["is_unlocked"] == False
        assert "unlock_time" not in status_data or status_data["unlock_time"] is None
        # 应该有失败的解锁条件（时间未到）
        assert isinstance(status_data["failed_conditions"], list)

        print(f"✅ 获取未来胶囊解锁状态成功: {capsule_id}")

    def test_get_unlock_status_nonexistent_capsule(self, admin_token):
        """测试获取不存在胶囊的解锁状态"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        response = requests.get(f"{base_url}/v1/unlock/999999/status", headers=headers)

        # 应该返回404或相应的错误状态码
        assert response.status_code in [404, 400]

        print("✅ 获取不存在胶囊解锁状态测试通过")

    def test_unlock_validation_errors(self, admin_token):
        """测试解锁时的验证错误"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试无效的位置数据
        unlock_data = {
            "current_location": {
                "latitude": "invalid_lat",
                "longitude": 121.4737
            }
        }

        response = requests.post(f"{base_url}/v1/unlock/1", json=unlock_data, headers=headers)
        assert response.status_code in [400, 422]

        # 测试缺少经度
        unlock_data = {
            "current_location": {
                "latitude": 31.2304
            }
        }

        response = requests.post(f"{base_url}/v1/unlock/1", json=unlock_data, headers=headers)
        assert response.status_code in [400, 422]

        print("✅ 解锁验证错误测试通过")