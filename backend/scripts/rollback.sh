#!/bin/bash
###############################################################################
# 回滚脚本 - 恢复到上一个版本
###############################################################################

set -e

DEPLOY_ENV="${DEPLOY_ENV:-staging}"
APP_NAME="timecapsule"

if [ "$DEPLOY_ENV" = "production" ]; then
    DEPLOY_PATH="${DEPLOY_PATH:-/var/www/timecapsule/production}"
else
    DEPLOY_PATH="${DEPLOY_PATH:-/var/www/timecapsule/staging}"
fi

BACKUP_DIR="${DEPLOY_PATH}/backup"

echo "🔄 开始回滚 ${APP_NAME} (${DEPLOY_ENV})..."

# 检查备份目录
if [ ! -d "${BACKUP_DIR}" ]; then
    echo "❌ 错误: 备份目录不存在"
    exit 1
fi

# 列出可用的备份
echo ""
echo "可用的备份:"
echo "----------------------------------------"
ls -lh "${BACKUP_DIR}"/backup_*.tar.gz 2>/dev/null | nl || {
    echo "❌ 错误: 没有可用的备份"
    exit 1
}
echo "----------------------------------------"

# 获取最新的备份
LATEST_BACKUP=$(ls -t "${BACKUP_DIR}"/backup_*.tar.gz 2>/dev/null | head -n 1)

if [ -z "${LATEST_BACKUP}" ]; then
    echo "❌ 错误: 没有找到备份文件"
    exit 1
fi

echo ""
echo "将回滚到: $(basename ${LATEST_BACKUP})"
read -p "确认回滚? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ 回滚已取消"
    exit 0
fi

# 停止服务
echo ""
echo "停止当前服务..."
bash "$(dirname "$0")/stop.sh"

# 备份当前版本（作为安全措施）
if [ -d "${DEPLOY_PATH}/app" ]; then
    echo "备份当前版本..."
    SAFETY_BACKUP="backup_before_rollback_$(date +'%Y%m%d_%H%M%S').tar.gz"
    tar -czf "${BACKUP_DIR}/${SAFETY_BACKUP}" \
        -C "${DEPLOY_PATH}" app environment.yml 2>/dev/null || true
fi

# 删除当前部署
echo "删除当前部署..."
rm -rf "${DEPLOY_PATH}/app"
rm -f "${DEPLOY_PATH}/environment.yml"

# 恢复备份
echo "恢复备份..."
tar -xzf "${LATEST_BACKUP}" -C "${DEPLOY_PATH}"

echo "✅ 回滚完成"
echo ""
echo "请手动重新启动服务或运行部署脚本"
echo "bash scripts/deploy.sh"
