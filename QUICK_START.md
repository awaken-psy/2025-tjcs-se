# 快速启动指南

## 环境设置

### 1. 创建 Conda 环境

```bash
cd d:\Tongji\ThirdGrade\SoftwareEngineering\Project\timecapsule
conda env create -f environment.yml -n timecapsule
conda activate timecapsule
```

### 2. 验证安装

```bash
python -c "import jwt; print('PyJWT 安装成功')"
python -c "import fastapi; print('FastAPI 安装成功')"
```

## 运行应用

### 方式 1: 直接运行

```bash
cd app
python main.py
```

应用将在 `http://localhost:8000` 启动

### 方式 2: 使用 uvicorn

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

启动应用后访问：

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

## 测试用户

系统预配置了三个测试用户，可直接使用：

| 用户名 | user_id   | 角色     | 权限           |
| ------ | --------- | -------- | -------------- |
| 张三   | user_001  | 普通用户 | 胶囊操作、解锁 |
| 李四   | user_002  | 普通用户 | 胶囊操作、解锁 |
| 管理员 | admin_001 | 管理员   | 全部权限       |

## 快速演示

### 1. 获取测试用户列表

```bash
curl http://localhost:8000/api/v1/auth/test-users
```

**预期响应**：

```json
{
  "total": 3,
  "test_users": [
    {
      "user_id": "user_001",
      "username": "张三",
      "role": "user"
    },
    ...
  ]
}
```

### 2. 演示登录获取 Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/demo-login/张三
```

**预期响应**：

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 3. 使用 Token 获取用户信息

```bash
curl -H "Authorization: Bearer <your_access_token>" \
     http://localhost:8000/api/v1/auth/me
```

**预期响应**：

```json
{
  "user_id": "user_001",
  "username": "张三",
  "role": "user",
  "permissions": [
    "create:capsule",
    "read:capsule",
    "update:capsule",
    "delete:capsule",
    "unlock:capsule"
  ],
  "email": "zhangsan@university.edu",
  "department": "计算机学院"
}
```

### 4. 检查权限

```bash
curl -H "Authorization: Bearer <your_access_token>" \
     -X POST http://localhost:8000/api/v1/auth/check-permission \
     -H "Content-Type: application/json" \
     -d '{"required_permission": "create:capsule"}'
```

### 5. 获取用户权限列表

```bash
curl -H "Authorization: Bearer <your_access_token>" \
     http://localhost:8000/api/v1/auth/permissions
```

### 6. 刷新 Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "<your_refresh_token>"}'
```

## 运行测试

### 运行所有测试

```bash
cd tests
pytest -v
```

### 运行特定测试

```bash
# 测试用户系统
pytest test_user_system.py -v

# 测试 JWT 处理
pytest test_jwt_handler.py -v

# 运行特定测试类
pytest test_user_system.py::TestUserModel -v

# 运行特定测试方法
pytest test_user_system.py::TestUserModel::test_guest_user_creation -v
```

## 使用 Postman 测试

### 1. 创建集合

创建新的 Postman 集合 "TimeCapsule User System"

### 2. 添加请求

#### 请求 1: 演示登录

```
POST http://localhost:8000/api/v1/auth/demo-login/张三
```

保存响应中的 `access_token` 到环境变量 `{{token}}`

#### 请求 2: 获取用户信息

```
GET http://localhost:8000/api/v1/auth/me
Header: Authorization: Bearer {{token}}
```

#### 请求 3: 检查权限

```
POST http://localhost:8000/api/v1/auth/check-permission?required_permission=create:capsule
Header: Authorization: Bearer {{token}}
```

## 常见问题

### Q1: PyJWT 导入错误

**错误信息**：`ModuleNotFoundError: No module named 'jwt'`

**解决方案**：

```bash
conda activate timecapsule
pip install PyJWT
```

### Q2: FastAPI 导入错误

**错误信息**：`ModuleNotFoundError: No module named 'fastapi'`

**解决方案**：

```bash
conda activate timecapsule
pip install fastapi uvicorn
```

### Q3: 端口被占用

**错误信息**：`Address already in use`

**解决方案**：

```bash
# 修改启动端口
python -m uvicorn main:app --port 8001
```

### Q4: Token 过期

**症状**：获取受保护资源时返回 401

**解决方案**：

1. 重新获取 Token
2. 或使用 Refresh Token 刷新

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
     -d '{"refresh_token": "<your_refresh_token>"}'
```

## 文件说明

### 核心文件

- `app/auth/jwt_handler.py`：JWT Token 处理
- `app/auth/permission_manager.py`：权限管理
- `app/auth/dependencies.py`：FastAPI 依赖
- `app/models/core/user.py`：用户模型
- `app/api/v1/auth.py`：认证 API
- `app/services/user_service.py`：用户服务

### 示例和文档

- `app/api/v1/capsules_integrated_example.py`：胶囊 API 集成示例
- `USER_SYSTEM_GUIDE.md`：完整的用户系统指南
- `IMPLEMENTATION_SUMMARY.md`：实现总结

### 测试文件

- `tests/test_user_system.py`：用户系统测试
- `tests/test_jwt_handler.py`：JWT 处理器测试

## 集成到现有代码

### 步骤 1: 导入依赖

```python
from auth.dependencies import AuthenticationDependencies
from auth.permission_manager import PermissionManager
from models.core.user import BaseUser
```

### 步骤 2: 在路由中添加用户参数

```python
@router.post("/capsules")
async def create_capsule(
    request: CapsuleCreateRequest,
    user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
):
    # 现在可以使用 user 对象
    ...
```

### 步骤 3: 添加权限检查

```python
if not PermissionManager.can_create_capsule(user):
    raise HTTPException(
        status_code=403,
        detail="您没有权限创建胶囊"
    )
```

## 查看日志

### 应用日志

应用启动时会输出日志，包括：

- 服务启动信息
- 请求处理信息
- 错误信息

### 测试日志

运行测试时可以查看详细日志：

```bash
pytest -v -s
```

## 下一步

1. **数据库集成**：将 UserService 改为数据库查询
2. **用户认证**：实现密码验证
3. **功能扩展**：实现用户注册、用户禁用等功能
4. **性能优化**：添加缓存，优化权限检查
5. **安全增强**：实现密码加密、审计日志等

## 获取帮助

### 查看 API 文档

访问 Swagger UI：http://localhost:8000/docs

### 查看源代码

主要文档：

- `USER_SYSTEM_GUIDE.md`：完整指南
- `IMPLEMENTATION_SUMMARY.md`：实现总结

### 查看测试用例

测试用例展示了各个功能的使用方法：

- `tests/test_user_system.py`
- `tests/test_jwt_handler.py`

---

**提示**：首次使用建议按照"快速演示"部分依次执行命令，熟悉 API 接口。
