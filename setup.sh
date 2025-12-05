#!/bin/bash

echo "🚀 开始部署时光胶囊应用..."

# 确保挂载目录存在
UPLOAD_DIR="~/Downloads/timecapsule-uploads"
echo "📁 创建上传目录: $UPLOAD_DIR"
mkdir -p ~/Downloads/timecapsule-uploads

echo "🔨 构建Docker镜像..."
docker build --no-cache -t timecapsule-backend:123456 ./backend
docker build --no-cache -t timecapsule-frontend:123456 ./frontend

echo "🌐 创建Docker网络..."
docker network create timecapsule-net || true

echo "🛑 停止并删除旧容器..."
docker rm -f timecapsule-backend
docker rm -f timecapsule-frontend
 
echo "🚀 启动后端容器 (端口8000)..."
docker run -d \
--name timecapsule-backend \
-p 8000:8000 \
--network timecapsule-net \
-v ~/Downloads/timecapsule-uploads:/app/uploads \
--env-file ./backend/.env \
timecapsule-backend:123456

echo "🌐 启动前端容器 (端口80)..."
docker run -d \
--name timecapsule-frontend \
-p 80:80 \
--network timecapsule-net \
timecapsule-frontend:123456

echo ""
echo "✅ 部署完成!"
echo "=========================================="
echo "📱 前端访问: http://localhost"
echo "🔧 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo "📁 上传目录: ~/Downloads/timecapsule-uploads"
echo "=========================================="
echo ""
echo "📊 容器状态:"
docker ps --filter "name=timecapsule" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "💡 查看日志:"
echo "   后端: docker logs -f timecapsule-backend"
echo "   前端: docker logs -f timecapsule-frontend"
