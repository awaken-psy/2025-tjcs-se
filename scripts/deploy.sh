#!/bin/bash
###############################################################################
# 时光胶囊项目部署脚本
# 用于自动化部署 FastAPI 应用到服务器
###############################################################################

set -e  # 遇到错误立即退出

# ============================================================================
# 配置变量
# ============================================================================

# 环境变量（可通过 GitLab CI/CD Variables 配置）
DEPLOY_ENV="${DEPLOY_ENV:-staging}"  # staging 或 production
APP_NAME="timecapsule"
APP_PORT="${APP_PORT:-8000}"
CONDA_ENV_NAME="${CONDA_ENV_NAME:-timecapsule}"

# 部署路径
if [ "$DEPLOY_ENV" = "production" ]; then
    DEPLOY_PATH="${DEPLOY_PATH:-/var/www/timecapsule/production}"
    APP_PORT=8000
else
    DEPLOY_PATH="${DEPLOY_PATH:-/var/www/timecapsule/staging}"
    APP_PORT=8001
fi

# 日志
LOG_FILE="${DEPLOY_PATH}/logs/deploy.log"
APP_LOG_FILE="${DEPLOY_PATH}/logs/app.log"

# ============================================================================
# 工具函数
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ❌ ERROR: $1" | tee -a "${LOG_FILE}"
    exit 1
}

success() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1" | tee -a "${LOG_FILE}"
}

# ============================================================================
# 前置检查
# ============================================================================

log "========================================="
log "开始部署 ${APP_NAME} - ${DEPLOY_ENV} 环境"
log "========================================="

# 检查 conda
if ! command -v conda &> /dev/null; then
    error "Conda 未安装，请先安装 Miniconda 或 Anaconda"
fi

# 创建部署目录
log "创建部署目录..."
mkdir -p "${DEPLOY_PATH}"
mkdir -p "${DEPLOY_PATH}/logs"
mkdir -p "${DEPLOY_PATH}/backup"

# ============================================================================
# 备份现有部署
# ============================================================================

if [ -d "${DEPLOY_PATH}/app" ]; then
    log "备份当前部署..."
    BACKUP_NAME="backup_$(date +'%Y%m%d_%H%M%S')"
    tar -czf "${DEPLOY_PATH}/backup/${BACKUP_NAME}.tar.gz" \
        -C "${DEPLOY_PATH}" app environment.yml 2>/dev/null || true
    success "备份完成: ${BACKUP_NAME}.tar.gz"

    # 保留最近5个备份
    cd "${DEPLOY_PATH}/backup"
    ls -t backup_*.tar.gz | tail -n +6 | xargs -r rm
fi

# ============================================================================
# 部署新代码
# ============================================================================

log "复制应用文件..."
# 从 CI/CD 环境复制文件（假设代码已经在当前目录）
cp -r app "${DEPLOY_PATH}/"
cp environment.yml "${DEPLOY_PATH}/"
cp -r tests "${DEPLOY_PATH}/" 2>/dev/null || true
success "文件复制完成"

# ============================================================================
# 配置 Conda 环境
# ============================================================================

log "配置 Conda 环境: ${CONDA_ENV_NAME}..."

# 初始化 conda（确保 conda 命令可用）
eval "$(conda shell.bash hook)"

# 检查环境是否存在
if conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    log "更新现有 Conda 环境..."
    conda env update -f "${DEPLOY_PATH}/environment.yml" -n "${CONDA_ENV_NAME}" --prune
else
    log "创建新的 Conda 环境..."
    conda env create -f "${DEPLOY_PATH}/environment.yml" -n "${CONDA_ENV_NAME}"
fi

success "Conda 环境配置完成"

# ============================================================================
# 停止旧服务
# ============================================================================

log "停止旧服务..."

# 查找并停止现有进程
PID_FILE="${DEPLOY_PATH}/${APP_NAME}.pid"
if [ -f "${PID_FILE}" ]; then
    OLD_PID=$(cat "${PID_FILE}")
    if ps -p "${OLD_PID}" > /dev/null 2>&1; then
        log "停止进程 PID: ${OLD_PID}"
        kill "${OLD_PID}" || true
        sleep 2
        # 如果还没停止，强制杀死
        if ps -p "${OLD_PID}" > /dev/null 2>&1; then
            kill -9 "${OLD_PID}" || true
        fi
    fi
    rm -f "${PID_FILE}"
fi

# 备用方案：通过端口查找进程
EXISTING_PID=$(lsof -ti:${APP_PORT} 2>/dev/null || true)
if [ -n "${EXISTING_PID}" ]; then
    log "停止占用端口 ${APP_PORT} 的进程: ${EXISTING_PID}"
    kill "${EXISTING_PID}" || true
    sleep 2
fi

success "旧服务已停止"

# ============================================================================
# 运行测试（可选）
# ============================================================================

if [ "${RUN_TESTS:-false}" = "true" ]; then
    log "运行测试..."
    cd "${DEPLOY_PATH}"
    conda run -n "${CONDA_ENV_NAME}" pytest tests/ -v || error "测试失败，部署终止"
    success "测试通过"
fi

# ============================================================================
# 启动新服务
# ============================================================================

log "启动新服务..."

cd "${DEPLOY_PATH}/app"

# 使用 nohup 在后台启动服务
nohup conda run -n "${CONDA_ENV_NAME}" --no-capture-output \
    uvicorn main:app \
    --host 0.0.0.0 \
    --port "${APP_PORT}" \
    --workers 4 \
    > "${APP_LOG_FILE}" 2>&1 &

NEW_PID=$!
echo "${NEW_PID}" > "${PID_FILE}"

log "等待服务启动 (PID: ${NEW_PID})..."
sleep 5

# ============================================================================
# 健康检查
# ============================================================================

log "执行健康检查..."

MAX_RETRIES=10
RETRY_COUNT=0
HEALTH_CHECK_URL="http://localhost:${APP_PORT}/health"

while [ ${RETRY_COUNT} -lt ${MAX_RETRIES} ]; do
    if curl -f -s "${HEALTH_CHECK_URL}" > /dev/null 2>&1; then
        success "健康检查通过！"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    log "健康检查失败，重试 ${RETRY_COUNT}/${MAX_RETRIES}..."
    sleep 3

    if [ ${RETRY_COUNT} -eq ${MAX_RETRIES} ]; then
        error "健康检查失败，服务可能未正常启动"
    fi
done

# ============================================================================
# 部署完成
# ============================================================================

log "========================================="
success "部署完成！"
log "========================================="
log "环境: ${DEPLOY_ENV}"
log "端口: ${APP_PORT}"
log "PID: ${NEW_PID}"
log "日志: ${APP_LOG_FILE}"
log "API 文档: http://localhost:${APP_PORT}/docs"
log "健康检查: http://localhost:${APP_PORT}/health"
log "========================================="

# 显示服务状态
log "服务状态:"
ps -fp "${NEW_PID}" || error "服务进程不存在"

exit 0
