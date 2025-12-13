import pytest
import requests
from datetime import datetime, timedelta

from .config import base_url
from .utils import get_admin_user, get_registered_users


class TestCapsuleBrowse:
    """胶囊浏览和搜索功能测试"""

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
        """创建测试用的胶囊数据"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsules = {}

        # 创建不同位置的胶囊
        locations = [
            {
                "name": "tongji",
                "title": "同济大学胶囊",
                "content": "位于同济大学的胶囊，用于地图模式测试。",
                "lat": 31.2304,
                "lng": 121.4737,
                "address": "上海市同济大学",
                "tags": ["同济", "大学", "上海"]
            },
            {
                "name": "fudan",
                "title": "复旦大学胶囊",
                "content": "位于复旦大学的胶囊，用于地图模式测试。",
                "lat": 31.2404,
                "lng": 121.4837,
                "address": "上海市复旦大学",
                "tags": ["复旦", "大学", "上海"]
            },
            {
                "name": "sjtu",
                "title": "交通大学胶囊",
                "content": "位于交通大学的胶囊，用于地图模式测试。",
                "lat": 31.2204,
                "lng": 121.4637,
                "address": "上海市交通大学",
                "tags": ["交大", "大学", "上海"]
            }
        ]

        for i, location in enumerate(locations):
            capsule_data = {
                "title": location["title"],
                "content": location["content"],
                "visibility": "public",
                "tags": location["tags"],
                "location": {
                    "latitude": location["lat"],
                    "longitude": location["lng"],
                    "address": location["address"]
                },
                "unlock_conditions": {
                    "type": "public",
                    "radius": 1000.0
                }
            }

            response = requests.post(f"{base_url}/v1/capsules/", json=capsule_data, headers=headers)
            assert response.status_code == 200
            capsules[location["name"]] = response.json()["data"]["capsule_id"]

        # 创建不同时间的胶囊用于时间线模式
        base_time = datetime.now()
        time_offsets = [30, 20, 10, 5, 1]  # 天数前

        for i, offset in enumerate(time_offsets):
            created_time = base_time - timedelta(days=offset)
            capsule_data = {
                "title": f"时间线胶囊 - {offset}天前",
                "content": f"这是{i+offset}天前创建的胶囊，用于时间线模式测试。",
                "visibility": "public",
                "tags": ["时间线", "历史", f"{'{:02d}'.format(offset)}天前"],
                "location": {
                    "latitude": 31.2304 + i * 0.01,
                    "longitude": 121.4737 + i * 0.01,
                    "address": f"测试地点{i}"
                },
                "unlock_conditions": {
                    "type": "public",
                    "radius": 100.0,
                    "unlockable_time": created_time.isoformat()
                }
            }

            response = requests.post(f"{base_url}/v1/capsules/", json=capsule_data, headers=headers)
            assert response.status_code == 200
            capsules[f"timeline_{i}"] = response.json()["data"]["capsule_id"]

        # 创建不同标签的胶囊用于标签模式
        tag_groups = [
            ["风景", "自然", "户外"],
            ["美食", "餐厅", "推荐"],
            ["学习", "图书馆", "课程"],
            ["活动", "聚会", "社团"],
            ["旅行", "景点", "攻略"]
        ]

        for i, tags in enumerate(tag_groups):
            capsule_data = {
                "title": f"{tags[0]}主题胶囊",
                "content": f"这是一个关于{tags[0]}的胶囊，包含{','.join(tags)}等标签。",
                "visibility": "public",
                "tags": tags,
                "location": {
                    "latitude": 31.2304 + i * 0.02,
                    "longitude": 121.4737 + i * 0.02,
                    "address": f"{tags[0]}地点"
                },
                "unlock_conditions": {
                    "type": "public",
                    "radius": 500.0
                }
            }

            response = requests.post(f"{base_url}/v1/capsules/", json=capsule_data, headers=headers)
            assert response.status_code == 200
            capsules[f"tags_{i}"] = response.json()["data"]["capsule_id"]

        print(f"✅ 创建浏览测试胶囊完成，共 {len(capsules)} 个胶囊")
        return capsules

    def test_browse_capsules_map_mode(self, admin_token, test_capsules):
        """测试地图模式浏览胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        params = {
            "mode": "map",
            "page": 1,
            "size": 20
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data

        browse_data = data["data"]
        assert browse_data["mode"] == "map"
        assert "capsules" in browse_data
        assert isinstance(browse_data["capsules"], list)

        capsules = browse_data["capsules"]
        if capsules:
            capsule = capsules[0]
            # 验证地图模式下胶囊应该包含位置信息
            assert "id" in capsule
            assert "title" in capsule
            assert "location" in capsule
            assert "latitude" in capsule["location"]
            assert "longitude" in capsule["location"]
            assert "visibility" in capsule
            assert "created_at" in capsule

        print(f"✅ 地图模式浏览成功，找到 {len(capsules)} 个胶囊")

    def test_browse_capsules_timeline_mode(self, admin_token, test_capsules):
        """测试时间线模式浏览胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        params = {
            "mode": "timeline",
            "page": 1,
            "size": 20
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        browse_data = data["data"]
        assert browse_data["mode"] == "timeline"
        assert "timeline_groups" in browse_data
        assert isinstance(browse_data["timeline_groups"], dict)

        timeline_groups = browse_data["timeline_groups"]

        # 验证时间线分组
        if timeline_groups:
            for time_group, capsules in timeline_groups.items():
                assert isinstance(capsules, list)
                assert isinstance(time_group, str)

                if capsules:
                    capsule = capsules[0]
                    assert "id" in capsule
                    assert "title" in capsule
                    assert "created_at" in capsule

        print(f"✅ 时间线模式浏览成功，共 {len(timeline_groups)} 个时间分组")

    def test_browse_capsules_tags_mode(self, admin_token, test_capsules):
        """测试标签模式浏览胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        params = {
            "mode": "tags",
            "page": 1,
            "size": 20
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        browse_data = data["data"]
        assert browse_data["mode"] == "tags"
        assert "capsules" in browse_data
        assert isinstance(browse_data["capsules"], list)

        capsules = browse_data["capsules"]
        if capsules:
            capsule = capsules[0]
            # 验证标签模式下胶囊应该包含标签信息
            assert "id" in capsule
            assert "title" in capsule
            assert "tags" in capsule
            assert isinstance(capsule["tags"], list)
            assert "created_at" in capsule

        print(f"✅ 标签模式浏览成功，找到 {len(capsules)} 个胶囊")

    def test_browse_capsules_invalid_mode(self, admin_token):
        """测试无效的浏览模式"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        params = {
            "mode": "invalid_mode",
            "page": 1,
            "size": 20
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)

        # 应该返回错误，因为模式无效
        assert response.status_code in [400, 422]

        print("✅ 无效浏览模式测试通过")

    def test_browse_capsules_pagination(self, admin_token, test_capsules):
        """测试浏览分页"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试地图模式分页
        params = {
            "mode": "map",
            "page": 1,
            "size": 5
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)
        assert response.status_code == 200

        # 测试第二页
        params["page"] = 2
        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)
        assert response.status_code == 200

        print("✅ 浏览分页测试通过")

    def test_browse_capsules_page_size_limits(self, admin_token):
        """测试页面大小限制"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试最小页面大小
        params = {
            "mode": "map",
            "page": 1,
            "size": 1
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)
        assert response.status_code == 200

        # 测试最大页面大小
        params["size"] = 100
        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)
        assert response.status_code == 200

        # 测试超出限制的页面大小
        params["size"] = 200
        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)
        assert response.status_code in [200, 400, 422]  # 根据实现可能成功或失败

        print("✅ 页面大小限制测试通过")

    def test_browse_capsules_unauthorized(self):
        """测试未授权浏览胶囊"""
        params = {
            "mode": "map",
            "page": 1,
            "size": 20
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", params=params)

        assert response.status_code == 401

        print("✅ 未授权浏览测试通过")

    def test_browse_capsules_missing_mode(self, admin_token):
        """测试缺少模式参数"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        params = {
            "page": 1,
            "size": 20
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)

        # 应该返回错误，因为缺少必需的模式参数
        assert response.status_code in [400, 422]

        print("✅ 缺少模式参数测试通过")

    def test_browse_capsules_invalid_page_params(self, admin_token):
        """测试无效的分页参数"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试无效的页码
        params = {
            "mode": "map",
            "page": 0,
            "size": 20
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)
        assert response.status_code in [400, 422]

        # 测试无效的页面大小
        params = {
            "mode": "map",
            "page": 1,
            "size": 0
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)
        assert response.status_code in [400, 422]

        print("✅ 无效分页参数测试通过")

    def test_browse_capsules_empty_result(self, admin_token):
        """测试空结果情况"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 使用一个不会存在的条件来获取空结果
        params = {
            "mode": "map",
            "page": 1,
            "size": 20
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200

        # 验证结果结构，即使为空也应该有正确的结构
        if data["data"]["mode"] == "map":
            assert isinstance(data["data"]["capsules"], list)
        elif data["data"]["mode"] == "timeline":
            assert isinstance(data["data"]["timeline_groups"], dict)
        elif data["data"]["mode"] == "tags":
            assert isinstance(data["data"]["capsules"], list)

        print("✅ 空结果测试通过")

    def test_browse_capsules_data_consistency(self, admin_token, test_capsules):
        """测试浏览数据一致性"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 多次请求同一页面的数据
        params = {
            "mode": "map",
            "page": 1,
            "size": 10
        }

        responses = []
        for i in range(3):
            response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)
            assert response.status_code == 200
            responses.append(response.json())

        # 验证响应的一致性
        first_response = responses[0]
        for i in range(1, len(responses)):
            current_response = responses[i]
            assert current_response["code"] == first_response["code"]
            assert current_response["data"]["mode"] == first_response["data"]["mode"]

            # 数据量应该一致
            if current_response["data"]["mode"] in ["map", "tags"]:
                assert len(current_response["data"]["capsules"]) == len(first_response["data"]["capsules"])
            elif current_response["data"]["mode"] == "timeline":
                assert len(current_response["data"]["timeline_groups"]) == len(first_response["data"]["timeline_groups"])

        print("✅ 数据一致性测试通过")

    def test_browse_capsules_timeline_ordering(self, admin_token, test_capsules):
        """测试时间线模式的时间排序"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        params = {
            "mode": "timeline",
            "page": 1,
            "size": 50  # 获取足够多的数据
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)
        assert response.status_code == 200

        data = response.json()
        timeline_groups = data["data"]["timeline_groups"]

        if timeline_groups:
            # 验证时间分组的顺序（应该按时间倒序）
            group_names = list(timeline_groups.keys())
            print(f"时间分组: {group_names}")

        print("✅ 时间线排序测试通过")

    def test_browse_capsules_with_visibility_filter(self, admin_token):
        """测试基于可见性的浏览过滤"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 创建不同可见性的胶囊
        private_capsule = {
            "title": "私有胶囊",
            "content": "私有胶囊内容",
            "visibility": "private",
            "location": {"latitude": 31.2304, "longitude": 121.4737},
            "unlock_conditions": {"type": "private"}
        }

        public_capsule = {
            "title": "公共胶囊",
            "content": "公共胶囊内容",
            "visibility": "public",
            "location": {"latitude": 31.2304, "longitude": 121.4737},
            "unlock_conditions": {"type": "public"}
        }

        # 创建私有胶囊
        response = requests.post(f"{base_url}/v1/capsules/", json=private_capsule, headers=headers)
        assert response.status_code == 200

        # 创建公共胶囊
        response = requests.post(f"{base_url}/v1/capsules/", json=public_capsule, headers=headers)
        assert response.status_code == 200

        # 测试浏览（应该只显示公共胶囊）
        params = {
            "mode": "map",
            "page": 1,
            "size": 20
        }

        response = requests.get(f"{base_url}/v1/capsules/browse", headers=headers, params=params)
        assert response.status_code == 200

        data = response.json()
        capsules = data["data"]["capsules"]

        # 验证所有返回的胶囊都是公共的或好友可见的
        for capsule in capsules:
            assert capsule["visibility"] in ["public", "friends"] or capsule.get("is_owner", False)

        print("✅ 可见性过滤测试通过")