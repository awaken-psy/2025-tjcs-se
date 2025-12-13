import pytest
import requests
from datetime import datetime, timedelta

from .config import base_url
from .utils import get_admin_user, get_registered_users


class TestCapsuleHub:
    """胶囊Hub相关功能测试"""

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
        """创建Hub测试用的胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsules = {}

        # 在不同位置创建胶囊用于Hub附近功能测试
        locations = [
            {
                "name": "hub_nearby_1",
                "title": "Hub附近胶囊1",
                "content": "用于Hub附近功能测试的胶囊1。",
                "lat": 31.2304,
                "lng": 121.4737,
                "address": "上海市同济大学",
                "visibility": "public"
            },
            {
                "name": "hub_nearby_2",
                "title": "Hub附近胶囊2",
                "content": "用于Hub附近功能测试的胶囊2。",
                "lat": 31.2350,
                "lng": 121.4780,
                "address": "上海市同济大学附近",
                "visibility": "public"
            },
            {
                "name": "hub_far",
                "title": "Hub远距离胶囊",
                "content": "用于Hub附近功能测试的远距离胶囊。",
                "lat": 31.1000,
                "lng": 121.3000,
                "address": "上海市远郊",
                "visibility": "public"
            }
        ]

        for location in locations:
            capsule_data = {
                "title": location["title"],
                "content": location["content"],
                "visibility": location["visibility"],
                "tags": ["Hub", "测试", "附近"],
                "location": {
                    "latitude": location["lat"],
                    "longitude": location["lng"],
                    "address": location["address"]
                },
                "unlock_conditions": {
                    "type": "public",
                    "radius": 100.0
                }
            }

            response = requests.post(f"{base_url}/v1/capsules/", json=capsule_data, headers=headers)
            assert response.status_code == 200
            capsules[location["name"]] = response.json()["data"]["capsule_id"]

        print(f"✅ 创建Hub测试胶囊完成，共 {len(capsules)} 个胶囊")
        return capsules

    def test_get_user_info(self, admin_token):
        """测试获取用户信息"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        response = requests.get(f"{base_url}/v1/hub/user-info", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "获取成功" in data["message"]

        user_info = data["data"]
        assert "user_id" in user_info
        assert "nickname" in user_info
        assert "email" in user_info
        assert "created_at" in user_info
        assert "stats" in user_info

        # 验证统计信息
        stats = user_info["stats"]
        assert "created_capsules" in stats
        assert "unlocked_capsules" in stats
        assert "friends_count" in stats
        assert "collection_count" in stats

        # 验证数据类型
        assert isinstance(stats["created_capsules"], int)
        assert isinstance(stats["unlocked_capsules"], int)
        assert isinstance(stats["friends_count"], int)
        assert isinstance(stats["collection_count"], int)

        print(f"✅ 获取用户信息成功: {user_info['nickname']}")
        print(f"   - 创建胶囊: {stats['created_capsules']}")
        print(f"   - 解锁胶囊: {stats['unlocked_capsules']}")
        print(f"   - 好友数量: {stats['friends_count']}")
        print(f"   - 收藏数量: {stats['collection_count']}")

    def test_get_user_info_unauthorized(self):
        """测试未授权获取用户信息"""
        response = requests.get(f"{base_url}/v1/hub/user-info")

        assert response.status_code == 401

        print("✅ 未授权获取用户信息测试通过")

    def test_get_hub_nearby_capsules(self, admin_token, test_capsules):
        """测试获取Hub附近胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 使用同济大学的位置
        params = {
            "lat": 31.2304,
            "lng": 121.4737,
            "range": 1000,  # 1公里范围
            "page": 1,
            "limit": 20
        }

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "获取成功" in data["message"]

        capsules = data["data"]
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

            # 验证位置信息
            location = capsule["location"]
            assert "latitude" in location
            assert "longitude" in location
            assert "distance" in location  # 应该包含距离信息

            # 验证距离是合理的数字
            assert isinstance(location["distance"], (int, float))
            assert location["distance"] >= 0

        print(f"✅ 获取Hub附近胶囊成功，找到 {len(capsules)} 个胶囊")

    def test_get_hub_nearby_capsules_different_ranges(self, admin_token):
        """测试不同范围的附近胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        base_params = {
            "lat": 31.2304,
            "lng": 121.4737,
            "page": 1,
            "limit": 20
        }

        # 测试小范围
        params = base_params.copy()
        params["range"] = 100  # 100米

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code == 200
        small_range_capsules = response.json()["data"]

        # 测试中等范围
        params["range"] = 500  # 500米

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code == 200
        medium_range_capsules = response.json()["data"]

        # 测试大范围
        params["range"] = 2000  # 2公里

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code == 200
        large_range_capsules = response.json()["data"]

        # 验证范围越大，胶囊数量可能越多
        print(f"✅ 不同范围附近胶囊测试:")
        print(f"   - 100米范围: {len(small_range_capsules)} 个胶囊")
        print(f"   - 500米范围: {len(medium_range_capsules)} 个胶囊")
        print(f"   - 2公里范围: {len(large_range_capsules)} 个胶囊")

    def test_get_hub_nearby_capsules_pagination(self, admin_token):
        """测试附近胶囊分页"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        params = {
            "lat": 31.2304,
            "lng": 121.4737,
            "range": 10000,  # 大范围确保有足够的数据
            "page": 1,
            "limit": 5
        }

        # 第一页
        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code == 200
        first_page = response.json()["data"]

        # 第二页
        params["page"] = 2
        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code == 200
        second_page = response.json()["data"]

        print(f"✅ 附近胶囊分页测试:")
        print(f"   - 第1页: {len(first_page)} 个胶囊")
        print(f"   - 第2页: {len(second_page)} 个胶囊")

    def test_get_hub_nearby_capsules_range_limits(self, admin_token):
        """测试附近胶囊范围限制"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        base_params = {
            "lat": 31.2304,
            "lng": 121.4737,
            "page": 1,
            "limit": 20
        }

        # 测试最小范围
        params = base_params.copy()
        params["range"] = 10  # 10米

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code == 200

        # 测试最大范围
        params["range"] = 1000000  # 1000公里

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code == 200

        # 测试超出限制的范围
        params["range"] = 2000000  # 2000公里

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        # 根据实现可能成功或失败
        assert response.status_code in [200, 400, 422]

        print("✅ 附近胶囊范围限制测试通过")

    def test_get_hub_nearby_capsules_limit_validation(self, admin_token):
        """测试附近胶囊数量限制"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        params = {
            "lat": 31.2304,
            "lng": 121.4737,
            "range": 1000,
            "page": 1
        }

        # 测试最小限制
        params["limit"] = 1
        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code == 200
        result = response.json()["data"]
        assert len(result) <= 1

        # 测试最大限制
        params["limit"] = 100
        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code == 200

        # 测试超出限制
        params["limit"] = 200
        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        # 根据实现可能成功或失败
        assert response.status_code in [200, 400, 422]

        print("✅ 附近胶囊数量限制测试通过")

    def test_get_hub_nearby_capsules_missing_params(self, admin_token):
        """测试缺少必需参数"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 缺少纬度
        params = {
            "lng": 121.4737,
            "range": 1000,
            "page": 1,
            "limit": 20
        }

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code in [400, 422]

        # 缺少经度
        params = {
            "lat": 31.2304,
            "range": 1000,
            "page": 1,
            "limit": 20
        }

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code in [400, 422]

        print("✅ 缺少参数测试通过")

    def test_get_hub_nearby_capsules_invalid_location(self, admin_token):
        """测试无效的地理位置参数"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 无效的纬度
        params = {
            "lat": "invalid_lat",
            "lng": 121.4737,
            "range": 1000,
            "page": 1,
            "limit": 20
        }

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code in [400, 422]

        # 超出范围的纬度
        params = {
            "lat": 91.0,  # 超出纬度范围
            "lng": 121.4737,
            "range": 1000,
            "page": 1,
            "limit": 20
        }

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code in [400, 422]

        # 超出范围的经度
        params = {
            "lat": 31.2304,
            "lng": 181.0,  # 超出经度范围
            "range": 1000,
            "page": 1,
            "limit": 20
        }

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code in [400, 422]

        print("✅ 无效地理位置参数测试通过")

    def test_get_hub_nearby_capsules_empty_result(self, admin_token):
        """测试空结果情况"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 使用一个不太可能有胶囊的位置
        params = {
            "lat": 0.0,
            "lng": 0.0,
            "range": 10,  # 很小的范围
            "page": 1,
            "limit": 20
        }

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        capsules = data["data"]
        assert isinstance(capsules, list)
        # 可能为空列表

        print(f"✅ 空结果测试: 找到 {len(capsules)} 个胶囊")

    def test_get_hub_nearby_capsules_unauthorized(self):
        """测试未授权获取附近胶囊"""
        params = {
            "lat": 31.2304,
            "lng": 121.4737,
            "range": 1000,
            "page": 1,
            "limit": 20
        }

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", params=params)

        assert response.status_code == 401

        print("✅ 未授权获取附近胶囊测试通过")

    def test_hub_distance_calculation(self, admin_token, test_capsules):
        """测试距离计算准确性"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 使用精确位置
        params = {
            "lat": 31.2304,
            "lng": 121.4737,
            "range": 1000,
            "page": 1,
            "limit": 50  # 获取更多数据
        }

        response = requests.get(f"{base_url}/v1/hub/nearby-capsules", headers=headers, params=params)
        assert response.status_code == 200

        capsules = response.json()["data"]

        # 验证距离计算
        for capsule in capsules:
            location = capsule["location"]
            distance = location["distance"]

            # 距离应该是非负数
            assert distance >= 0

            # 距离应该在指定范围内
            assert distance <= 1000

            # 距离应该是合理的精度
            assert isinstance(distance, (int, float))

        print(f"✅ 距离计算测试通过，验证了 {len(capsules)} 个胶囊的距离")

    def test_hub_user_info_stats_accuracy(self, admin_token, test_capsules):
        """测试用户信息统计准确性"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 获取创建胶囊前的统计信息
        response = requests.get(f"{base_url}/v1/hub/user-info", headers=headers)
        assert response.status_code == 200
        initial_stats = response.json()["data"]["stats"]
        initial_created = initial_stats["created_capsules"]

        # 创建一个新胶囊
        capsule_data = {
            "title": "统计测试胶囊",
            "content": "用于测试统计准确性的胶囊。",
            "visibility": "public",
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0
            }
        }

        response = requests.post(f"{base_url}/v1/capsules/", json=capsule_data, headers=headers)
        assert response.status_code == 200

        # 再次获取统计信息
        response = requests.get(f"{base_url}/v1/hub/user-info", headers=headers)
        assert response.status_code == 200
        new_stats = response.json()["data"]["stats"]
        new_created = new_stats["created_capsules"]

        # 验证统计信息更新
        assert new_created == initial_created + 1

        print(f"✅ 用户信息统计准确性测试通过")
        print(f"   - 初始创建胶囊数: {initial_created}")
        print(f"   - 新创建胶囊数: {new_created}")

    def test_multiple_users_hub_data(self, admin_token, user_tokens):
        """测试多用户Hub数据隔离"""
        if not user_tokens:
            pytest.skip("需要普通用户token进行测试")

        # 获取管理员的用户信息
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        admin_response = requests.get(f"{base_url}/v1/hub/user-info", headers=admin_headers)
        assert admin_response.status_code == 200
        admin_info = admin_response.json()["data"]

        # 获取普通用户的用户信息
        user_headers = {"Authorization": f"Bearer {user_tokens[0]['token']}"}
        user_response = requests.get(f"{base_url}/v1/hub/user-info", headers=user_headers)
        assert user_response.status_code == 200
        user_info = user_response.json()["data"]

        # 验证用户信息不同
        assert admin_info["user_id"] != user_info["user_id"]
        assert admin_info["email"] != user_info["email"]

        print("✅ 多用户Hub数据隔离测试通过")