import requests
import pytest

from .config import base_url
from .utils import get_admin_user, get_registered_users
from .data import users

def test_get_my_profile():
    """测试获取我的资料接口"""
    # 获取已注册用户
    registered_users = get_registered_users()

    for user in registered_users:
        # 测试获取个人资料
        response = requests.get(
            f"{base_url}/users/me",
            headers={"Authorization": f"Bearer {user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert "user_id" in data["data"]
        assert "email" in data["data"]
        assert "nickname" in data["data"]
        assert data["data"]["email"] == user["email"]

        print(f"✓ 获取用户 {user['email']} 资料成功")


def test_get_my_profile_unauthorized():
    """测试未授权访问获取我的资料接口"""
    # 测试不提供token
    response = requests.get(f"{base_url}/users/me")
    assert response.status_code != 200

    # 测试无效token
    response = requests.get(
        f"{base_url}/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

    print("✓ 未授权访问测试通过")


def test_update_my_profile():
    """测试更新我的资料接口"""
    registered_users = get_registered_users()
    user = registered_users[0]  # 使用第一个用户进行测试

    # 测试更新昵称
    update_data = {
        "nickname": "更新后的昵称"
    }

    response = requests.put(
        f"{base_url}/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {user['token']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

    # 验证更新是否成功
    response = requests.get(
        f"{base_url}/users/me",
        headers={"Authorization": f"Bearer {user['token']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["nickname"] == "更新后的昵称"

    print(f"✓ 更新用户 {user['email']} 资料成功")


def test_update_my_profile_invalid_data():
    """测试更新我的资料接口 - 无效数据"""
    registered_users = get_registered_users()
    user = registered_users[0]

    # 测试空数据
    response = requests.put(
        f"{base_url}/users/me",
        json={},
        headers={"Authorization": f"Bearer {user['token']}"}
    ).json()
    assert response["code"] == 400
    # 测试无效的昵称格式
    update_data = {
        "nickname": ""  # 空昵称
    }

    response = requests.put(
        f"{base_url}/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {user['token']}"}
    )
    assert response.status_code == 422

    print("✓ 无效数据更新测试通过")


# def test_get_my_history():
#     """测试获取我的历史记录接口"""
#     registered_users = get_registered_users()
#     user = registered_users[0]

#     # 测试获取历史记录（注意：此接口可能尚未实现）
#     response = requests.get(
#         f"{base_url}/users/me/history",
#         headers={"Authorization": f"Bearer {user['token']}"}
#     )

#     # 由于接口可能未实现，我们检查状态码
#     if response.status_code == 200:
#         data = response.json()
#         print(f"✓ 获取用户 {user['email']} 历史记录成功")
#     elif response.status_code == 501:
#         print(f"⚠ 用户历史记录接口尚未实现")
#     else:
#         print(f"⚠ 用户历史记录接口返回状态码: {response.status_code}")


# def test_get_user_profile():
#     """测试获取指定用户资料接口"""
#     registered_users = get_registered_users()
#     current_user = registered_users[0]

#     # 尝试获取另一个用户的资料
#     if len(registered_users) > 1:
#         target_user = registered_users[1]

#         response = requests.get(
#             f"{base_url}/users/{target_user['user_id']}",
#             headers={"Authorization": f"Bearer {current_user['token']}"}
#         )

#         # 由于接口可能未实现，我们检查状态码
#         if response.status_code == 200:
#             data = response.json()
#             assert data["code"] == 200
#             assert "data" in data
#             print(f"✓ 获取用户 {target_user['email']} 资料成功")
#         elif response.status_code == 501:
#             print(f"⚠ 获取指定用户资料接口尚未实现")
#         else:
#             print(f"⚠ 获取指定用户资料接口返回状态码: {response.status_code}")

#     # 测试获取不存在的用户
#     response = requests.get(
#         f"{base_url}/users/99999",
#         headers={"Authorization": f"Bearer {current_user['token']}"}
#     )

#     if response.status_code == 404:
#         print("✓ 不存在用户测试通过")
#     elif response.status_code == 501:
#         print("⚠ 获取指定用户资料接口尚未实现")


# def test_get_user_capsules():
#     """测试获取用户胶囊接口"""
#     registered_users = get_registered_users()
#     current_user = registered_users[0]

#     # 尝试获取用户的胶囊
#     if len(registered_users) > 1:
#         target_user = registered_users[1]

#         response = requests.get(
#             f"{base_url}/users/{target_user['user_id']}/capsules",
#             headers={"Authorization": f"Bearer {current_user['token']}"}
#         )

#         # 由于接口可能未实现，我们检查状态码
#         if response.status_code == 200:
#             data = response.json()
#             assert data["code"] == 200
#             assert "data" in data
#             print(f"✓ 获取用户 {target_user['email']} 胶囊成功")
#         elif response.status_code == 501:
#             print(f"⚠ 获取用户胶囊接口尚未实现")
#         else:
#             print(f"⚠ 获取用户胶囊接口返回状态码: {response.status_code}")


# def test_users_endpoints_comprehensive():
#     """综合测试用户相关接口"""
#     print("\n=== 开始用户接口综合测试 ===")

#     # 运行所有测试
#     test_get_my_profile_unauthorized()
#     test_get_my_profile()
#     test_update_my_profile()
#     test_update_my_profile_invalid_data()
#     test_get_my_history()
#     test_get_user_profile()
#     test_get_user_capsules()

#     print("\n=== 用户接口综合测试完成 ===")


# if __name__ == "__main__":
#     # 如果直接运行此文件，执行综合测试
#     test_users_endpoints_comprehensive()