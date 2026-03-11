#!/bin/bash
# 开发环境启动脚本
echo "🚀 Starting Backend in DEV mode..."

# 使用开发环境配置
cp .env.dev .env

echo "📁 Environment: .env.dev"
echo "🔗 Database: football_platform_dev"
echo "🌐 Port: 8021"
uvicorn main:app --reload --host 0.0.0.0 --port 8021
