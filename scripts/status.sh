#!/bin/bash
###############################################################################
# 查看服务状态脚本
###############################################################################

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
APP_LOG_FILE="${DEPLOY_PATH}/logs/app.log"

echo "========================================="
echo "📊 ${APP_NAME} 服务状态 (${DEPLOY_ENV})"
echo "========================================="

# 检查 PID 文件
if [ -f "${PID_FILE}" ]; then
    PID=$(cat "${PID_FILE}")
    if ps -p "${PID}" > /dev/null 2>&1; then
        echo "✅ 状态: 运行中"
        echo "📍 PID: ${PID}"
        echo "🔌 端口: ${APP_PORT}"
        echo ""
        echo "进程信息:"
        ps -fp "${PID}"
        echo ""

        # 检查端口
        if lsof -i:${APP_PORT} > /dev/null 2>&1; then
            echo "✅ 端口 ${APP_PORT} 正在监听"
        else
            echo "⚠️  端口 ${APP_PORT} 未监听"
        fi

        # 健康检查
        echo ""
        echo "健康检查:"
        if curl -f -s "http://localhost:${APP_PORT}/health" > /dev/null 2>&1; then
            echo "✅ 健康检查通过"
            curl -s "http://localhost:${APP_PORT}/health" | python3 -m json.tool
        else
            echo "❌ 健康检查失败"
        fi
    else
        echo "❌ 状态: 已停止 (PID 文件存在但进程不存在)"
        echo "📍 PID: ${PID} (已失效)"
    fi
else
    echo "❌ 状态: 已停止 (未找到 PID 文件)"

    # 检查是否有进程占用端口
    EXISTING_PID=$(lsof -ti:${APP_PORT} 2>/dev/null || true)
    if [ -n "${EXISTING_PID}" ]; then
        echo "⚠️  检测到端口 ${APP_PORT} 被占用 (PID: ${EXISTING_PID})"
    fi
fi

echo ""
echo "========================================="
echo "📂 部署路径: ${DEPLOY_PATH}"
echo "📝 日志文件: ${APP_LOG_FILE}"
echo "🌐 API 文档: http://localhost:${APP_PORT}/docs"
echo "========================================="

# 显示最近的日志
if [ -f "${APP_LOG_FILE}" ]; then
    echo ""
    echo "最近日志 (最后10行):"
    echo "----------------------------------------"
    tail -n 10 "${APP_LOG_FILE}"
fi
