#!/usr/bin/env python3
"""
调试测试脚本 - 检查API基本功能
"""

import requests
import sys

def test_basic_api():
    """测试基本API连接"""
    base_url = "http://localhost:8000/api"

    print("🔍 调试API连接问题")
    print("=" * 50)

    # 1. 测试基本连接
    try:
        print("\n1. 测试根路径连接...")
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return

    # 2. 测试认证
    print("\n2. 测试管理员登录...")
    try:
        login_data = {
            "email": "admin@admin.com",
            "password": "admin"
        }
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=5)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data["data"]["token"]
            print(f"   ✅ 登录成功，获取token: {token[:20]}...")
            return token
        else:
            print(f"   ❌ 登录失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 登录请求失败: {e}")
        return None

    return None

def test_capsule_creation(token):
    """测试胶囊创建"""
    base_url = "http://localhost:8000/api"

    print("\n3. 测试胶囊创建...")
    headers = {"Authorization": f"Bearer {token}"}

    # 最简单的胶囊数据
    capsule_data = {
        "title": "调试胶囊",
        "content": "这是一个调试胶囊",
        "visibility": "public",
        "location": {
            "latitude": 31.2304,
            "longitude": 121.4737
        },
        "unlock_conditions": {
            "type": "public"
        }
    }

    try:
        response = requests.post(f"{base_url}/capsules/", json=capsule_data, headers=headers, timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 创建成功: {data}")
        else:
            print(f"   ❌ 创建失败")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")

def main():
    """主函数"""
    print("时光胶囊·校园 - API调试工具")
    print("=" * 50)

    # 测试基本连接
    token = test_basic_api()

    if token:
        # 测试胶囊创建
        test_capsule_creation(token)
    else:
        print("\n❌ 无法获取认证token，跳过胶囊测试")

if __name__ == "__main__":
    main()