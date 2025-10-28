# 时光胶囊·校园 - Campus Time Capsule

## 🌟 项目简介

时光胶囊·校园是一款基于地理位置与时间触发的校园记忆数字化平台，旨在帮助高校师生及校友记录、保存和回溯校园生活中的珍贵瞬间。通过"数字胶囊"的形式，将情感记忆与时空坐标相结合，构建跨届学生之间的情感连接桥梁。

## 🎯 核心价值

- **情感留存**：将校园记忆数字化，实现长期保存
- **时空交织**：地理位置 + 时间触发，创造独特的回忆体验
- **文化传承**：连接在校生与校友，促进校园文化延续
- **情感共鸣**：通过延时解锁机制，增强情感期待与共鸣

## 🚀 快速开始

### 环境要求

- Python 3.13.9
- Conda 包管理器

### 安装与运行

1. **创建并激活环境**

```bash
conda env create -f environment.yml
conda activate timecapsule
```

2. **启动应用**

```bash
python3 app/main.py
```

3. **访问 API 文档**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📱 主要功能

### 🎁 时光胶囊管理

- **创建胶囊**：在校园特定位置创建数字记忆胶囊
- **多媒体支持**：支持文字、图片、语音等多种内容形式
- **解锁胶囊**：在时间、地点等条件下触发解锁胶囊
- **可见性控制**：私有、好友可见、校园公开多级权限

### 🗺️ 地理位置服务

- **精确定位**：基于 GPS 和 WiFi 的校园位置定位
- **地理围栏**：虚拟边界触发胶囊解锁（使用 Haversine 公式计算距离）
- **地图展示**：校园地图上的胶囊分布可视化
- **位置回溯**：重返校园时自动触发历史胶囊

### 👥 用户系统（✨ 新增）

- **用户认证**：基于 JWT 的无状态认证机制
- **RBAC 权限**：三层角色权限模型（访客、用户、管理员）
- **权限控制**：粒度化权限检查和控制
- **用户管理**：用户创建、查询、权限管理
- **可见性控制**：基于用户的内容可见性规则
- **演示登录**：快速获取测试用户 Token

### 👥 用户互动系统

- **社交互动**：点赞、评论、收藏胶囊内容
- **内容分享**：安全的内容分享机制
- **校友连接**：跨届学生的情感交流平台

### 🛡️ 管理审核

- **内容审核**：人工+自动的内容安全过滤
- **用户管理**：多角色权限控制系统
- **数据统计**：校园记忆热力图与访问分析

## 🏗️ 系统架构

### 后端技术栈

```text
Python + FastAPI (异步Web框架)
SQLAlchemy (ORM)
MySQL (主数据库)
Redis (缓存)
Pydantic (数据验证)
JWT (身份认证)
```

### 项目结构

```
timecapsule/
├── app/
│   ├── auth/                    # 认证授权模块（✨ 新增）
│   │   ├── jwt_handler.py       # JWT Token 处理
│   │   ├── permission_manager.py # 权限管理
│   │   ├── dependencies.py      # FastAPI 依赖
│   │   └── decorators.py        # 权限装饰器
│   ├── services/                # 服务模块（✨ 新增）
│   │   └── user_service.py      # 用户服务
│   ├── api/v1/
│   │   ├── auth.py              # 认证 API（✨ 新增）
│   │   ├── capsules.py          # 胶囊管理 API
│   │   ├── capsules_integrated_example.py  # 集成示例
│   │   └── unlock.py            # 解锁功能 API
│   ├── models/
│   │   ├── core/
│   │   │   ├── user.py          # 用户模型（✨ 新增）
│   │   │   ├── capsule.py       # 胶囊核心模型（✨ 增强）
│   │   │   └── condition.py     # 解锁条件模型
│   │   └── net/
│   │       ├── request.py       # 请求模型
│   │       └── response.py      # 响应模型
│   └── main.py                  # 应用入口
├── tests/                       # 测试目录（✨ 新增）
│   ├── test_user_system.py     # 用户系统测试
│   └── test_jwt_handler.py     # JWT 处理测试
├── USER_SYSTEM_GUIDE.md         # 用户系统指南（✨ 新增）
├── IMPLEMENTATION_SUMMARY.md    # 实现总结（✨ 新增）
├── QUICK_START.md               # 快速启动指南（✨ 新增）
├── FILE_MANIFEST.md             # 文件清单（✨ 新增）
├── environment.yml              # 环境配置（✨ 已更新）
└── README.md                    # 项目文档（✨ 已更新）
```

## 🔧 API 接口

### 认证接口（✨ 新增）

- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新 Token
- `GET /api/v1/auth/me` - 获取当前用户信息
- `GET /api/v1/auth/permissions` - 获取用户权限列表
- `POST /api/v1/auth/check-permission` - 检查权限
- `GET /api/v1/auth/test-users` - 获取测试用户（演示用）
- `POST /api/v1/auth/demo-login/{username}` - 演示登录（无需密码）

### 胶囊管理接口

- `POST /api/v1/capsules` - 创建新胶囊
- `GET /api/v1/capsules` - 获取胶囊列表
- `GET /api/v1/capsules/{capsule_id}` - 获取胶囊详情
- `PUT /api/v1/capsules/{capsule_id}` - 更新胶囊信息
- `DELETE /api/v1/capsules/{capsule_id}` - 删除胶囊

### 解锁功能接口

- `POST /api/v1/unlock/check` - 检查可解锁胶囊
- `POST /api/v1/unlock/capsule` - 解锁指定胶囊

### 解锁条件类型

- **时间条件**：指定日期时间解锁
- **位置条件**：到达指定地理范围内解锁
- **组合条件**：同时满足时间和位置条件

## 💡 核心特性

### 用户认证系统（✨ 新增）

- **JWT 无状态认证**：支持分布式部署
- **角色权限模型**：三层权限体系（访客、用户、管理员）
- **粒度化权限控制**：按操作类型进行权限检查
- **权限继承关系**：支持权限层级和继承
- **可见性控制**：基于用户角色的内容可见性

### 智能解锁机制

- **时间触发**：在特定日期自动解锁
- **位置触发**：当用户进入指定地理范围时解锁
- **组合触发**：同时满足时间和位置条件
- **距离计算**：使用 Haversine 公式精确计算地理距离

### 数据模型设计

- **胶囊状态**：LOCKED（锁定）、UNLOCKED（已解锁）、EXPIRED（已过期）
- **可见性级别**：PRIVATE（私有）、FRIENDS（好友可见）、CAMPUS（校园公开）
- **内容类型**：TEXT（文本）、IMAGE（图片）、AUDIO（音频）、MIXED（混合）

### 响应标准化

所有 API 响应遵循统一格式：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

## 🔄 开发状态

### ✅ 已完成

- [x] FastAPI 基础框架搭建
- [x] 胶囊管理 API 接口
- [x] 解锁功能 API 接口
- [x] 数据模型定义
- [x] 位置距离计算算法
- [x] 解锁条件验证逻辑
- [x] 用户认证系统（新增）
- [x] 权限管理系统（新增）
- [x] JWT Token 处理（新增）
- [x] FastAPI 依赖注入（新增）
- [x] 权限装饰器（新增）
- [x] 用户模型和服务（新增）

### 🚧 进行中

- [ ] 数据库集成
- [ ] 用户注册功能
- [ ] 文件上传功能
- [ ] 缓存系统实现

### 📋 待开发

- [ ] 前端界面
- [ ] 移动端应用
- [ ] 推送通知
- [ ] 数据分析系统

## 📚 文档资源

### 用户系统相关文档（✨ 新增）

1. **USER_SYSTEM_GUIDE.md** - 完整的用户系统指南

   - 系统架构详细说明
   - API 使用示例
   - 集成指南和最佳实践

2. **QUICK_START.md** - 快速启动指南

   - 环境设置步骤
   - 运行应用说明
   - 测试用户信息
   - 常见问题解决

3. **IMPLEMENTATION_SUMMARY.md** - 实现总结

   - 项目完成情况
   - 实现模块清单
   - 验收标准完成情况
   - 技术架构说明

4. **FILE_MANIFEST.md** - 文件清单
   - 创建和修改的所有文件列表
   - 功能统计信息
   - 使用快速开始

## 🎯 快速体验用户系统

### 1. 获取演示 Token

```bash
# 演示登录获取 Token（不需要密码）
curl -X POST http://localhost:8000/api/v1/auth/demo-login/张三

# 响应示例：
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 2. 获取当前用户信息

```bash
# 使用 Token 获取用户信息
curl -H "Authorization: Bearer <your_access_token>" \
     http://localhost:8000/api/v1/auth/me

# 响应示例：
{
  "user_id": "user_001",
  "username": "张三",
  "role": "user",
  "permissions": ["create:capsule", "read:capsule", ...],
  "email": "zhangsan@university.edu",
  "department": "计算机学院"
}
```

### 3. 检查权限

```bash
# 检查用户是否有创建胶囊的权限
curl -H "Authorization: Bearer <your_access_token>" \
     "http://localhost:8000/api/v1/auth/check-permission?required_permission=create:capsule"
```

## 👥 预配置测试用户

| 用户名 | user_id   | 角色     | 权限                       |
| ------ | --------- | -------- | -------------------------- |
| 张三   | user_001  | 普通用户 | 创建、读取、编辑、删除胶囊 |
| 李四   | user_002  | 普通用户 | 创建、读取、编辑、删除胶囊 |
| 管理员 | admin_001 | 管理员   | 全部权限                   |

**获取测试用户列表**：

```bash
curl http://localhost:8000/api/v1/auth/test-users
```
