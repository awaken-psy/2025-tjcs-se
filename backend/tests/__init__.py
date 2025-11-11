"""
测试模块
"""
import os
import sys

cur_file_path = os.path.abspath(__file__)
test_dir_path = os.path.dirname(cur_file_path)
backend_dir_path = os.path.dirname(test_dir_path)
app_dir_path = os.path.join(backend_dir_path, "app")
if backend_dir_path not in sys.path:
    sys.path.append(backend_dir_path)
if app_dir_path not in sys.path:
    sys.path.append(app_dir_path)