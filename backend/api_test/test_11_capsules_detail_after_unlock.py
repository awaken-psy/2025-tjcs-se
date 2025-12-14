import pytest
import requests
from datetime import datetime, timedelta

from .config import base_url
from .utils import get_admin_user, get_registered_users


class TestCapsuleDetailAfterUnlock:
    """测试胶囊解锁后查看详情的相关字段"""

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

    def create_test_capsule(self, token, capsule_data, created_capsule_ids):
        """创建测试胶囊的辅助方法"""
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{base_url}/capsules/", json=capsule_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        capsule_id = data["data"]["capsule_id"]
        created_capsule_ids.append(capsule_id)
        return capsule_id

    def test_unlock_then_view_capsule_detail_complete_flow(self, admin_token, created_capsule_ids):
        """测试完整的解锁后查看胶囊详情流程"""

        # 1. 创建一个复杂的胶囊用于测试
        capsule_data = {
            "title": "完整解锁测试胶囊",
            "content": """这是一个复杂的测试胶囊内容，用于验证解锁后查看详情的完整性。

包含以下元素：
1. 多行文本内容
2. 中文字符测试：时光胶囊系统测试
3. 数字测试：1234567890
4. 英文测试：Time Capsule System
5. 特殊字符：!@#$%^&*()

这个内容用于验证所有字段在解锁后都能正确显示和更新。""",
            "visibility": "public",
            "tags": ["完整测试", "解锁验证", "字段检查"],
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737,
                "address": "上海市同济大学完整测试地址"
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0,
                "unlockable_time": (datetime.now() - timedelta(days=1)).isoformat()
            }
        }

        capsule_id = self.create_test_capsule(admin_token, capsule_data, created_capsule_ids)
        print(f"✅ 创建测试胶囊成功: {capsule_id}")

        # 2. 解锁前尝试查看（应该失败）
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{base_url}/capsules/{capsule_id}", headers=headers)

        # 管理员应该能够查看，即使未解锁
        assert response.status_code == 200
        unlock_response = response.json()
        assert unlock_response["code"] == 200
        capsule_detail_before = unlock_response["data"]

        print("✅ 管理员可以在解锁前查看胶囊")

        # 3. 执行解锁操作
        unlock_data = {
            "current_location": {
                "latitude": 31.2304,
                "longitude": 121.4737
            }
        }

        unlock_response = requests.post(
            f"{base_url}/unlock/{capsule_id}",
            json=unlock_data,
            headers=headers
        )

        assert unlock_response.status_code == 200
        unlock_result = unlock_response.json()
        assert unlock_result["code"] == 200
        assert "data" in unlock_result
        assert "access_token" in unlock_result["data"]
        assert "capsule_id" in unlock_result["data"]
        assert "unlocked_at" in unlock_result["data"]

        print(f"✅ 解锁胶囊成功: {capsule_id}")

        # 4. 使用新token查看胶囊详情
        new_token = unlock_result["data"]["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}

        detail_response = requests.get(f"{base_url}/capsules/{capsule_id}", headers=new_headers)

        assert detail_response.status_code == 200
        detail_result = detail_response.json()
        assert detail_result["code"] == 200
        assert "data" in detail_result

        capsule_detail_after = detail_result["data"]

        # 5. 验证所有关键字段
        print("📋 开始验证胶囊详情字段...")

        # 验证基础信息字段
        assert "id" in capsule_detail_after, "缺少id字段"
        assert "title" in capsule_detail_after, "缺少title字段"
        assert "content" in capsule_detail_after, "缺少content字段"
        assert "visibility" in capsule_detail_after, "缺少visibility字段"
        assert "status" in capsule_detail_after, "缺少status字段"
        assert "created_at" in capsule_detail_after, "缺少created_at字段"

        # 验证字段值正确性
        assert capsule_detail_after["id"] == str(capsule_id) or capsule_detail_after["id"] == capsule_id
        assert capsule_detail_after["title"] == capsule_data["title"]
        assert capsule_detail_after["content"] == capsule_data["content"]
        assert capsule_detail_after["visibility"] == "public"

        # 验证位置信息字段
        assert "location" in capsule_detail_after, "缺少location字段"
        location = capsule_detail_after["location"]
        assert "latitude" in location, "缺少latitude字段"
        assert "longitude" in location, "缺少longitude字段"

        # 使用浮点数精度比较，避免精度问题
        assert abs(location["latitude"] - 31.2304) < 0.001, f"纬度不匹配: {location['latitude']} != 31.2304"
        assert abs(location["longitude"] - 121.4737) < 0.001, f"经度不匹配: {location['longitude']} != 121.4737"

        if "address" in location:
            # 地址可能为空或None，进行适当处理
            expected_address = capsule_data["location"]["address"]
            if expected_address:
                assert location["address"] == expected_address
        print(f"✅ 位置字段验证通过 (lat: {location['latitude']}, lng: {location['longitude']})")

        print("✅ 基础字段验证通过")

        # 6. 验证解锁条件字段
        assert "unlock_conditions" in capsule_detail_after, "缺少unlock_conditions字段"
        unlock_conditions = capsule_detail_after["unlock_conditions"]

        # 验证解锁状态标记
        if isinstance(unlock_conditions, dict):
            assert "is_unlocked" in unlock_conditions, "缺少is_unlocked字段"
            assert unlock_conditions["is_unlocked"] == True, "is_unlocked应该为True"
            assert "type" in unlock_conditions
            assert unlock_conditions["type"] == "public"
        elif hasattr(unlock_conditions, 'is_unlocked'):
            assert unlock_conditions.is_unlocked == True
        print("✅ 解锁状态字段验证通过")

        # 7. 验证创建者信息字段
        assert "creator" in capsule_detail_after, "缺少creator字段"
        creator = capsule_detail_after["creator"]
        assert "user_id" in creator, "creator缺少user_id字段"
        assert "nickname" in creator, "creator缺少nickname字段"
        assert creator["user_id"] is not None
        assert creator["nickname"] is not None

        print("✅ 创建者字段验证通过")

        # 8. 验证统计信息字段
        assert "stats" in capsule_detail_after, "缺少stats字段"
        stats = capsule_detail_after["stats"]
        assert "view_count" in stats, "stats缺少view_count字段"
        assert "like_count" in stats, "stats缺少like_count字段"
        assert "comment_count" in stats, "stats缺少comment_count字段"
        assert "unlock_count" in stats, "stats缺少unlock_count字段"

        # 验证统计值为整数且合理
        assert isinstance(stats["view_count"], int)
        assert isinstance(stats["like_count"], int)
        assert isinstance(stats["comment_count"], int)
        assert isinstance(stats["unlock_count"], int)
        assert stats["unlock_count"] >= 1, "unlock_count应该至少为1"
        assert stats["view_count"] >= 1, "view_count应该至少为1"

        print("✅ 统计字段验证通过")

        # 9. 验证时间戳格式
        created_at = capsule_detail_after["created_at"]
        assert isinstance(created_at, str)
        assert "T" in created_at, "created_at应该是ISO格式"

        print("✅ 时间戳字段验证通过")

        # 10. 验证标签字段（如果存在）
        if "tags" in capsule_detail_after:
            tags = capsule_detail_after["tags"]
            assert isinstance(tags, list)
            # 验证标签内容
            for original_tag in capsule_data["tags"]:
                assert original_tag in tags, f"标签 '{original_tag}' 未找到"

            print("✅ 标签字段验证通过")

        # 11. 对比解锁前后的差异
        print("📋 对比解锁前后的字段变化...")

        # 解锁后的unlock_conditions应该有is_unlocked=True
        if isinstance(capsule_detail_after.get("unlock_conditions"), dict):
            assert capsule_detail_after["unlock_conditions"].get("is_unlocked") == True

        print("✅ 解锁前后对比验证通过")

        # 12. 验证内容完整性
        content_length_diff = len(capsule_detail_after["content"]) - len(capsule_data["content"])
        assert content_length_diff == 0, f"内容长度不一致，差异: {content_length_diff}"

        print("✅ 内容完整性验证通过")

        # 13. 输出最终验证结果
        print(f"\n🎉 完整流程测试成功！")
        print(f"   胶囊ID: {capsule_detail_after['id']}")
        print(f"   标题: {capsule_detail_after['title']}")
        print(f"   解锁状态: {capsule_detail_after.get('unlock_conditions', {}).get('is_unlocked', 'unknown')}")
        print(f"   查看次数: {stats['view_count']}")
        print(f"   解锁次数: {stats['unlock_count']}")
        print(f"   内容长度: {len(capsule_detail_after['content'])} 字符")

    def test_multiple_users_unlock_same_capsule(self, admin_token, user_tokens, created_capsule_ids):
        """测试多个用户解锁同一个胶囊的统计字段更新"""
        print("📋 开始多用户解锁测试...")

        # 检查用户token是否有效
        if not user_tokens or len(user_tokens) < 2:
            pytest.skip("需要至少2个用户进行多用户解锁测试")

        print(f"用户tokens长度: {len(user_tokens)}")
        print(f"用户1: {user_tokens[0].get('email', 'unknown')}")
        print(f"用户2: {user_tokens[1].get('email', 'unknown')}")

        # 创建一个胶囊
        capsule_data = {
            "title": "多用户解锁测试胶囊",
            "content": "这是一个用于测试多用户解锁统计的胶囊",
            "visibility": "public",
            "tags": ["多用户", "统计测试"],
            "location": {
                "latitude": 31.2305,
                "longitude": 121.4738
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0,
                "unlockable_time": (datetime.now() - timedelta(days=1)).isoformat()
            }
        }

        capsule_id = self.create_test_capsule(admin_token, capsule_data, created_capsule_ids)
        print(f"✅ 创建多用户测试胶囊成功: {capsule_id}")

        # 解锁数据
        unlock_data = {
            "current_location": {
                "latitude": 31.2305,
                "longitude": 121.4738
            }
        }

        # 用户1解锁胶囊
        try:
            user1_token = user_tokens[0].get('token')
            if not user1_token:
                pytest.fail("用户1 token为空")

            user1_headers = {"Authorization": f"Bearer {user1_token}"}
            response = requests.post(f"{base_url}/unlock/{capsule_id}", json=unlock_data, headers=user1_headers)
            assert response.status_code == 200
            print("✅ 用户1解锁成功")
        except Exception as e:
            pytest.fail(f"用户1解锁失败: {str(e)}")

        # 用户2解锁胶囊
        try:
            user2_token = user_tokens[1].get('token')
            if not user2_token:
                pytest.fail("用户2 token为空")

            user2_headers = {"Authorization": f"Bearer {user2_token}"}
            response = requests.post(f"{base_url}/unlock/{capsule_id}", json=unlock_data, headers=user2_headers)
            assert response.status_code == 200
            print("✅ 用户2解锁成功")
        except Exception as e:
            pytest.fail(f"用户2解锁失败: {str(e)}")

        # 使用用户2查看胶囊详情，检查统计字段
        try:
            # 验证解锁响应包含token
            unlock_response = response.json()
            assert "data" in unlock_response
            assert "access_token" in unlock_response["data"]

            user2_token = unlock_response["data"]["access_token"]
            user2_detail_headers = {"Authorization": f"Bearer {user2_token}"}

            detail_response = requests.get(f"{base_url}/capsules/{capsule_id}", headers=user2_detail_headers)
            assert detail_response.status_code == 200

            detail_data = detail_response.json()
            assert "data" in detail_data

            capsule_detail = detail_data["data"]

            # 验证stats字段存在
            if "stats" not in capsule_detail:
                pytest.fail("胶囊详情中缺少stats字段")

            stats = capsule_detail["stats"]

            # 验证统计字段存在
            required_stats = ["view_count", "like_count", "comment_count", "unlock_count"]
            for stat_field in required_stats:
                if stat_field not in stats:
                    pytest.fail(f"stats中缺少{stat_field}字段")

            # 验证解锁次数应该为2（两个用户都解锁了）
            unlock_count = stats.get("unlock_count", 0)
            assert unlock_count >= 2, f"解锁次数应该至少为2，实际为: {unlock_count}"

            print(f"✅ 多用户解锁测试通过，解锁次数: {unlock_count}")

        except Exception as e:
            pytest.fail(f"查看胶囊详情失败: {str(e)}")

    def test_unlock_status_persistence(self, admin_token, created_capsule_ids):
        """测试解锁状态持久化"""

        # 创建胶囊
        capsule_data = {
            "title": "解锁状态持久化测试胶囊",
            "content": "测试解锁状态是否正确持久化",
            "visibility": "public",
            "tags": ["持久化", "状态测试"],
            "location": {
                "latitude": 31.2306,
                "longitude": 121.4739
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0,
                "unlockable_time": (datetime.now() - timedelta(days=1)).isoformat()
            }
        }

        capsule_id = self.create_test_capsule(admin_token, capsule_data, created_capsule_ids)

        # 解锁胶囊
        unlock_data = {
            "current_location": {
                "latitude": 31.2306,
                "longitude": 121.4739
            }
        }

        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{base_url}/unlock/{capsule_id}", json=unlock_data, headers=headers)
        assert response.status_code == 200

        # 等待一秒确保数据库更新
        import time
        time.sleep(1)

        # 再次查看胶囊详情
        detail_response = requests.get(f"{base_url}/capsules/{capsule_id}", headers=headers)
        assert detail_response.status_code == 200

        capsule_detail = detail_response.json()["data"]

        # 验证解锁状态持久化
        unlock_conditions = capsule_detail.get("unlock_conditions")
        if isinstance(unlock_conditions, dict):
            assert unlock_conditions.get("is_unlocked") == True
        elif hasattr(unlock_conditions, 'is_unlocked'):
            assert unlock_conditions.is_unlocked == True

        print("✅ 解锁状态持久化测试通过")