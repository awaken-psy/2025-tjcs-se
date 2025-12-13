# 胶囊API测试文档

本文档介绍胶囊相关API测试的使用方法和内容结构。

## 📁 测试文件结构

胶囊API测试分为以下6个测试文件：

### 1. `test_5_capsules_basic.py` - 基础CRUD操作测试
- **功能**: 测试胶囊的创建、读取、更新、删除等基本操作
- **测试内容**:
  - 创建公共/私有/好友可见胶囊
  - 创建密码保护胶囊
  - 获取我的胶囊列表（支持过滤和分页）
  - 获取胶囊详情
  - 更新胶囊信息
  - 删除胶囊
  - 保存草稿
  - 验证错误处理和权限检查

### 2. `test_6_capsules_unlock.py` - 解锁功能测试
- **功能**: 测试胶囊的各种解锁条件和状态查询
- **测试内容**:
  - 公共胶囊解锁
  - 密码保护胶囊解锁（正确/错误密码）
  - 时间锁定胶囊解锁
  - 位置锁定胶囊解锁
  - 获取附近胶囊
  - 获取胶囊解锁状态
  - 解锁条件验证

### 3. `test_7_capsules_interactions.py` - 互动功能测试
- **功能**: 测试用户与胶囊的互动操作
- **测试内容**:
  - 点赞/取消点赞胶囊
  - 收藏/取消收藏胶囊
  - 添加评论（主评论和回复）
  - 获取评论列表（支持分页）
  - 删除评论
  - 多用户互动测试
  - 权限验证

### 4. `test_8_capsules_media.py` - 媒体文件测试
- **功能**: 测试胶囊媒体文件的上传和管理
- **测试内容**:
  - 上传图片/音频文件
  - 文件类型验证
  - 文件大小限制
  - 创建包含媒体的胶囊
  - 获取包含媒体的胶囊详情
  - 多媒体文件支持
  - 文件权限和安全检查

### 5. `test_9_capsules_browse.py` - 浏览和搜索测试
- **功能**: 测试胶囊的多种浏览模式
- **测试内容**:
  - 地图模式浏览
  - 时间线模式浏览
  - 标签模式浏览
  - 分页功能
  - 参数验证
  - 数据一致性
  - 可见性过滤

### 6. `test_10_capsules_hub.py` - Hub功能测试
- **功能**: 测试Hub相关功能
- **测试内容**:
  - 获取用户信息和统计数据
  - 获取附近胶囊
  - 距离计算
  - 范围和分页参数
  - 用户数据隔离
  - 位置参数验证

## 🚀 运行测试

### 方法1: 使用专用运行器（推荐）

```bash
# 运行所有胶囊测试
python run_capsules_tests.py

# 运行特定测试文件
python run_capsules_tests.py test_5_capsules_basic.py
python run_capsules_tests.py test_6_capsules_unlock.py
```

### 方法2: 使用pytest直接运行

```bash
# 运行所有胶囊测试
pytest test_5_capsules_basic.py test_6_capsules_unlock.py test_7_capsules_interactions.py test_8_capsules_media.py test_9_capsules_browse.py test_10_capsules_hub.py -v

# 运行单个测试文件
pytest test_5_capsules_basic.py -v

# 运行特定测试类
pytest test_5_capsules_basic.py::TestCapsuleCRUD -v

# 运行特定测试方法
pytest test_5_capsules_basic.py::TestCapsuleCRUD::test_create_capsule_success -v
```

### 方法3: 批量运行

```bash
# 运行所有测试（包括其他模块）
pytest -v

# 只运行胶囊相关测试
pytest -v -k "capsule"

# 运行特定模式的测试
pytest -v -k "test_create_capsule"
```

## 📋 测试前准备

1. **启动后端服务**:
   ```bash
   cd backend
   python app/main.py
   ```

2. **确保数据库可用**:
   - 测试会自动创建所需的胶囊数据
   - 测试完成后会清理创建的数据

3. **检查测试环境**:
   ```bash
   # 检查配置文件
   cat config.py

   # 检查测试数据
   cat data.py
   ```

## 🔧 测试配置

### 配置文件 (`config.py`)
```python
admin_user_email = "admin@admin.com"
base_url = "http://localhost:8000/api"
```

### 测试数据 (`data.py`)
包含测试用户账户信息，用于多用户交互测试。

### 工具函数 (`utils.py`)
提供认证token获取等辅助功能。

## 📊 测试覆盖范围

### ✅ 已覆盖的API端点

#### 胶囊管理 (`/api/v1/capsules/`)
- `POST /capsules/` - 创建胶囊
- `GET /capsules/my` - 获取我的胶囊
- `GET /capsules/browse` - 浏览胶囊（多模式）
- `GET /capsules/{id}` - 获取胶囊详情
- `PUT /capsules/{id}` - 更新胶囊
- `DELETE /capsules/{id}` - 删除胶囊
- `POST /capsules/drafts` - 保存草稿

#### 解锁功能 (`/api/v1/unlock/`)
- `POST /unlock/{id}` - 解锁胶囊
- `GET /unlock/nearby` - 获取附近胶囊
- `GET /unlock/{id}/status` - 获取解锁状态

#### 互动功能 (`/api/v1/interactions/`)
- `POST /interactions/{id}/like` - 点赞胶囊
- `DELETE /interactions/{id}/like` - 取消点赞
- `POST /interactions/{id}/collect` - 收藏胶囊
- `DELETE /interactions/{id}/collect` - 取消收藏
- `POST /interactions/{id}/comments` - 添加评论
- `GET /interactions/{id}/comments` - 获取评论
- `DELETE /interactions/comments/{comment_id}` - 删除评论

#### 媒体上传 (`/api/v1/upload/`)
- `POST /upload/image` - 上传图片
- `POST /upload/audio` - 上传音频

#### Hub功能 (`/api/v1/hub/`)
- `GET /hub/user-info` - 获取用户信息
- `GET /hub/nearby-capsules` - 获取附近胶囊

### 🎯 测试场景覆盖

#### 功能测试
- ✅ 正常业务流程
- ✅ 边界条件测试
- ✅ 异常情况处理
- ✅ 参数验证

#### 权限测试
- ✅ JWT认证
- ✅ 用户权限检查
- ✅ 数据访问控制

#### 数据验证
- ✅ 请求参数验证
- ✅ 响应数据结构
- ✅ 数据类型验证
- ✅ 业务逻辑验证

#### 性能测试
- ✅ 分页功能
- ✅ 大数据量处理
- ✅ 并发操作（基础）

## 🐛 常见问题

### 1. 认证失败
```
FAILED: test_create_capsule_unauthorized - 401
```
**解决**: 确保管理员账户正确且可以登录。

### 2. 连接失败
```
requests.exceptions.ConnectionError
```
**解决**: 确保后端服务在 `http://localhost:8000` 运行。

### 3. 数据库问题
```
数据库连接失败
```
**解决**: 检查数据库配置和连接状态。

### 4. 端口占用
```
Address already in use
```
**解决**: 更改后端端口或停止占用端口的进程。

## 📈 测试报告

运行测试后，可以生成详细的测试报告：

```bash
# 生成HTML报告
pytest --html=report.html --self-contained-html

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 🔍 调试技巧

1. **查看详细输出**:
   ```bash
   pytest -v -s test_5_capsules_basic.py
   ```

2. **运行单个测试**:
   ```bash
   pytest test_5_capsules_basic.py::TestCapsuleCRUD::test_create_capsule_success -v -s
   ```

3. **进入调试模式**:
   ```bash
   pytest --pdb test_5_capsules_basic.py
   ```

4. **查看API响应**:
   测试中的 `print()` 语句会显示API响应的详细信息。

## 📝 添加新测试

1. 在相应的测试文件中添加新的测试方法
2. 使用 `@pytest.fixture` 创建测试数据
3. 遵循现有的命名约定和测试结构
4. 添加适当的断言和错误处理
5. 更新此文档

## 🤝 贡献

如果发现测试问题或有改进建议，请：
1. 检查现有的测试覆盖
2. 添加缺失的测试用例
3. 修复发现的bug
4. 更新文档

---

**注意**: 这些测试会创建真实的胶囊数据，建议在开发或测试环境中运行。