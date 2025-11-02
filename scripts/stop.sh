#!/bin/bash
###############################################################################
# 停止服务脚本
###############################################################################

set -e

DEPLOY_ENV="${DEPLOY_ENV:-staging}"
APP_NAME="timecapsule"

if [ "$DEPLOY_ENV" = "production" ]; then
    DEPLOY_PATH="${DEPLOY_PATH:-/var/www/timecapsule/production}"
    APP_PORT=8000
else
    DEPLOY_PATH="${DEPLOY_PATH:-/var/www/timecapsule/staging}"
    APP_PORT=8001
fi

PID_FILE="${DEPLOY_PATH}/${APP_NAME}.pid"

echo "🛑 停止 ${APP_NAME} (${DEPLOY_ENV})..."

# 通过 PID 文件停止
if [ -f "${PID_FILE}" ]; then
    PID=$(cat "${PID_FILE}")
    if ps -p "${PID}" > /dev/null 2>&1; then
        echo "停止进程 PID: ${PID}"
        kill "${PID}"
        sleep 2
        if ps -p "${PID}" > /dev/null 2>&1; then
            echo "强制停止..."
            kill -9 "${PID}"
        fi
    fi
    rm -f "${PID_FILE}"
    echo "✅ 服务已停止"
else
    # 通过端口查找
    EXISTING_PID=$(lsof -ti:${APP_PORT} 2>/dev/null || true)
    if [ -n "${EXISTING_PID}" ]; then
        echo "停止占用端口 ${APP_PORT} 的进程: ${EXISTING_PID}"
        kill "${EXISTING_PID}"
        echo "✅ 服务已停止"
    else
        echo "⚠️  未找到运行中的服务"
    fi
fi
