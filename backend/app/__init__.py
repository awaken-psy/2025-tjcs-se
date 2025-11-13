import os
import sys

current_path = os.path.abspath(__file__)
app_dir = os.path.dirname(current_path)
backend_dir = os.path.dirname(app_dir)
if app_dir not in sys.path:
    sys.path.append(app_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)