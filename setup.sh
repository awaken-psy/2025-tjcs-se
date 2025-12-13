#!/bin/bash

# 检查是否有 Docker 权限
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker 权限不足，尝试使用 sudo..."
    DOCKER_CMD="sudo docker"
    DOCKER_COMPOSE_CMD="sudo docker compose"
else
    DOCKER_CMD="docker"
    DOCKER_COMPOSE_CMD="docker compose"
fi

echo "🚀 开始部署时光胶囊应用..."

# 确保挂载目录存在
UPLOAD_DIR="./backend/uploads"
echo "📁 创建上传目录: $UPLOAD_DIR"
mkdir -p ./backend/uploads

echo "🛑 停止并清理旧的容器和服务..."
cd ./backend
$DOCKER_COMPOSE_CMD down

echo "🔨 使用 Docker Compose 构建并启动服务..."
$DOCKER_COMPOSE_CMD up -d --build

echo "🔍 检查服务状态..."
$DOCKER_COMPOSE_CMD ps

# 如果容器没有正常启动，显示详细日志
if ! $DOCKER_COMPOSE_CMD ps | grep -q "Up"; then
    echo "❌ 检测到容器启动问题，显示日志："
    echo "--- MySQL 日志 ---"
    $DOCKER_COMPOSE_CMD logs mysql | tail -20
    echo "--- Backend 日志 ---"
    $DOCKER_COMPOSE_CMD logs backend | tail -20
fi

echo "🚀 启动前端容器 (端口80)..."
cd ../
$DOCKER_CMD build --no-cache -t timecapsule-frontend:123456 ./frontend
$DOCKER_CMD rm -f timecapsule-frontend 2>/dev/null || true
$DOCKER_CMD run -d \
--name timecapsule-frontend \
-p 80:80 \
--network backend_default \
timecapsule-frontend:123456

echo "⏳ 等待服务启动..."
sleep 5



echo ""
echo "✅ 部署完成!"
echo "=========================================="
echo "📱 前端访问: http://localhost"
echo "🔧 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo "📁 上传目录: ./backend/uploads"
echo "🗄️  MySQL: localhost:3307"
echo "🔴 Redis: localhost:6379"
echo "=========================================="
echo ""
echo "📊 容器状态:"
$DOCKER_CMD ps --filter "name=timecapsule" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "💡 查看日志:"
echo "   后端: $DOCKER_COMPOSE_CMD -f ./backend/docker-compose.yml logs -f backend"
echo "   MySQL: $DOCKER_COMPOSE_CMD -f ./backend/docker-compose.yml logs -f mysql"
echo "   Redis: $DOCKER_COMPOSE_CMD -f ./backend/docker-compose.yml logs -f redis"
echo "   前端: $DOCKER_CMD logs -f timecapsule-frontend"
