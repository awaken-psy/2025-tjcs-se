"""
用户系统集成指南

这个文档介绍了如何在时光胶囊应用中使用新实现的用户权限系统。
"""

# ============================================================================

# 用户系统架构概览

# ============================================================================

"""

## 用户系统架构

### 核心模块

1. **models/core/user.py** - 用户数据模型

   - UserRole: 用户角色枚举（GUEST, USER, ADMIN）
   - Permission: 权限枚举（CREATE_CAPSULE, READ_CAPSULE, etc.）
   - BaseUser: 用户基类
   - AccessUser: 访客用户
   - AuthenticatedUser: 认证用户
   - AdminUser: 管理员用户
   - UserFactory: 用户工厂类

2. **auth/jwt_handler.py** - JWT Token 处理

   - JWTHandler: 生成、验证、刷新 Token
   - JWTConfig: JWT 配置

3. **auth/permission_manager.py** - 权限管理

   - PermissionManager: 权限检查和验证
   - PermissionDeniedException: 权限异常

4. **auth/dependencies.py** - FastAPI 依赖注入

   - AuthenticationDependencies: 认证依赖
   - PermissionChecker: 权限检查器

5. **auth/decorators.py** - 权限装饰器

   - @require_permission: 需要特定权限
   - @require_any_permission: 需要任意权限
   - @require_all_permissions: 需要所有权限
   - @require_admin: 需要管理员权限

6. **api/v1/auth.py** - 认证 API 路由

   - /auth/login: 用户登录
   - /auth/refresh: 刷新 Token
   - /auth/me: 获取当前用户信息
   - /auth/permissions: 获取用户权限
   - /auth/demo-login/{username}: 演示登录（测试用）

7. **services/user_service.py** - 用户服务
   - UserService: 用户数据管理（临时 mock 实现）

### 用户角色和权限

#### 访客用户 (GUEST)

权限:

- read:capsule: 读取胶囊

使用场景:

- 未登录用户
- 只能浏览公开内容

#### 认证用户 (USER)

权限:

- create:capsule: 创建胶囊
- read:capsule: 读取胶囊
- update:capsule: 更新胶囊（仅自己的）
- delete:capsule: 删除胶囊（仅自己的）
- unlock:capsule: 解锁胶囊

使用场景:

- 已登录用户
- 可以创建和管理自己的胶囊

#### 管理员用户 (ADMIN)

权限:

- create:capsule, read:capsule, update:capsule, delete:capsule: 胶囊操作
- create:user, read:user, update:user, delete:user: 用户管理
- moderate:content: 内容审核
- manage:permissions: 权限管理
- view:analytics: 查看分析数据

使用场景:

- 系统管理员
- 可以完全控制系统

### 权限检查流程

1. 请求到达 → 从 Authorization 请求头提取 JWT Token
2. Token 验证 → 解析 Token 获取用户信息和权限
3. 权限检查 → 根据路由需要的权限进行检查
4. 执行处理 → 如果权限检查通过，执行业务逻辑
5. 返回响应 → 返回结果给客户端

## 快速开始

### 1. 获取测试用户列表

GET /api/v1/auth/test-users

返回:
{
"total": 3,
"test_users": [
{
"user_id": "user_001",
"username": "张三",
"role": "user"
},
{
"user_id": "user_002",
"username": "李四",
"role": "user"
},
{
"user_id": "admin_001",
"username": "管理员",
"role": "admin"
}
]
}

### 2. 演示登录获取 Token

POST /api/v1/auth/demo-login/张三

返回:
{
"access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
"token_type": "bearer",
"expires_in": 86400
}

### 3. 使用 Token 访问受保护的资源

GET /api/v1/auth/me
Headers:
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

返回:
{
"user_id": "user_001",
"username": "张三",
"role": "user",
"permissions": ["create:capsule", "read:capsule", "update:capsule", "delete:capsule", "unlock:capsule"],
"email": "zhangsan@university.edu",
"department": "计算机学院"
}

## API 使用示例

### 示例 1: 普通用户创建胶囊

1. 先获取 Token
   POST /api/v1/auth/demo-login/张三

2. 使用 Token 创建胶囊
   POST /api/v1/capsules
   Headers:
   Authorization: Bearer <token>
   Body:
   {
   "title": "校园回忆",
   "content": "美好的校园时光...",
   "visibility": "campus"
   }

权限检查:

- ✅ 检查用户有 CREATE_CAPSULE 权限
- ✅ 自动设置所有者为当前用户
- ✅ 保存胶囊

结果:

- 胶囊创建成功
- owner_id = "user_001"

### 示例 2: 访问胶囊列表

1. 不登录获取胶囊列表
   GET /api/v1/capsules

   返回:

   - 只能看到 visibility=CAMPUS 的胶囊

2. 用普通用户登录后获取列表
   GET /api/v1/capsules
   Headers:
   Authorization: Bearer <user_token>

   返回:

   - 可以看到自己的胶囊（所有可见性）
   - 可以看到好友的胶囊（visibility=FRIENDS）
   - 可以看到公开胶囊（visibility=CAMPUS）

3. 用管理员登录后获取列表
   GET /api/v1/capsules
   Headers:
   Authorization: Bearer <admin_token>

   返回:

   - 可以看到所有胶囊（不受可见性限制）

### 示例 3: 编辑胶囊

只有所有者和管理员可以编辑:

PUT /api/v1/capsules/caps_001
Headers:
Authorization: Bearer <token>
Body:
{
"title": "更新的标题",
"content": "更新的内容"
}

权限检查:

- ✅ 检查用户有 UPDATE_CAPSULE 权限
- ✅ 检查用户是否为所有者或管理员
- ❌ 拒绝其他用户编辑

### 示例 4: 删除胶囊

只有所有者和管理员可以删除:

DELETE /api/v1/capsules/caps_001
Headers:
Authorization: Bearer <token>

权限检查:

- ✅ 检查用户有 DELETE_CAPSULE 权限
- ✅ 检查用户是否为所有者或管理员
- ❌ 拒绝其他用户删除

### 示例 5: 内容审核（仅管理员）

POST /api/v1/capsules/caps_001/moderate
Headers:
Authorization: Bearer <admin_token>
Body:
{
"action": "approve",
"reason": null
}

权限检查:

- ✅ 检查用户有 MODERATE_CONTENT 权限
- ✅ 只有管理员可以执行
- ❌ 拒绝普通用户执行

## 集成到现有代码

### 步骤 1: 在路由中添加用户参数

旧代码:

```python
@router.post("/capsules")
async def create_capsule(request: CapsuleCreateRequest):
    ...
```

新代码:

```python
from auth.dependencies import AuthenticationDependencies
from models.core.user import BaseUser

@router.post("/capsules")
async def create_capsule(
    request: CapsuleCreateRequest,
    user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
):
    ...
```

### 步骤 2: 添加权限检查

```python
from auth.permission_manager import PermissionManager

async def create_capsule(...):
    # 检查权限
    if not PermissionManager.can_create_capsule(user):
        raise HTTPException(
            status_code=403,
            detail="您没有权限创建胶囊"
        )

    # 关联用户
    capsule.owner_id = user.user_id
    ...
```

### 步骤 3: 处理可见性控制

```python
async def get_capsule_detail(capsule_id: str, user: BaseUser = ...):
    capsule = db.get_capsule(capsule_id)

    # 检查可见性
    is_admin = PermissionManager.is_admin(user)
    if not capsule.can_view_by(user.user_id, is_admin=is_admin):
        raise HTTPException(
            status_code=403,
            detail="您没有权限查看这个胶囊"
        )

    return capsule
```

## 测试

运行单元测试:

```bash
cd tests
pytest test_user_system.py -v
pytest test_jwt_handler.py -v
```

测试覆盖:

- ✅ 用户模型创建和权限检查
- ✅ JWT Token 生成、验证、刷新
- ✅ 权限管理和权限检查
- ✅ 不同角色的权限差异

## 最佳实践

### 1. 始终检查权限

不要假设用户有权限执行操作，始终显式检查:

```python
if not PermissionManager.can_delete_capsule(user, capsule.owner_id):
    raise HTTPException(status_code=403, detail="...")
```

### 2. 在模型级别实现权限逻辑

使用 Capsule 模型的方法进行权限检查:

```python
if not capsule.can_edit_by(user.user_id, is_admin=admin):
    raise HTTPException(status_code=403, detail="...")
```

### 3. 记录审计日志

对重要操作记录日志:

```python
audit_log.record(
    action="delete_capsule",
    user_id=user.user_id,
    capsule_id=capsule_id,
    timestamp=datetime.now()
)
```

### 4. 使用依赖注入

使用 FastAPI 的依赖注入系统简化代码:

```python
@router.post("/capsules")
async def create_capsule(
    request: CapsuleCreateRequest,
    user: BaseUser = Depends(
        PermissionChecker.require_permission(Permission.CREATE_CAPSULE)
    )
):
    ...  # user 已经过权限检查
```

## 下一步

### 数据库集成

1. 将 UserService 从 mock 实现改为数据库查询
2. 实现用户持久化
3. 添加用户认证（密码验证）
4. 实现用户注册流程

### 功能扩展

1. 实现用户好友关系
2. 添加用户信息完善
3. 实现用户禁用功能
4. 添加权限审计日志
5. 实现基于时间的权限过期

### 性能优化

1. 缓存 Token 验证结果
2. 实现权限缓存
3. 使用 Redis 存储会话
4. 优化权限检查算法
   """

# ============================================================================

# 快速参考

# ============================================================================

# 创建用户

from models.core.user import UserFactory

guest = UserFactory.create_guest_user()
user = UserFactory.create_authenticated_user(user_id="user_001", username="张三")
admin = UserFactory.create_admin_user(user_id="admin_001", username="管理员")

# 检查权限

from auth.permission_manager import PermissionManager
from models.core.user import Permission

has_perm = PermissionManager.check_permission(user, Permission.CREATE_CAPSULE)
can_edit = PermissionManager.can_update_capsule(user, "owner_id")
is_admin = PermissionManager.is_admin(user)

# 生成 Token

from auth.jwt_handler import JWTHandler
from models.core.user import UserRole

token = JWTHandler.generate_access_token(
user_id="user_001",
username="张三",
role=UserRole.USER,
permissions=["create:capsule", "read:capsule"]
)

refresh_token = JWTHandler.generate_refresh_token(
user_id="user_001",
username="张三"
)

# 验证 Token

valid, payload = JWTHandler.verify_access_token(token)

# 在 FastAPI 中使用

from fastapi import Depends
from auth.dependencies import AuthenticationDependencies

async def my_route(
user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
):
...
