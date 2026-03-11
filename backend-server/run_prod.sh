#!/bin/bash
# 生产环境启动脚本
echo "🚀 Starting Backend in PROD mode..."

# 使用生产环境配置
cp .env.prod .env

echo "📁 Environment: .env.prod"
echo "🔗 Database: football_platform_prod"
echo "🌐 Port: 8023"
echo "⚠️  Production mode - no auto-reload"
uvicorn main:app --host 0.0.0.0 --port 8023 --workers 4
