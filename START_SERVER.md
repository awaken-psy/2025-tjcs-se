# 🚀 启动时光胶囊后端服务

## 快速启动

### 方法1: 从项目根目录启动（推荐）
```bash
# 在项目根目录 timecapsule/ 下运行
python run_server.py
```

### 方法2: 直接运行服务器文件
```bash
# 进入backend目录
cd backend
python server.py
```

### 方法3: 使用uvicorn启动
```bash
# 进入backend目录
cd backend
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

## 📖 访问地址

启动成功后，访问以下地址：

- **API文档**: http://127.0.0.1:8000/docs
- **健康检查**: http://127.0.0.1:8000/health
- **根路径**: http://127.0.0.1:8000/

## 🔗 可用接口

### 胶囊相关接口（与前端完全匹配）

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/capsule/create` | 创建胶囊 |
| GET | `/api/v1/capsule/my` | 获取我的胶囊列表 |
| GET | `/api/v1/capsule/detail/{id}` | 获取胶囊详情 |
| POST | `/api/v1/capsule/edit/{id}` | 编辑胶囊 |
| POST | `/api/v1/capsule/delete/{id}` | 删除胶囊 |
| POST | `/api/v1/capsule/upload-img` | 上传图片 |

## 🧪 测试示例

### 1. 健康检查
```bash
curl http://127.0.0.1:8000/health
```

### 2. 创建胶囊
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/capsule/create" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试胶囊",
    "content": "这是一个测试胶囊",
    "visibility": "private",
    "tags": ["测试", "胶囊"]
  }'
```

### 3. 获取我的胶囊
```bash
curl "http://127.0.0.1:8000/api/v1/capsule/my?page=1&limit=10"
```

### 4. 获取胶囊详情
```bash
curl "http://127.0.0.1:8000/api/v1/capsule/detail/caps_1"
```

## ⚡ 特性

✅ **完全兼容前端API** - 支持前端使用的所有接口
✅ **模拟数据完整** - 提供详细的模拟数据供测试
✅ **错误处理完善** - 包含完整的错误处理和响应
✅ **自动API文档** - FastAPI自动生成交互式API文档
✅ **开发模式** - 支持热重载，修改代码后自动重启

## 📝 注意事项

1. 当前版本使用模拟数据，数据不会持久化存储
2. 未包含用户认证系统，所有接口都可以直接访问
3. 文件上传功能仅返回模拟URL，不会实际存储文件
4. 适用于开发和测试环境

## 🔧 如果遇到问题

### 1. 模块未找到错误
确保在正确的目录下运行命令：
```bash
# 确保当前目录是项目根目录或backend目录
pwd
```

### 2. 依赖缺失
安装必要的依赖：
```bash
pip install fastapi uvicorn[standard] python-multipart pydantic
```

### 3. 端口被占用
如果8000端口被占用，可以修改端口：
```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8001 --reload
```

## 🎯 前后端对接状态

| 前端API | 后端API | 状态 |
|----------|----------|------|
| `POST /capsule/create` | `POST /api/v1/capsule/create` | ✅ 对接完成 |
| `GET /capsule/my` | `GET /api/v1/capsule/my` | ✅ 对接完成 |
| `GET /capsule/detail/{id}` | `GET /api/v1/capsule/detail/{id}` | ✅ 对接完成 |
| `POST /capsule/edit/{id}` | `POST /api/v1/capsule/edit/{id}` | ✅ 对接完成 |
| `POST /capsule/delete/{id}` | `POST /api/v1/capsule/delete/{id}` | ✅ 对接完成 |
| `POST /capsule/upload-img` | `POST /api/v1/capsule/upload-img` | ✅ 对接完成 |