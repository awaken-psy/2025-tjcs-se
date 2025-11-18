# 🚀 时光胶囊后端快速启动指南

## 📋 前置条件

确保已安装Python和pip，然后安装必要依赖：

```bash
pip install fastapi uvicorn[standard] python-multipart pydantic
```

## 🎯 启动方式

### 方式1: 启动完整版API（推荐）
```bash
cd backend
python simple_server.py
```

### 方式2: 启动最简版本（测试用）
```bash
cd backend
python simple_server.py
```

### 方式3: 从项目根目录启动
```bash
python run_server.py
```

## 📖 访问地址

启动成功后访问：
- **API文档**: http://127.0.0.1:8000/docs
- **健康检查**: http://127.0.0.1:8000/health
- **根路径**: http://127.0.0.1:8000/

## 🔧 胶囊API接口

当前可用的胶囊接口：

1. **创建胶囊**
   ```bash
   POST http://127.0.0.1:8000/api/v1/capsule/create
   ```

2. **获取我的胶囊**
   ```bash
   GET http://127.0.0.1:8000/api/v1/capsule/my
   ```

3. **获取胶囊详情**
   ```bash
   GET http://127.0.0.1:8000/api/v1/capsule/detail/{id}
   ```

4. **编辑胶囊**
   ```bash
   POST http://127.0.0.1:8000/api/v1/capsule/edit/{id}
   ```

5. **删除胶囊**
   ```bash
   POST http://127.0.0.1:8000/api/v1/capsule/delete/{id}
   ```

6. **上传图片**
   ```bash
   POST http://127.0.0.1:8000/api/v1/capsule/upload-img
   ```

## ✅ 前后端对接状态

| 前端API调用 | 后端接口 | 状态 |
|-------------|----------|------|
| `POST /capsule/create` | `POST /api/v1/capsule/create` | ✅ 已实现 |
| `GET /capsule/my` | `GET /api/v1/capsule/my` | ✅ 已实现 |
| `GET /capsule/detail/{id}` | `GET /api/v1/capsule/detail/{id}` | ✅ 已实现 |
| `POST /capsule/edit/{id}` | `POST /api/v1/capsule/edit/{id}` | ✅ 已实现 |
| `POST /capsule/delete/{id}` | `POST /api/v1/capsule/delete/{id}` | ✅ 已实现 |
| `POST /capsule/upload-img` | `POST /api/v1/capsule/upload-img` | ✅ 已实现 |

## 🧪 快速测试

### 1. 测试服务器是否运行
```bash
curl http://127.0.0.1:8000/health
```

### 2. 测试创建胶囊
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/capsule/create" \
  -H "Content-Type: application/json" \
  -d '{"title": "测试", "content": "内容", "visibility": "private"}'
```

## ❓ 常见问题

### Q: 提示 "ModuleNotFoundError"
A: 确保在backend目录下运行，或使用完整路径

### Q: 提示端口被占用
A: 修改端口号或关闭占用端口的程序

### Q: API文档无法访问
A: 检查服务是否成功启动，查看控制台输出

## 📝 注意事项

- 当前版本使用模拟数据
- 无需用户认证即可访问
- 文件上传仅返回模拟URL
- 适用于开发和测试环境

---

🎉 **现在后端API已经准备就绪，可以与前端进行联调测试了！**