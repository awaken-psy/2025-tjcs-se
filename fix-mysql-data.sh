#!/bin/bash

# 修复 MySQL 数据持久化问题的脚本

echo "🔧 修复 MySQL 数据持久化问题..."

# 进入项目目录
cd /home/gingkoleaves/Documents/TJSE/timecapsule/backend

echo "1️⃣ 停止所有服务..."
sudo docker compose down -v

echo "2️⃣ 清理可能的权限问题目录..."
sudo rm -rf mysql-config mysql-logs redis-config

echo "3️⃣ 创建正确权限的目录..."
mkdir -p mysql-config mysql-logs redis-config
sudo chown -R $USER:$USER mysql-config mysql-logs redis-config

echo "4️⃣ 检查 Docker 卷..."
sudo docker volume ls | grep mysql || echo "没有找到现有的 MySQL 卷"

echo "5️⃣ 启动服务（仅 MySQL 和 Redis）..."
sudo docker compose up -d mysql redis

echo "6️⃣ 等待 MySQL 启动..."
sleep 10

echo "7️⃣ 检查 MySQL 健康状态..."
sudo docker logs timecapsule_mysql --tail 20

echo "8️⃣ 尝试连接 MySQL..."
sudo docker exec -it timecapsule_mysql mysql -u root -p"Markov@2025" -e "SHOW DATABASES;"

echo "9️⃣ 启动后端服务..."
sudo docker compose up -d backend

echo "✅ 修复完成！请检查服务状态："
sudo docker compose ps

echo "📝 如果需要重新初始化数据库表，请运行："
echo "sudo docker exec -it timecapsule_backend python -c \"from app.database.database import create_tables; create_tables()\""