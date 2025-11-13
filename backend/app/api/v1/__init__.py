from fastapi import APIRouter
from pathlib import Path
import importlib

from .routes import *

# 导入当前目录下所有一级子目录下的python文件
package_dir = Path(__file__).parent
for dir in package_dir.iterdir():
    if not dir.is_dir():
        continue
    dir_name = dir.name
    for file in dir.iterdir():
        if file.suffix == '.py' and file.name != '__init__.py':
            module_name = file.stem
            try:
                importlib.import_module(f'.{module_name}', package=__name__+'.'+dir_name)
                print(f"imported module {module_name}")
            except ImportError as e:
                print(f"warning: failed to import module {module_name}: {e}")

