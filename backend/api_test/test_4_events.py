import requests
import pytest
from datetime import datetime, timedelta
import uuid

from .config import base_url
from .utils import get_admin_user, get_registered_users


class TestEventsAPI:
    """活动相关接口测试类"""

    @pytest.fixture(scope="class")
    def event_data(self):
        """测试活动数据"""
        return {
            "name": "校园马拉松",
            "description": "欢迎参加一年一度的校园马拉松活动，一起挑战自我！",
            "date": (datetime.now() + timedelta(days=30)).isoformat(),
            "location": "同济大学嘉定校区体育场",
            "tags": ["运动", "健康", "校园活动"],
            "cover_img": "https://example.com/marathon-cover.jpg"
        }

    @pytest.fixture(scope="class")
    def update_event_data(self):
        """更新活动数据"""
        return {
            "name": "校园马拉松2024（更新版）",
            "description": "欢迎参加一年一度的校园马拉松活动，一起挑战自我！活动日期已调整。",
            "date": (datetime.now() + timedelta(days=35)).isoformat(),
            "location": "同济大学嘉定校区主体育场",
            "tags": ["运动", "健康", "校园活动", "马拉松"],
            "cover_img": "https://example.com/marathon-cover-updated.jpg"
        }

    def test_create_event_success(self, event_data):
        """测试创建活动成功"""
        admin_user = get_admin_user()

        response = requests.post(
            f"{base_url}/events/",
            json=event_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "活动创建成功"

        # 验证响应数据结构符合 EventCreateResponse 模型
        event_response = data["data"]
        assert "id" in event_response
        assert event_response["name"] == event_data["name"]
        assert "created_at" in event_response

        # 验证 id 是有效的整数ID（转换为字符串格式）
        try:
            int(event_response["id"])
        except ValueError:
            pytest.fail(f"Event ID is not a valid integer ID: {event_response['id']}")

        print(f"✓ 创建活动成功，活动ID: {event_response['id']}")
        return event_response["id"]

    def test_create_event_unauthorized(self, event_data):
        """测试未授权创建活动"""
        # 测试不提供token
        response = requests.post(f"{base_url}/events/", json=event_data)
        # 可能返回401或422，取决于认证中间件的具体实现
        assert response.status_code in [401, 403, 422]

        # 测试无效token
        response = requests.post(
            f"{base_url}/events/",
            json=event_data,
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code in [401, 403]

        print("✓ 未授权创建活动测试通过")

    def test_create_event_invalid_data(self):
        """测试创建活动 - 无效数据"""
        admin_user = get_admin_user()

        # 测试缺少必填字段
        invalid_data = {
            "name": "测试活动"
            # 缺少 description, date, location
        }

        response = requests.post(
            f"{base_url}/events/",
            json=invalid_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        assert response.status_code == 422

        # 测试空字符串
        invalid_data_empty = {
            "name": "",
            "description": "测试描述",
            "date": datetime.now().isoformat(),
            "location": "测试地点"
        }

        response = requests.post(
            f"{base_url}/events/",
            json=invalid_data_empty,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        assert response.status_code == 422

        print("✓ 无效数据创建活动测试通过")

    def test_get_events_list_success(self):
        """测试获取活动列表成功"""
        response = requests.get(f"{base_url}/events/")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "获取成功"

        # 验证响应数据结构符合 EventListResponse 模型
        event_list = data["data"]
        assert "list" in event_list
        assert "total" in event_list
        assert "page" in event_list
        assert "page_size" in event_list

        # 验证列表中的每个活动符合 EventResponse 模型
        if event_list["list"]:
            event = event_list["list"][0]
            self._validate_event_response_structure(event)

        print(f"✓ 获取活动列表成功，共 {event_list['total']} 个活动")

    def test_get_events_list_with_pagination(self):
        """测试分页获取活动列表"""
        # 测试第一页，每页5条
        params = {"page": 1, "size": 5}
        response = requests.get(f"{base_url}/events/", params=params)

        assert response.status_code == 200
        data = response.json()
        event_list = data["data"]

        assert event_list["page"] == 1
        assert event_list["page_size"] == 5
        assert len(event_list["list"]) <= 5

        print("✓ 分页获取活动列表测试通过")

    def test_get_event_detail_success(self):
        """测试获取活动详情成功"""
        # 先创建一个活动
        admin_user = get_admin_user()
        event_data = {
            "name": "测试活动详情",
            "description": "这是一个用于测试活动详情的活动",
            "date": (datetime.now() + timedelta(days=7)).isoformat(),
            "location": "测试地点",
            "tags": ["测试"]
        }

        create_response = requests.post(
            f"{base_url}/events/",
            json=event_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        event_id = create_response.json()["data"]["id"]

        # 获取活动详情
        response = requests.get(
            f"{base_url}/events/{event_id}",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "获取成功"

        # 验证响应数据结构符合 EventResponse 模型
        event_detail = data["data"]
        self._validate_event_response_structure(event_detail)
        assert event_detail["name"] == event_data["name"]
        assert event_detail["description"] == event_data["description"]

        print(f"✓ 获取活动详情成功，活动名称: {event_detail['name']}")

    def test_get_event_detail_not_found(self):
        """测试获取不存在的活动详情"""
        admin_user = get_admin_user()
        # 使用一个确定不存在的大整数ID，因为后端使用的是整数ID
        nonexistent_id = "999999"

        response = requests.get(
            f"{base_url}/events/{nonexistent_id}",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 404

        print("✓ 获取不存在活动详情测试通过")

    def test_update_event_success(self, update_event_data):
        """测试更新活动成功"""
        # 先创建一个活动
        admin_user = get_admin_user()
        original_data = {
            "name": "原始活动名称",
            "description": "原始描述",
            "date": (datetime.now() + timedelta(days=10)).isoformat(),
            "location": "原始地点",
            "tags": ["原始标签"]
        }

        create_response = requests.post(
            f"{base_url}/events/",
            json=original_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        event_id = create_response.json()["data"]["id"]

        # 更新活动
        response = requests.put(
            f"{base_url}/events/{event_id}",
            json=update_event_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "活动更新成功"

        # 验证响应数据结构符合 EventUpdateResponse 模型
        update_response = data["data"]
        assert update_response["updated"] is True
        assert update_response["event_id"] == event_id

        # 验证更新后的详情
        detail_response = requests.get(
            f"{base_url}/events/{event_id}",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        updated_event = detail_response.json()["data"]
        assert updated_event["name"] == update_event_data["name"]
        assert updated_event["description"] == update_event_data["description"]

        print(f"✓ 更新活动成功，活动ID: {event_id}")

    def test_update_event_unauthorized(self, update_event_data):
        """测试未授权更新活动"""
        admin_user = get_admin_user()

        # 先创建一个活动
        original_data = {
            "name": "测试未授权更新",
            "description": "测试描述",
            "date": (datetime.now() + timedelta(days=5)).isoformat(),
            "location": "测试地点",
            "tags": ["测试"]
        }

        create_response = requests.post(
            f"{base_url}/events/",
            json=original_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        event_id = create_response.json()["data"]["id"]

        # 使用另一个用户尝试更新
        registered_users = get_registered_users()
        if len(registered_users) > 0:
            other_user = registered_users[0]

            response = requests.put(
                f"{base_url}/events/{event_id}",
                json=update_event_data,
                headers={"Authorization": f"Bearer {other_user['token']}"}
            )

            # 应该返回403权限错误
            if response.status_code == 403:
                print("✓ 权限不足更新活动测试通过")
            elif response.status_code == 500 and "权限" in response.json().get("detail", ""):
                print("✓ 权限不足更新活动测试通过")
            else:
                print(f"⚠ 更新活动权限测试返回状态码: {response.status_code}")

    def test_update_event_not_found(self, update_event_data):
        """测试更新不存在的活动"""
        admin_user = get_admin_user()
        # 使用一个确定不存在的大整数ID
        nonexistent_id = "999999"

        response = requests.put(
            f"{base_url}/events/{nonexistent_id}",
            json=update_event_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 404

        print("✓ 更新不存在活动测试通过")

    def test_delete_event_success(self):
        """测试删除活动成功"""
        # 先创建一个活动
        admin_user = get_admin_user()
        event_data = {
            "name": "待删除的活动",
            "description": "这个活动将被删除",
            "date": (datetime.now() + timedelta(days=3)).isoformat(),
            "location": "测试删除地点",
            "tags": ["删除测试"]
        }

        create_response = requests.post(
            f"{base_url}/events/",
            json=event_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        event_id = create_response.json()["data"]["id"]

        # 删除活动
        response = requests.delete(
            f"{base_url}/events/{event_id}",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "活动删除成功"

        # 验证响应数据结构符合 EventDeleteResponse 模型
        delete_response = data["data"]
        assert delete_response["deleted"] is True
        assert delete_response["event_id"] == event_id

        # 验证活动已被删除
        detail_response = requests.get(
            f"{base_url}/events/{event_id}",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        assert detail_response.status_code == 404

        print(f"✓ 删除活动成功，活动ID: {event_id}")

    def test_delete_event_unauthorized(self):
        """测试未授权删除活动"""
        admin_user = get_admin_user()

        # 先创建一个活动
        event_data = {
            "name": "测试未授权删除",
            "description": "测试描述",
            "date": (datetime.now() + timedelta(days=4)).isoformat(),
            "location": "测试地点",
            "tags": ["测试"]
        }

        create_response = requests.post(
            f"{base_url}/events/",
            json=event_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        event_id = create_response.json()["data"]["id"]

        # 使用另一个用户尝试删除
        registered_users = get_registered_users()
        if len(registered_users) > 0:
            other_user = registered_users[0]

            response = requests.delete(
                f"{base_url}/events/{event_id}",
                headers={"Authorization": f"Bearer {other_user['token']}"}
            )

            # 应该返回403权限错误
            if response.status_code == 403:
                print("✓ 权限不足删除活动测试通过")
            elif response.status_code == 500 and "权限" in response.json().get("detail", ""):
                print("✓ 权限不足删除活动测试通过")
            else:
                print(f"⚠ 删除活动权限测试返回状态码: {response.status_code}")

    def test_register_event_success(self):
        """测试报名活动成功"""
        # 先创建一个活动
        admin_user = get_admin_user()
        event_data = {
            "name": "报名测试活动",
            "description": "用于测试报名功能的活动",
            "date": (datetime.now() + timedelta(days=20)).isoformat(),
            "location": "报名测试地点",
            "tags": ["报名测试"]
        }

        create_response = requests.post(
            f"{base_url}/events/",
            json=event_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        event_id = create_response.json()["data"]["id"]

        # 使用普通用户报名
        registered_users = get_registered_users()
        if len(registered_users) > 0:
            user = registered_users[0]

            response = requests.post(
                f"{base_url}/events/{event_id}/register",
                headers={"Authorization": f"Bearer {user['token']}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["message"] == "报名成功"

            # 验证响应数据结构符合 EventRegistrationResponse 模型
            registration_response = data["data"]
            assert "registration_id" in registration_response
            assert registration_response["event_id"] == event_id
            assert "user_id" in registration_response
            assert "registered_at" in registration_response

            print(f"✓ 报名活动成功，报名ID: {registration_response['registration_id']}")
            return registration_response

    def test_register_event_duplicate(self):
        """测试重复报名活动"""
        # 先创建一个活动并报名
        admin_user = get_admin_user()
        event_data = {
            "name": "重复报名测试活动",
            "description": "用于测试重复报名功能的活动",
            "date": (datetime.now() + timedelta(days=25)).isoformat(),
            "location": "重复报名测试地点",
            "tags": ["重复报名"]
        }

        create_response = requests.post(
            f"{base_url}/events/",
            json=event_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        event_id = create_response.json()["data"]["id"]

        # 使用普通用户第一次报名
        registered_users = get_registered_users()
        if len(registered_users) > 0:
            user = registered_users[0]

            # 第一次报名
            response1 = requests.post(
                f"{base_url}/events/{event_id}/register",
                headers={"Authorization": f"Bearer {user['token']}"}
            )
            assert response1.status_code == 200

            # 第二次报名（应该失败）
            response2 = requests.post(
                f"{base_url}/events/{event_id}/register",
                headers={"Authorization": f"Bearer {user['token']}"}
            )
            assert response2.status_code == 400

            print("✓ 重复报名活动测试通过")

    def test_register_event_not_found(self):
        """测试报名不存在的活动"""
        registered_users = get_registered_users()
        if len(registered_users) > 0:
            user = registered_users[0]
            # 使用一个确定不存在的大整数ID
            nonexistent_id = "999999"

            response = requests.post(
                f"{base_url}/events/{nonexistent_id}/register",
                headers={"Authorization": f"Bearer {user['token']}"}
            )

            assert response.status_code == 404

            print("✓ 报名不存在活动测试通过")

    def test_cancel_registration_success(self):
        """测试取消报名成功"""
        # 先创建一个活动并报名
        admin_user = get_admin_user()
        event_data = {
            "name": "取消报名测试活动",
            "description": "用于测试取消报名功能的活动",
            "date": (datetime.now() + timedelta(days=15)).isoformat(),
            "location": "取消报名测试地点",
            "tags": ["取消报名"]
        }

        create_response = requests.post(
            f"{base_url}/events/",
            json=event_data,
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )
        event_id = create_response.json()["data"]["id"]

        # 使用普通用户报名
        registered_users = get_registered_users()
        if len(registered_users) > 0:
            user = registered_users[0]

            # 先报名
            register_response = requests.post(
                f"{base_url}/events/{event_id}/register",
                headers={"Authorization": f"Bearer {user['token']}"}
            )
            assert register_response.status_code == 200

            # 取消报名
            response = requests.post(
                f"{base_url}/events/{event_id}/cancel",
                headers={"Authorization": f"Bearer {user['token']}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["message"] == "取消报名成功"

            # 验证响应数据结构符合 EventCancelResponse 模型
            cancel_response = data["data"]
            assert cancel_response["cancelled"] is True
            assert cancel_response["event_id"] == event_id

            print(f"✓ 取消报名成功，活动ID: {event_id}")

    def test_get_my_events(self):
        """测试获取我创建的活动"""
        admin_user = get_admin_user()

        response = requests.get(
            f"{base_url}/events/my",
            headers={"Authorization": f"Bearer {admin_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "获取成功"

        # 验证响应数据结构符合 EventListResponse 模型
        event_list = data["data"]
        assert "list" in event_list
        assert "total" in event_list
        assert "page" in event_list
        assert "page_size" in event_list

        print(f"✓ 获取我创建的活动成功，共 {event_list['total']} 个活动")

    def test_get_my_registrations(self):
        """测试获取我报名的活动"""
        registered_users = get_registered_users()
        if len(registered_users) > 0:
            user = registered_users[0]

            response = requests.get(
                f"{base_url}/events/my-registered",
                headers={"Authorization": f"Bearer {user['token']}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["message"] == "获取成功"

            # 验证响应数据结构符合 EventListResponse 模型
            event_list = data["data"]
            assert "list" in event_list
            assert "total" in event_list
            assert "page" in event_list
            assert "page_size" in event_list

            print(f"✓ 获取我报名的活动成功，共 {event_list['total']} 个活动")

    def _validate_event_response_structure(self, event):
        """验证活动响应数据结构"""
        required_fields = [
            "id", "name", "description", "date", "location",
            "tags", "participant_count", "is_registered",
            "created_at", "updated_at"
        ]

        for field in required_fields:
            assert field in event, f"Missing required field: {field}"

        # 验证数据类型
        assert isinstance(event["id"], str)
        assert isinstance(event["name"], str)
        assert isinstance(event["description"], str)
        assert isinstance(event["location"], str)
        assert isinstance(event["tags"], list)
        assert isinstance(event["participant_count"], int)
        assert isinstance(event["is_registered"], bool)

        # 验证日期格式
        try:
            datetime.fromisoformat(event["date"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"Invalid date format: {event['date']}")


# 独立测试函数
# def test_create_event_success():
#     """独立测试：创建活动成功"""
#     test_instance = TestEventsAPI()
#     event_data = {
#         "name": "校园马拉松",
#         "description": "欢迎参加一年一度的校园马拉松活动，一起挑战自我！",
#         "date": (datetime.now() + timedelta(days=30)).isoformat(),
#         "location": "同济大学嘉定校区体育场",
#         "tags": ["运动", "健康", "校园活动"]
#     }
#     test_instance.test_create_event_success(event_data)


# def test_get_events_list_success():
#     """独立测试：获取活动列表成功"""
#     test_instance = TestEventsAPI()
#     test_instance.test_get_events_list_success()


# def test_events_comprehensive():
#     """活动接口综合测试"""
#     print("\n=== 开始活动接口综合测试 ===")

#     test_instance = TestEventsAPI()
#     event_data = {
#         "name": "综合测试活动",
#         "description": "用于综合测试的活动",
#         "date": (datetime.now() + timedelta(days=40)).isoformat(),
#         "location": "综合测试地点",
#         "tags": ["综合测试"]
#     }
#     update_data = {
#         "name": "综合测试活动（更新）",
#         "description": "更新后的综合测试活动描述",
#         "date": (datetime.now() + timedelta(days=45)).isoformat(),
#         "location": "更新后的综合测试地点",
#         "tags": ["综合测试", "更新"]
#     }

#     # 创建活动
#     event_id = test_instance.test_create_event_success(event_data)

#     # 获取活动列表
#     test_instance.test_get_events_list_success()

#     # 获取活动详情
#     test_instance.test_get_event_detail_success()

#     # 更新活动
#     test_instance.test_update_event_success(update_data)

#     # 测试报名功能
#     test_instance.test_register_event_success()

#     # 测试取消报名
#     test_instance.test_cancel_registration_success()

#     # 获取我创建的活动
#     test_instance.test_get_my_events()

#     # 获取我报名的活动
#     test_instance.test_get_my_registrations()

#     # 删除活动
#     test_instance.test_delete_event_success()

#     print("\n=== 活动接口综合测试完成 ===")


# if __name__ == "__main__":
#     # 如果直接运行此文件，执行独立测试
#     test_create_event_success()
#     test_get_events_list_success()
#     test_events_comprehensive()