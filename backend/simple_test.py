#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的API测试工具
使用内存数据库和模拟数据，不写任何文件到磁盘
测试所有capsule相关API，确保前后端能正常对接

使用方法:
1. 启动后端服务: uvicorn app.main:app --reload --port 8000
2. 运行此测试: python simple_test.py
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import Dict, Any

# 模拟测试数据
TEST_DATA = {
    "capsule_create": {
        "title": "测试胶囊-毕业纪念",
        "content": "这是我们的毕业纪念胶囊，记录了美好的大学时光。大家一起拍了照片，留下了珍贵的回忆。",
        "visibility": "public",
        "tags": ["毕业", "纪念", "校园", "青春"],
        "location": "上海市同济大学",
        "lat": 31.2834,
        "lng": 121.5057,
        "createTime": datetime.utcnow().isoformat() + "Z",
        "updateTime": datetime.utcnow().isoformat() + "Z"
    },
    "capsule_create_new": {
        "title": "新版API测试胶囊",
        "content": "这是使用新版API创建的测试胶囊，支持嵌套的location对象。",
        "visibility": "public",
        "tags": ["新版API", "测试", "验证"],
        "location": {
            "latitude": 31.2304,
            "longitude": 121.4737,
            "address": "上海市人民广场"
        }
    },
    "capsule_update": {
        "title": "更新后的胶囊标题",
        "content": "这是更新后的胶囊内容",
        "visibility": "private",
        "tags": ["更新", "修改"]
    },
    "unlock_check": {
        "user_location": {
            "latitude": 31.1434,
            "longitude": 121.6580,
            "address": "上海迪士尼乐园"
        },
        "max_distance_meters": 1000,
        "current_time": datetime.utcnow().isoformat() + "Z"
    },
    "unlock_capsule": {
        "capsule_id": "1",
        "user_location": {
            "latitude": 31.1434,
            "longitude": 121.6580
        },
        "current_time": datetime.utcnow().isoformat() + "Z"
    }
}


class SimpleAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"

        # 添加查询参数
        if params:
            query_string = urllib.parse.urlencode(params)
            url += f"?{query_string}"

        try:
            req = urllib.request.Request(url)
            req.add_header('Content-Type', 'application/json')

            if method.upper() in ['POST', 'PUT', 'DELETE']:
                req.get_method = lambda: method.upper()
                if data:
                    req.data = json.dumps(data).encode('utf-8')

            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                content = response.read().decode('utf-8')

                try:
                    response_data = json.loads(content) if content else {}
                except:
                    response_data = content

                return status_code, response_data

        except urllib.error.HTTPError as e:
            try:
                error_content = e.read().decode('utf-8')
                error_data = json.loads(error_content) if error_content else error_content
            except:
                error_data = str(e)
            return e.code, error_data
        except Exception as e:
            return 0, str(e)

    def log_test(self, test_name: str, endpoint: str, method: str, status_code: int,
                 success: bool, response_data: Any = None, error_msg: str = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "success": success,
            "timestamp": datetime.now().strftime('%H:%M:%S')
        }

        print(f"{'='*60}")
        print(f"🧪 {test_name}")
        print(f"📍 接口: {method} {endpoint}")
        print(f"📊 状态码: {status_code}")

        if success:
            print("✅ 测试结果: 成功")
        else:
            print("❌ 测试结果: 失败")

        print("\n📋 完整响应数据:")
        if isinstance(response_data, (dict, list)):
            print(json.dumps(response_data, ensure_ascii=False, indent=2))
        else:
            print(str(response_data))

        if error_msg and not isinstance(response_data, (dict, list)):
            print(f"\n🚨 错误详情: {error_msg}")

        print("\n" + "-"*60)
        print()
        self.test_results.append(result)

    def test_create_capsule_legacy(self):
        """测试创建胶囊(旧版API)"""
        status_code, data = self.make_request(
            "POST",
            "/api/v1/capsule/create",
            data=TEST_DATA["capsule_create"]
        )

        success = status_code == 200 and isinstance(data, dict) and data.get('success')
        self.log_test(
            "创建胶囊(旧版API)",
            "/api/v1/capsule/create",
            "POST",
            status_code,
            success,
            data if success else None,
            None if success else str(data)
        )

    def test_create_capsule_new(self):
        """测试创建胶囊(新版API)"""
        status_code, data = self.make_request(
            "POST",
            "/api/v1/capsule/",
            data=TEST_DATA["capsule_create_new"]
        )

        success = status_code == 200 and isinstance(data, dict) and data.get('success')
        self.log_test(
            "创建胶囊(新版API)",
            "/api/v1/capsule/",
            "POST",
            status_code,
            success,
            data if success else None,
            None if success else str(data)
        )

    def test_get_capsules(self):
        """测试获取胶囊列表"""
        status_code, data = self.make_request(
            "GET",
            "/api/v1/capsule/",
            params={"page": 1, "limit": 10}
        )

        success = status_code == 200 and isinstance(data, dict)
        self.log_test(
            "获取胶囊列表",
            "/api/v1/capsule/",
            "GET",
            status_code,
            success,
            data if success else None,
            None if success else str(data)
        )

    def test_get_my_capsules(self):
        """测试获取我的胶囊"""
        status_code, data = self.make_request(
            "GET",
            "/api/v1/capsule/my",
            params={"page": 1, "limit": 10}
        )

        success = status_code == 200
        self.log_test(
            "获取我的胶囊",
            "/api/v1/capsule/my",
            "GET",
            status_code,
            success,
            data if success else None,
            None if success else str(data)
        )

    def test_get_capsule_detail(self, capsule_id="caps_1"):
        """测试获取胶囊详情"""
        status_code, data = self.make_request(
            "GET",
            f"/api/v1/capsule/{capsule_id}"
        )

        success = status_code == 200 and isinstance(data, dict) and 'capsule' in data
        self.log_test(
            "获取胶囊详情",
            f"/api/v1/capsule/{capsule_id}",
            "GET",
            status_code,
            success,
            data if success else None,
            None if success else str(data)
        )

    def test_update_capsule(self, capsule_id="caps_114514"):
        """测试更新胶囊"""
        status_code, data = self.make_request(
            "PUT",
            f"/api/v1/capsule/{capsule_id}",
            data=TEST_DATA["capsule_update"]
        )

        success = status_code == 200 and isinstance(data, dict) and data.get('success')
        self.log_test(
            "更新胶囊",
            f"/api/v1/capsule/{capsule_id}",
            "PUT",
            status_code,
            success,
            data if success else None,
            None if success else str(data)
        )

    def test_delete_capsule(self, capsule_id="caps_114514"):
        """测试删除胶囊"""
        status_code, data = self.make_request(
            "DELETE",
            f"/api/v1/capsule/{capsule_id}"
        )

        success = status_code == 200 and isinstance(data, dict) and data.get('success')
        self.log_test(
            "删除胶囊",
            f"/api/v1/capsule/{capsule_id}",
            "DELETE",
            status_code,
            success,
            data if success else None,
            None if success else str(data)
        )

    def test_upload_image(self):
        """测试上传图片"""
        # 模拟文件上传数据
        upload_data = {
            "filename": "test_image.jpg",
            "file_size": 1024,
            "file_type": "image/jpeg"
        }

        status_code, data = self.make_request(
            "POST",
            "/api/v1/capsule/upload-img",
            data=upload_data
        )

        # 这个接口预期可能会失败，因为它需要真实的文件上传
        success = status_code == 200
        self.log_test(
            "上传图片",
            "/api/v1/capsule/upload-img",
            "POST",
            status_code,
            success,
            data if success else None,
            None if success else str(data)
        )

    def test_unlock_check(self):
        """测试检查可解锁胶囊 - 已暂时禁用"""
        print("=" * 60)
        print("⏸️ 检查可解锁胶囊")
        print("📍 接口: POST /api/v1/unlock/check")
        print("⚠️ 状态: 功能暂时禁用，等待其他团队成员实现")
        print("-" * 60)
        print()

    def test_unlock_capsule(self):
        """测试解锁胶囊 - 已暂时禁用"""
        print("=" * 60)
        print("⏸️ 解锁胶囊")
        print("📍 接口: POST /api/v1/unlock/capsule")
        print("⚠️ 状态: 功能暂时禁用，等待其他团队成员实现")
        print("-" * 60)
        print()

    def check_server_status(self):
        """检查服务器状态"""
        print("🔍 检查后端服务状态...")
        try:
            status_code, data = self.make_request("GET", "/docs")
            if status_code == 200:
                print("✅ 后端服务正常运行")
                return True
            else:
                print(f"❌ 后端服务响应异常: {status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接后端服务: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 TimeCapsule API 简单测试工具")
        print("=" * 50)
        print("📋 测试说明:")
        print("• 使用内存数据库，不写任何文件")
        print("• 测试所有capsule相关API接口")
        print("• 验证前后端数据格式对接")
        print("=" * 50)

        # 检查服务器状态
        if not self.check_server_status():
            print("\n❌ 请先启动后端服务:")
            print("   uvicorn app.main:app --reload --port 8000")
            return

        print(f"\n🚀 开始测试 - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)

        # 运行所有测试
        tests = [
            self.test_create_capsule_legacy,
            self.test_create_capsule_new,
            self.test_get_capsules,
            self.test_get_my_capsules,
            self.test_get_capsule_detail,
            self.test_update_capsule,
            self.test_delete_capsule,
            self.test_upload_image,
            self.test_unlock_check,
            self.test_unlock_capsule
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ 测试异常: {test.__name__} - {e}")

        # 输出测试结果汇总
        self.print_summary()

    def print_summary(self):
        """打印测试结果汇总"""
        print("=" * 80)
        print("📊 测试结果汇总")
        print("=" * 80)

        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - successful_tests

        print(f"✅ 成功: {successful_tests}/{total_tests} ({(successful_tests/total_tests)*100:.1f}%)")
        print(f"❌ 失败: {failed_tests}/{total_tests} ({(failed_tests/total_tests)*100:.1f}%)")

        if failed_tests > 0:
            print(f"\n🚨 失败的测试详情:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   ❌ {result['test_name']}")
                    print(f"      接口: {result['method']} {result['endpoint']}")
                    print(f"      状态码: {result['status_code']}")
                    print(f"      时间: {result['timestamp']}")

        print(f"\n💡 前后端对接分析:")
        if successful_tests == total_tests:
            print("   🎉 所有API测试通过！前后端对接完全正常。")
            print("   ✅ 数据格式匹配，可以开始前端开发。")
        elif successful_tests >= total_tests * 0.7:
            print("   ✅ 大部分API正常，基本可以对接。")
            print("   🔧 失败的接口可能需要数据库初始化或服务修复。")
        elif successful_tests >= total_tests * 0.3:
            print("   ⚠️  部分API正常，需要修复失败的接口。")
            print("   🔍 建议检查: 认证逻辑、数据库连接、服务类实现。")
        else:
            print("   ❌ 多数API有问题，需要全面检查后端。")
            print("   🔍 建议: 依赖安装、数据库初始化、服务重启。")

        print("=" * 80)


def main():
    """主函数"""
    tester = SimpleAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()