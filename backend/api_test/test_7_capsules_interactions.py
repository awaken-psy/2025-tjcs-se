import pytest
import requests
from datetime import datetime, timedelta

from .config import base_url
from .utils import get_admin_user, get_registered_users


class TestCapsuleInteractions:
    """胶囊互动功能测试（点赞、收藏、评论）"""

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

        # 创建公共互动测试胶囊
        interaction_capsule = {
            "title": "互动测试胶囊",
            "content": "这是一个用于测试点赞、收藏和评论功能的胶囊。",
            "visibility": "public",
            "tags": ["互动", "测试"],
            "location": {
                "latitude": 31.2304,
                "longitude": 121.4737,
                "address": "上海市同济大学"
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0
            }
        }

        response = requests.post(f"{base_url}/v1/capsules/", json=interaction_capsule, headers=headers)
        assert response.status_code == 200
        capsules["interaction"] = response.json()["data"]["capsule_id"]

        # 创建第二个胶囊用于测试不同用户的互动
        second_capsule = {
            "title": "第二个互动胶囊",
            "content": "这是第二个用于测试多用户互动的胶囊。",
            "visibility": "public",
            "tags": ["多用户", "互动"],
            "location": {
                "latitude": 31.2404,
                "longitude": 121.4837,
                "address": "上海市复旦大学"
            },
            "unlock_conditions": {
                "type": "public",
                "radius": 100.0
            }
        }

        response = requests.post(f"{base_url}/v1/capsules/", json=second_capsule, headers=headers)
        assert response.status_code == 200
        capsules["second"] = response.json()["data"]["capsule_id"]

        print(f"✅ 创建互动测试胶囊完成: {capsules}")
        return capsules

    @pytest.fixture(scope="class")
    def created_comment_ids(self):
        """存储测试中创建的评论ID，用于清理"""
        return []

    def test_like_capsule(self, admin_token, test_capsules):
        """测试点赞胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/like", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "点赞成功" in data["message"]

        print(f"✅ 点赞胶囊成功: {capsule_id}")

    def test_like_capsule_already_liked(self, admin_token, test_capsules):
        """测试重复点赞同一个胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        # 第一次点赞
        requests.post(f"{base_url}/v1/interactions/{capsule_id}/like", headers=headers)

        # 第二次点赞同一个胶囊
        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/like", headers=headers)

        # 应该返回成功，但可能提示已经点赞
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        print(f"✅ 重复点赞胶囊测试通过: {capsule_id}")

    def test_unlike_capsule(self, admin_token, test_capsules):
        """测试取消点赞胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        # 先点赞
        requests.post(f"{base_url}/v1/interactions/{capsule_id}/like", headers=headers)

        # 然后取消点赞
        response = requests.delete(f"{base_url}/v1/interactions/{capsule_id}/like", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "取消点赞成功" in data["message"]

        print(f"✅ 取消点赞胶囊成功: {capsule_id}")

    def test_unlike_not_liked_capsule(self, admin_token, test_capsules):
        """测试取消点赞未点赞的胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        # 确保胶囊未被点赞
        requests.delete(f"{base_url}/v1/interactions/{capsule_id}/like", headers=headers)

        # 尝试取消点赞
        response = requests.delete(f"{base_url}/v1/interactions/{capsule_id}/like", headers=headers)

        # 应该返回成功，但可能提示未点赞
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        print(f"✅ 取消点赞未点赞胶囊测试通过: {capsule_id}")

    def test_collect_capsule(self, admin_token, test_capsules):
        """测试收藏胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/collect", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "收藏成功" in data["message"]

        print(f"✅ 收藏胶囊成功: {capsule_id}")

    def test_collect_capsule_already_collected(self, admin_token, test_capsules):
        """测试重复收藏同一个胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        # 第一次收藏
        requests.post(f"{base_url}/v1/interactions/{capsule_id}/collect", headers=headers)

        # 第二次收藏同一个胶囊
        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/collect", headers=headers)

        # 应该返回成功，但可能提示已经收藏
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        print(f"✅ 重复收藏胶囊测试通过: {capsule_id}")

    def test_uncollect_capsule(self, admin_token, test_capsules):
        """测试取消收藏胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        # 先收藏
        requests.post(f"{base_url}/v1/interactions/{capsule_id}/collect", headers=headers)

        # 然后取消收藏
        response = requests.delete(f"{base_url}/v1/interactions/{capsule_id}/collect", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "取消收藏成功" in data["message"]

        print(f"✅ 取消收藏胶囊成功: {capsule_id}")

    def test_uncollect_not_collected_capsule(self, admin_token, test_capsules):
        """测试取消收藏未收藏的胶囊"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        # 确保胶囊未被收藏
        requests.delete(f"{base_url}/v1/interactions/{capsule_id}/collect", headers=headers)

        # 尝试取消收藏
        response = requests.delete(f"{base_url}/v1/interactions/{capsule_id}/collect", headers=headers)

        # 应该返回成功，但可能提示未收藏
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        print(f"✅ 取消收藏未收藏胶囊测试通过: {capsule_id}")

    def test_add_comment(self, admin_token, test_capsules, created_comment_ids):
        """测试添加评论"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        comment_data = {
            "content": "这是一条测试评论，用于验证评论功能是否正常工作。"
        }

        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/comments",
                               json=comment_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "评论添加成功" in data["message"]

        comment_response = data["data"]
        assert "comment_id" in comment_response
        assert "content" in comment_response
        assert "created_at" in comment_response
        assert comment_response["content"] == comment_data["content"]

        # 保存评论ID用于后续测试
        created_comment_ids.append(comment_response["comment_id"])

        print(f"✅ 添加评论成功: {comment_response['comment_id']}")

    def test_add_reply_comment(self, admin_token, test_capsules, created_comment_ids):
        """测试添加回复评论"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        # 先添加一条主评论
        parent_comment_data = {
            "content": "这是一条主评论。"
        }

        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/comments",
                               json=parent_comment_data, headers=headers)
        assert response.status_code == 200
        parent_comment_id = response.json()["data"]["comment_id"]
        created_comment_ids.append(parent_comment_id)

        # 然后添加回复
        reply_data = {
            "content": "这是一条回复评论。",
            "parent_id": parent_comment_id
        }

        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/comments",
                               json=reply_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        comment_response = data["data"]
        assert comment_response["content"] == reply_data["content"]
        created_comment_ids.append(comment_response["comment_id"])

        print(f"✅ 添加回复评论成功: {comment_response['comment_id']}")

    def test_add_comment_validation_errors(self, admin_token, test_capsules):
        """测试添加评论时的验证错误"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        # 测试空内容
        empty_comment_data = {
            "content": ""
        }

        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/comments",
                               json=empty_comment_data, headers=headers)
        assert response.status_code in [400, 422]

        # 测试缺少内容
        no_content_data = {}

        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/comments",
                               json=no_content_data, headers=headers)
        assert response.status_code in [400, 422]

        print("✅ 添加评论验证错误测试通过")

    def test_get_comments(self, admin_token, test_capsules, created_comment_ids):
        """测试获取评论列表"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        # 确保有评论存在
        if not created_comment_ids:
            comment_data = {"content": "测试评论"}
            response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/comments",
                                   json=comment_data, headers=headers)
            if response.status_code == 200:
                created_comment_ids.append(response.json()["data"]["comment_id"])

        response = requests.get(f"{base_url}/v1/interactions/{capsule_id}/comments", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "comments" in data["data"]
        assert "pagination" in data["data"]

        comments = data["data"]["comments"]
        pagination = data["data"]["pagination"]

        assert isinstance(comments, list)
        assert "page" in pagination
        assert "page_size" in pagination
        assert "total" in pagination
        assert "total_pages" in pagination

        # 验证评论结构
        if comments:
            comment = comments[0]
            assert "comment_id" in comment
            assert "content" in comment
            assert "created_at" in comment
            assert "user" in comment
            assert "user_id" in comment

            # 验证用户信息
            user = comment["user"]
            assert "user_id" in user
            assert "nickname" in user

        print(f"✅ 获取评论列表成功，共 {len(comments)} 条评论")

    def test_get_comments_pagination(self, admin_token, test_capsules):
        """测试评论分页"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        # 测试第一页
        params = {"page": 1, "size": 5}
        response = requests.get(f"{base_url}/v1/interactions/{capsule_id}/comments",
                              headers=headers, params=params)
        assert response.status_code == 200

        # 测试第二页
        params["page"] = 2
        response = requests.get(f"{base_url}/v1/interactions/{capsule_id}/comments",
                              headers=headers, params=params)
        assert response.status_code == 200

        print("✅ 评论分页测试通过")

    def test_get_comments_empty_capsule(self, admin_token, test_capsules):
        """测试获取没有评论的胶囊的评论列表"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["second"]  # 使用第二个胶囊，应该没有评论

        response = requests.get(f"{base_url}/v1/interactions/{capsule_id}/comments", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        comments = data["data"]["comments"]
        assert isinstance(comments, list)
        # 可能为空列表或包含一些默认评论

        print(f"✅ 获取空评论列表成功: {len(comments)} 条评论")

    def test_delete_own_comment(self, admin_token, test_capsules, created_comment_ids):
        """测试删除自己的评论"""
        if not created_comment_ids:
            pytest.skip("没有可用的评论ID进行删除测试")

        headers = {"Authorization": f"Bearer {admin_token}"}
        comment_id = created_comment_ids[0]

        response = requests.delete(f"{base_url}/v1/interactions/comments/{comment_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "评论删除成功" in data["message"]

        # 从列表中移除已删除的评论
        created_comment_ids.remove(comment_id)

        print(f"✅ 删除评论成功: {comment_id}")

    def test_delete_nonexistent_comment(self, admin_token):
        """测试删除不存在的评论"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        response = requests.delete(f"{base_url}/v1/interactions/comments/999999", headers=headers)

        # 应该返回404或相应的错误状态码
        assert response.status_code in [404, 400]

        print("✅ 删除不存在评论测试通过")

    def test_interaction_unauthorized(self, test_capsules):
        """测试未授权的互动操作"""
        capsule_id = test_capsules["interaction"]

        # 测试未授权点赞
        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/like")
        assert response.status_code == 401

        # 测试未授权收藏
        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/collect")
        assert response.status_code == 401

        # 测试未授权添加评论
        comment_data = {"content": "未授权评论"}
        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/comments",
                               json=comment_data)
        assert response.status_code == 401

        print("✅ 未授权互动操作测试通过")

    def test_interaction_nonexistent_capsule(self, admin_token):
        """测试对不存在胶囊的互动操作"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试对不存在胶囊的点赞
        response = requests.post(f"{base_url}/v1/interactions/999999/like", headers=headers)
        assert response.status_code in [404, 400]

        # 测试对不存在胶囊的收藏
        response = requests.post(f"{base_url}/v1/interactions/999999/collect", headers=headers)
        assert response.status_code in [404, 400]

        # 测试对不存在胶囊添加评论
        comment_data = {"content": "不存在胶囊的评论"}
        response = requests.post(f"{base_url}/v1/interactions/999999/comments",
                               json=comment_data, headers=headers)
        assert response.status_code in [404, 400]

        # 测试获取不存在胶囊的评论
        response = requests.get(f"{base_url}/v1/interactions/999999/comments", headers=headers)
        assert response.status_code in [404, 400]

        print("✅ 不存在胶囊互动操作测试通过")

    def test_multiple_user_interactions(self, admin_token, user_tokens, test_capsules):
        """测试多用户对同一胶囊的互动"""
        capsule_id = test_capsules["second"]

        # 管理员点赞
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/like", headers=admin_headers)
        assert response.status_code == 200

        # 普通用户点赞
        if user_tokens:
            user_headers = {"Authorization": f"Bearer {user_tokens[0]['token']}"}
            response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/like", headers=user_headers)
            assert response.status_code == 200

            # 普通用户添加评论
            comment_data = {"content": "来自普通用户的评论"}
            response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/comments",
                                   json=comment_data, headers=user_headers)
            assert response.status_code == 200

        print("✅ 多用户互动测试通过")

    def test_comment_content_length_validation(self, admin_token, test_capsules):
        """测试评论内容长度验证"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        capsule_id = test_capsules["interaction"]

        # 测试正常长度评论
        normal_comment = {
            "content": "这是一条正常长度的评论，用于验证正常情况下的评论功能。"
        }

        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/comments",
                               json=normal_comment, headers=headers)
        assert response.status_code == 200

        # 测试极长评论（如果有限制的话）
        long_comment = {
            "content": "这是一条非常长的评论。" * 100  # 重复100次，创建很长的评论
        }

        response = requests.post(f"{base_url}/v1/interactions/{capsule_id}/comments",
                               json=long_comment, headers=headers)
        # 根据后端实现，可能成功或失败
        assert response.status_code in [200, 400, 422]

        print("✅ 评论内容长度验证测试通过")