#!/bin/bash
# 测试环境启动脚本
echo "🚀 Starting Backend in TEST mode..."

# 使用测试环境配置
cp .env.test .env

echo "📁 Environment: .env.test"
echo "🔗 Database: football_platform_test"
echo "🌐 Port: 8022"
uvicorn main:app --reload --host 0.0.0.0 --port 8022
