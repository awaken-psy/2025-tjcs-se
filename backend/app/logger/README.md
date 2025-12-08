# 时光胶囊日志系统

这是一个为时光胶囊·校园项目设计的简易日志系统，支持文件和终端输出，具有灵活的配置选项。

## 功能特性

- ✅ **多级别日志**: 支持 DEBUG、INFO、WARNING、ERROR、CRITICAL 五个级别
- ✅ **多输出方式**: 支持终端彩色输出和文件输出
- ✅ **日志轮转**: 支持按文件大小自动轮转，避免日志文件过大
- ✅ **灵活配置**: 支持环境变量和代码配置两种方式
- ✅ **格式化**: 支持简单、详细、JSON 三种日志格式
- ✅ **类集成**: 提供 LoggerMixin 类，方便在其他类中使用
- ✅ **预定义记录器**: 提供常用模块的预定义日志记录器

## 快速开始

### 基本使用

```python
from app.logger import app_logger, log_info, log_error

# 使用预定义的日志记录器
app_logger.info("应用程序启动")
app_logger.error("发生错误")

# 使用快捷函数
log_info("这是一条信息")
log_error("这是一条错误")
```

### 自定义配置

```python
from app.logger import configure_logging, LogLevel, LogFormat, get_logger

# 配置日志系统
configure_logging(
    level=LogLevel.DEBUG,
    log_file="custom.log",
    enable_console=True,
    enable_file=True,
    format_type=LogFormat.DETAILED
)

# 获取自定义日志记录器
logger = get_logger("my_module")
logger.debug("调试信息")
```

### 在类中使用

```python
from app.logger import LoggerMixin

class MyService(LoggerMixin):
    def process_data(self, data):
        self.logger.info(f"开始处理数据: {data}")
        # 处理逻辑
        self.logger.debug("数据处理完成")
```

## 环境变量配置

可以通过以下环境变量配置日志系统：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `LOG_LEVEL` | INFO | 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `LOG_DIR` | logs | 日志文件目录 |
| `LOG_FILE` | app.log | 日志文件名 |
| `ENABLE_CONSOLE` | true | 是否启用终端输出 (true/false) |
| `ENABLE_FILE` | true | 是否启用文件输出 (true/false) |
| `LOG_FORMAT` | detailed | 日志格式 (simple/detailed/json) |

### 环境变量示例

```bash
# .env 文件
LOG_LEVEL=DEBUG
LOG_DIR=./logs
LOG_FILE=timecapsule.log
ENABLE_CONSOLE=true
ENABLE_FILE=true
LOG_FORMAT=detailed
```

## API 参考

### 配置函数

#### `configure_logging(...)`

配置日志系统的主要函数。

```python
def configure_logging(
    level: LogLevel = LogLevel.INFO,
    log_file: str = "app.log",
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_colors: bool = True,
    format_type: LogFormat = LogFormat.DETAILED,
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> None
```

### 日志记录器获取

#### `get_logger(name: str = None) -> logging.Logger`

获取指定名称的日志记录器。

```python
logger = get_logger("my_module")
logger.info("信息")
```

### 快捷函数

- `log_debug(message: str, name: str = None)`
- `log_info(message: str, name: str = None)`
- `log_warning(message: str, name: str = None)`
- `log_error(message: str, name: str = None, exception: Exception = None)`
- `log_critical(message: str, name: str = None, exception: Exception = None)`

### 预定义日志记录器

- `app_logger`: 应用程序主日志记录器
- `api_logger`: API 相关日志记录器
- `db_logger`: 数据库操作日志记录器
- `auth_logger`: 认证相关日志记录器

## 日志格式

### 简单格式 (simple)
```
INFO - 这是一条信息
ERROR - 这是一条错误
```

### 详细格式 (detailed)
```
2024-12-05 20:30:45 - timecapsule.app - INFO - main:156 - 应用程序启动
2024-12-05 20:30:46 - timecapsule.app - ERROR - main:160 - 发生错误
```

### JSON 格式 (json)
```json
{"timestamp": "2024-12-05 20:30:45", "logger": "timecapsule.app", "level": "INFO", "module": "main", "line": 156, "message": "应用程序启动"}
```

## 文件管理

### 日志轮转

日志系统支持按文件大小自动轮转：

- 默认最大文件大小：10MB
- 默认备份文件数量：5个
- 当日志文件达到最大大小时，会自动创建新的日志文件
- 旧的日志文件会被重命名为 `app.log.1`, `app.log.2` 等

### 文件命名

- 当前日志文件：`app.log`
- 备份文件：`app.log.1`, `app.log.2`, ...
- 日志目录：`logs/`（可配置）

## 颜色输出

在支持的终端中，不同级别的日志会显示不同颜色：

- 🔵 DEBUG: 青色
- 🟢 INFO: 绿色
- 🟡 WARNING: 黄色
- 🔴 ERROR: 红色
- 🟣 CRITICAL: 紫色

## 集成到现有代码

### 1. 替换 print 语句

```python
# 之前
print("用户登录成功")

# 之后
from app.logger import auth_logger
auth_logger.info("用户登录成功")
```

### 2. 添加异常日志

```python
try:
    # 可能出错的操作
    process_data()
except Exception as e:
    # 记录详细的异常信息
    log_error("数据处理失败", exception=e)
```

### 3. 性能监控

```python
import time
from app.logger import get_logger

logger = get_logger("performance")

def slow_operation():
    start_time = time.time()
    # 执行操作
    result = complex_calculation()
    duration = time.time() - start_time
    logger.info(f"操作完成，耗时: {duration:.2f}秒")
    return result
```

## 最佳实践

### 1. 合理使用日志级别

- **DEBUG**: 详细的调试信息，仅在开发时使用
- **INFO**: 一般信息，记录应用正常运行状态
- **WARNING**: 警告信息，不影响正常运行但需要注意
- **ERROR**: 错误信息，程序可以继续运行
- **CRITICAL**: 严重错误，可能导致程序无法继续运行

### 2. 使用结构化日志

```python
# 好的做法
user_id = 123
action = "login"
logger.info(f"用户操作", extra={"user_id": user_id, "action": action})

# 避免
logger.info(f"用户 123 执行了登录操作")
```

### 3. 避免敏感信息

```python
# 避免记录密码等敏感信息
logger.info(f"用户登录: {username}")  # ✅
logger.info(f"用户登录: {username}, 密码: {password}")  # ❌
```

### 4. 异常处理

```python
try:
    dangerous_operation()
except SpecificException as e:
    logger.error(f"特定异常: {str(e)}", exc_info=True)
    # 处理异常
except Exception as e:
    logger.critical(f"未预期异常: {str(e)}", exc_info=True)
    raise
```

## 故障排除

### 1. 日志文件未生成

- 检查日志目录权限
- 确认 `ENABLE_FILE` 环境变量为 `true`
- 检查磁盘空间

### 2. 日志级别不生效

- 确认环境变量 `LOG_LEVEL` 设置正确
- 检查日志记录器的配置
- 确认没有其他地方覆盖了日志级别

### 3. 颜色不显示

- 检查终端是否支持 ANSI 颜色代码
- 确认 `ENABLE_COLORS` 设置为 `true`
- 某些 IDE 终端可能不支持彩色输出

## 示例项目

查看 `example.py` 文件获取完整的使用示例：

```bash
cd backend/app/logger
python example.py
```

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的日志记录功能
- 支持文件和终端输出
- 支持日志轮转
- 支持多种日志格式