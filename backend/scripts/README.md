# 部署脚本使用指南

本目录包含时光胶囊项目的各种部署和管理脚本。

## 📋 脚本清单

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `deploy.sh` | 传统部署 | 直接部署到服务器（使用 Conda） |
| `deploy-docker.sh` | Docker 部署 | 容器化部署 |
| `stop.sh` | 停止服务 | 停止运行中的应用 |
| `status.sh` | 查看状态 | 查看服务运行状态和健康检查 |
| `rollback.sh` | 版本回滚 | 回滚到上一个版本 |

## 🚀 快速开始

### 方式 1: 传统部署（Conda）

```bash
# 给脚本添加执行权限
chmod +x scripts/*.sh

# 部署到 Staging 环境
DEPLOY_ENV=staging bash scripts/deploy.sh

# 部署到 Production 环境
DEPLOY_ENV=production bash scripts/deploy.sh
```

### 方式 2: Docker 部署

```bash
# 部署到 Staging 环境
DEPLOY_ENV=staging bash scripts/deploy-docker.sh

# 部署到 Production 环境
DEPLOY_ENV=production bash scripts/deploy-docker.sh
```

## 📖 详细说明

### deploy.sh - 传统部署脚本

**功能**：
- ✅ 自动备份旧版本
- ✅ 配置 Conda 环境
- ✅ 停止旧服务
- ✅ 启动新服务
- ✅ 健康检查
- ✅ 保留最近 5 个备份

**环境变量**：

```bash
# 部署环境 (staging 或 production)
DEPLOY_ENV=staging

# 部署路径（可选，有默认值）
DEPLOY_PATH=/var/www/timecapsule/staging

# 应用端口（可选）
APP_PORT=8001

# Conda 环境名称（可选）
CONDA_ENV_NAME=timecapsule

# 是否运行测试（可选）
RUN_TESTS=true
```

**使用示例**：

```bash
# 基本部署
bash scripts/deploy.sh

# 部署前运行测试
RUN_TESTS=true bash scripts/deploy.sh

# 自定义部署路径
DEPLOY_PATH=/home/user/myapp bash scripts/deploy.sh

# 完整示例
DEPLOY_ENV=production \
DEPLOY_PATH=/var/www/timecapsule/production \
APP_PORT=8000 \
RUN_TESTS=true \
bash scripts/deploy.sh
```

**默认配置**：

| 环境 | 路径 | 端口 |
|------|------|------|
| Staging | `/var/www/timecapsule/staging` | 8001 |
| Production | `/var/www/timecapsule/production` | 8000 |

**目录结构**：

```
/var/www/timecapsule/staging/
├── app/                    # 应用代码
├── environment.yml         # Conda 环境配置
├── logs/
│   ├── deploy.log         # 部署日志
│   └── app.log            # 应用日志
├── backup/
│   ├── backup_20241030_140000.tar.gz
│   └── ...
└── timecapsule.pid        # 进程 PID 文件
```

### deploy-docker.sh - Docker 部署脚本

**功能**：
- ✅ 自动构建 Docker 镜像
- ✅ 停止并删除旧容器
- ✅ 启动新容器
- ✅ 健康检查
- ✅ 自动重启策略

**环境变量**：

```bash
# 部署环境
DEPLOY_ENV=staging

# 镜像标签（可选，CI 环境中自动设置）
CI_COMMIT_SHORT_SHA=abc123
```

**使用示例**：

```bash
# 部署到 Staging
DEPLOY_ENV=staging bash scripts/deploy-docker.sh

# 部署到 Production
DEPLOY_ENV=production bash scripts/deploy-docker.sh

# 在 CI/CD 中使用（自动获取 Git SHA）
CI_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD) \
DEPLOY_ENV=production \
bash scripts/deploy-docker.sh
```

**容器管理**：

```bash
# 查看容器状态
docker ps -a | grep timecapsule

# 查看容器日志
docker logs -f timecapsule-staging

# 停止容器
docker stop timecapsule-staging

# 删除容器
docker rm timecapsule-staging

# 查看镜像
docker images | grep timecapsule
```

### stop.sh - 停止服务

**功能**：
- 停止运行中的应用（传统部署）

**使用示例**：

```bash
# 停止 Staging 服务
DEPLOY_ENV=staging bash scripts/stop.sh

# 停止 Production 服务
DEPLOY_ENV=production bash scripts/stop.sh
```

### status.sh - 查看服务状态

**功能**：
- ✅ 查看进程状态
- ✅ 查看端口监听
- ✅ 健康检查
- ✅ 显示最近日志

**使用示例**：

```bash
# 查看 Staging 状态
DEPLOY_ENV=staging bash scripts/status.sh

# 查看 Production 状态
DEPLOY_ENV=production bash scripts/status.sh
```

**输出示例**：

```
=========================================
📊 timecapsule 服务状态 (staging)
=========================================
✅ 状态: 运行中
📍 PID: 12345
🔌 端口: 8001

进程信息:
UID    PID  PPID ... CMD
user 12345     1 ... uvicorn main:app

✅ 端口 8001 正在监听

健康检查:
✅ 健康检查通过
{
  "status": "healthy",
  "timestamp": "2024-10-30T14:00:00Z"
}
=========================================
```

### rollback.sh - 版本回滚

**功能**：
- ✅ 列出可用备份
- ✅ 回滚到上一个版本
- ✅ 安全确认提示

**使用示例**：

```bash
# 回滚 Staging
DEPLOY_ENV=staging bash scripts/rollback.sh

# 回滚 Production（需要确认）
DEPLOY_ENV=production bash scripts/rollback.sh
```

**交互流程**：

```
🔄 开始回滚 timecapsule (staging)...

可用的备份:
----------------------------------------
1  -rw-r--r-- 1 user user 2.1M Oct 30 14:00 backup_20241030_140000.tar.gz
2  -rw-r--r-- 1 user user 2.0M Oct 30 13:00 backup_20241030_130000.tar.gz
----------------------------------------

将回滚到: backup_20241030_140000.tar.gz
确认回滚? (yes/no): yes

停止当前服务...
备份当前版本...
删除当前部署...
恢复备份...
✅ 回滚完成

请手动重新启动服务或运行部署脚本
bash scripts/deploy.sh
```

## 🔧 在 GitLab CI/CD 中使用

### 配置 CI/CD Variables

在 GitLab 项目设置中配置以下变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `SSH_PRIVATE_KEY` | SSH 私钥 | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DEPLOY_SERVER` | 部署服务器地址 | `deploy@example.com` |
| `DEPLOY_PATH_STAGING` | Staging 部署路径 | `/var/www/timecapsule/staging` |
| `DEPLOY_PATH_PRODUCTION` | Production 部署路径 | `/var/www/timecapsule/production` |

### 在 .gitlab-ci.yml 中使用

```yaml
deploy:staging:
  stage: deploy
  script:
    # 使用 SSH 连接到服务器
    - 'which ssh-agent || ( apt-get update -y && apt-get install openssh-client -y )'
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh

    # 复制文件到服务器
    - scp -r app/ environment.yml scripts/ $DEPLOY_SERVER:/tmp/timecapsule/

    # 在服务器上执行部署
    - ssh $DEPLOY_SERVER "cd /tmp/timecapsule && DEPLOY_ENV=staging bash scripts/deploy.sh"
  environment:
    name: staging
    url: https://staging.timecapsule.example.com
  only:
    - develop
  when: manual
```

## 📝 日志管理

### 查看日志

```bash
# 实时查看应用日志
tail -f /var/www/timecapsule/staging/logs/app.log

# 查看部署日志
tail -f /var/www/timecapsule/staging/logs/deploy.log

# 查看 Docker 容器日志
docker logs -f timecapsule-staging --tail 100
```

### 日志轮转

建议配置 logrotate 进行日志轮转：

```bash
# 创建 /etc/logrotate.d/timecapsule
/var/www/timecapsule/*/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 user user
    sharedscripts
    postrotate
        # 重启服务（可选）
    endscript
}
```

## ⚠️ 注意事项

1. **权限要求**：
   - 脚本需要执行权限：`chmod +x scripts/*.sh`
   - 部署路径需要写权限
   - Docker 部署需要 Docker 权限

2. **端口占用**：
   - Staging: 8001
   - Production: 8000
   - 确保端口未被占用

3. **备份策略**：
   - 自动保留最近 5 个备份
   - 建议定期手动备份到远程存储

4. **健康检查**：
   - 依赖 `/health` 端点
   - 最多重试 10 次，每次间隔 3 秒

5. **环境隔离**：
   - Staging 和 Production 使用不同端口和路径
   - 避免相互影响

## 🛠️ 故障排查

### 问题 1: 服务启动失败

```bash
# 查看应用日志
tail -n 50 /var/www/timecapsule/staging/logs/app.log

# 检查端口占用
lsof -i:8001

# 检查 Conda 环境
conda env list
conda activate timecapsule
python -c "import fastapi; print('OK')"
```

### 问题 2: 健康检查失败

```bash
# 手动测试健康检查
curl http://localhost:8001/health

# 查看进程状态
ps aux | grep uvicorn

# 检查防火墙
sudo ufw status
```

### 问题 3: Docker 容器无法启动

```bash
# 查看容器日志
docker logs timecapsule-staging

# 检查镜像
docker images | grep timecapsule

# 重新构建镜像
docker build --no-cache -t timecapsule:latest .
```

## 📚 参考资料

- [FastAPI 部署文档](https://fastapi.tiangolo.com/deployment/)
- [Conda 环境管理](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
- [Docker 官方文档](https://docs.docker.com/)
- [GitLab CI/CD 文档](https://docs.gitlab.com/ee/ci/)
