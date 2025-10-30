#!/bin/bash
###############################################################################
# Docker 部署脚本
# 使用 Docker 容器化部署应用
###############################################################################

set -e

DEPLOY_ENV="${DEPLOY_ENV:-staging}"
APP_NAME="timecapsule"
IMAGE_NAME="timecapsule"
IMAGE_TAG="${CI_COMMIT_SHORT_SHA:-latest}"

if [ "$DEPLOY_ENV" = "production" ]; then
    CONTAINER_NAME="${APP_NAME}-prod"
    APP_PORT=8000
    IMAGE_TAG="production-${IMAGE_TAG}"
else
    CONTAINER_NAME="${APP_NAME}-staging"
    APP_PORT=8001
    IMAGE_TAG="staging-${IMAGE_TAG}"
fi

echo "========================================="
echo "🐳 Docker 部署: ${APP_NAME}"
echo "========================================="
echo "环境: ${DEPLOY_ENV}"
echo "镜像: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "容器: ${CONTAINER_NAME}"
echo "端口: ${APP_PORT}"
echo "========================================="

# ============================================================================
# 构建 Docker 镜像
# ============================================================================

echo ""
echo "📦 构建 Docker 镜像..."

cat > Dockerfile.deploy <<EOF
FROM continuumio/miniconda3:latest

# 设置工作目录
WORKDIR /app

# 复制环境配置
COPY environment.yml .

# 创建 conda 环境
RUN conda env create -f environment.yml -n timecapsule && \\
    conda clean -afy

# 激活环境
SHELL ["conda", "run", "-n", "timecapsule", "/bin/bash", "-c"]

# 复制应用代码
COPY app/ ./app/

# 暴露端口
EXPOSE ${APP_PORT}

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:${APP_PORT}/health || exit 1

# 启动命令
CMD ["conda", "run", "-n", "timecapsule", "--no-capture-output", \\
     "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${APP_PORT}", "--workers", "4"]
EOF

docker build -f Dockerfile.deploy -t "${IMAGE_NAME}:${IMAGE_TAG}" .

echo "✅ 镜像构建完成"

# ============================================================================
# 停止并删除旧容器
# ============================================================================

echo ""
echo "🛑 停止旧容器..."

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    docker stop "${CONTAINER_NAME}" || true
    docker rm "${CONTAINER_NAME}" || true
    echo "✅ 旧容器已删除"
else
    echo "ℹ️  没有运行中的旧容器"
fi

# ============================================================================
# 启动新容器
# ============================================================================

echo ""
echo "🚀 启动新容器..."

docker run -d \\
    --name "${CONTAINER_NAME}" \\
    --restart unless-stopped \\
    -p "${APP_PORT}:${APP_PORT}" \\
    -e DEPLOY_ENV="${DEPLOY_ENV}" \\
    "${IMAGE_NAME}:${IMAGE_TAG}"

echo "✅ 容器已启动"

# ============================================================================
# 健康检查
# ============================================================================

echo ""
echo "⏳ 等待服务启动..."
sleep 10

MAX_RETRIES=10
RETRY_COUNT=0

while [ ${RETRY_COUNT} -lt ${MAX_RETRIES} ]; do
    if curl -f -s "http://localhost:${APP_PORT}/health" > /dev/null 2>&1; then
        echo "✅ 健康检查通过！"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "重试 ${RETRY_COUNT}/${MAX_RETRIES}..."
    sleep 3

    if [ ${RETRY_COUNT} -eq ${MAX_RETRIES} ]; then
        echo "❌ 健康检查失败"
        echo ""
        echo "容器日志:"
        docker logs "${CONTAINER_NAME}" --tail 50
        exit 1
    fi
done

# ============================================================================
# 部署完成
# ============================================================================

echo ""
echo "========================================="
echo "✅ 部署完成！"
echo "========================================="
echo "容器名称: ${CONTAINER_NAME}"
echo "容器状态:"
docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"
echo ""
echo "API 文档: http://localhost:${APP_PORT}/docs"
echo "健康检查: http://localhost:${APP_PORT}/health"
echo ""
echo "查看日志: docker logs -f ${CONTAINER_NAME}"
echo "停止容器: docker stop ${CONTAINER_NAME}"
echo "========================================="

# 清理构建文件
rm -f Dockerfile.deploy

exit 0
