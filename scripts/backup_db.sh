#!/bin/bash
# 每周定时执行：pg_dump 备份 + Excel 报表导出
# Crontab: 0 2 * * 4 /opt/services/football/scripts/backup_db.sh >> /opt/backups/football_platform/backup.log 2>&1

CONTAINER_NAME="football_platform_db_prod"
BACKEND_CONTAINER="football_platform_backend_prod"
DB_NAME="football_platform"
DB_USER="postgres"
BACKUP_DIR="/opt/backups/football_platform"
RETAIN_DAYS=90
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 1. pg_dump 数据库备份
BACKUP_FILE="$BACKUP_DIR/backup_${DATE}.sql.gz"
docker exec $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

if [ $? -ne 0 ]; then
    echo "[$(date)] 数据库备份失败!"
    rm -f $BACKUP_FILE
    exit 1
fi
echo "[$(date)] 数据库备份成功: $BACKUP_FILE"

# 2. Excel 报表导出（在 backend 容器中执行 Python 脚本）
docker exec $BACKEND_CONTAINER python /app/scripts/export_excel.py "/app/backups/report_${DATE}.xlsx"

if [ $? -ne 0 ]; then
    echo "[$(date)] Excel 报表导出失败!"
else
    echo "[$(date)] Excel 报表导出成功: report_${DATE}.xlsx"
fi

# 3. 清理过期备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETAIN_DAYS -delete
find $BACKUP_DIR -name "report_*.xlsx" -mtime +$RETAIN_DAYS -delete
echo "[$(date)] 已清理 $RETAIN_DAYS 天前的旧文件"
