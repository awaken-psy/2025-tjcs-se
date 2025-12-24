#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码加密工具
使用与前端相同的简单哈希算法对密码进行加密
用于验证前端加密的密码或在后端进行相同的加密处理
"""


def encrypt_password_sync(password: str) -> str:
    """
    同步版本的密码加密（与前端encryptPasswordSync功能相同）
    注意：这是一个简单的哈希实现，生产环境建议使用更安全的密码哈希算法
    
    Args:
        password: 原始密码字符串
    
    Returns:
        加密后的密码（十六进制字符串）
    """
    hash_value = 0
    for char in password:
        char_code = ord(char)
        hash_value = ((hash_value << 5) - hash_value) + char_code
        hash_value = hash_value & hash_value  # Convert to 32bit integer
    return hex(abs(hash_value))[2:]  # 去掉0x前缀


if __name__ == "__main__":
    # 测试与前端加密结果一致性
    test_passwords = ["password123", "test123", "123456"]
    for pwd in test_passwords:
        encrypted = encrypt_password_sync(pwd)
        print(f"原始密码: {pwd} -> 加密结果: {encrypted}")