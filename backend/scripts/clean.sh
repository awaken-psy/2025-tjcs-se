#!/bin/bash
# stop.sh - 停止但不删除

echo "⏸️  停止时光胶囊应用..."

# 停止前端容器
docker stop timecapsule-frontend 2>/dev/null && echo "前端容器已停止"

# 停止后端服务（保留数据）
cd ./backend
docker compose stop
cd ../

echo "✅ 应用已停止。要重新启动，请运行："
echo "   cd ./backend && docker compose start"
echo "   docker start timecapsule-frontend"