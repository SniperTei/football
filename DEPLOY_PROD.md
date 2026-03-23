# 云服务器部署指南（生产环境）

## 📋 部署前准备

### 1. 服务器环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 开放端口：80（前端）、8021（后端）、5433（数据库，可选）

### 2. 生成安全凭证

**生成 SECRET_KEY**：
```bash
openssl rand -hex 32
```

**生成数据库密码**：
```bash
openssl rand -hex 16
```

## 🚀 部署步骤

### 步骤 1：上传代码到服务器

```bash
# 在服务器上克隆代码（或使用 scp/sftp 上传）
git clone <your-repository-url> football_platform
cd football_platform
```

### 步骤 2：配置环境变量

```bash
# 复制环境变量示例文件
cp .env.prod.example .env.prod

# 编辑环境变量文件
nano .env.prod
```

**重要：必须修改以下变量**：
```bash
POSTGRES_PASSWORD=<生成的数据库密码>
SECRET_KEY=<生成的 SECRET_KEY>
```

### 步骤 3：构建并启动服务

```bash
# 使用生产环境配置启动
docker-compose -f docker-compose.prod.yml up -d --build
```

### 步骤 4：初始化数据库

```bash
# 等待数据库启动（约 10 秒）
sleep 10

# 进入后端容器
docker exec -it football_platform_backend_prod bash

# 初始化数据库（创建表和管理员账户）
python init_db.py

# 退出容器
exit
```

### 步骤 5：验证部署

```bash
# 检查容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看后端日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 测试后端 API
curl http://localhost:8021/health

# 测试前端
curl http://localhost/
```

## 📊 访问应用

- **前端**：http://your-server-ip
- **后端 API**：http://your-server-ip:8021
- **API 文档**：http://your-server-ip:8021/docs

**默认管理员账户**：
- 用户名：`admin`
- 密码：`admin123`

⚠️ **部署后请立即修改默认密码！**

## 🔧 常用运维命令

### 查看服务状态
```bash
docker-compose -f docker-compose.prod.yml ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看后端日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 查看前端日志
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### 重启服务
```bash
# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 重启单个服务
docker-compose -f docker-compose.prod.yml restart backend
```

### 停止服务
```bash
docker-compose -f docker-compose.prod.yml down
```

### 更新代码后重新部署
```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build
```

### 进入容器调试
```bash
# 进入后端容器
docker exec -it football_platform_backend_prod bash

# 进入数据库容器
docker exec -it football_platform_db_prod psql -U postgres -d football_platform
```

## 🔒 安全建议

### 1. 修改默认密码
```bash
# 进入后端容器
docker exec -it football_platform_backend_prod bash

# 运行修改密码脚本（需要先创建）
python change_admin_password.py
```

### 2. 配置防火墙
```bash
# 只开放必要端口
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

### 3. 配置 HTTPS（推荐）
使用 Let's Encrypt + Nginx：

```bash
# 安装 certbot
apt install certbot python3-certbot-nginx

# 获取 SSL 证书
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

### 4. 定期备份数据库
```bash
# 创建备份脚本
cat > backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/football_platform"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker exec football_platform_db_prod pg_dump -U postgres football_platform > $BACKUP_DIR/backup_$DATE.sql

# 保留最近 7 天的备份
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x backup_db.sh

# 添加到 crontab（每天凌晨 2 点备份）
crontab -e
# 添加：0 2 * * * /path/to/backup_db.sh
```

## 🐛 故障排查

### 问题 1：容器启动失败

**检查日志**：
```bash
docker-compose -f docker-compose.prod.yml logs backend
```

**常见原因**：
- 端口被占用：修改 docker-compose.prod.yml 中的端口映射
- 环境变量未设置：确认 .env.prod 文件存在且配置正确

### 问题 2：数据库连接失败

**检查数据库健康状态**：
```bash
docker exec football_platform_db_prod pg_isready -U postgres
```

**检查后端环境变量**：
```bash
docker exec football_platform_backend_prod env | grep DATABASE_URL
```

### 问题 3：前端无法访问后端

**检查前端 Nginx 配置**：
```bash
docker exec football_platform_frontend_prod cat /etc/nginx/conf.d/default.conf
```

**检查后端健康**：
```bash
curl http://localhost:8021/health
```

### 问题 4：容器内存不足

**查看资源使用**：
```bash
docker stats
```

**限制容器资源**（在 docker-compose.prod.yml 中添加）：
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

## 📈 性能优化

### 1. 数据库优化

编辑 `postgresql.conf`（需要挂载自定义配置）：
```conf
# 连接数
max_connections = 100

# 内存配置
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB

# 查询优化
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 2. 后端优化

- 使用 Gunicorn 替代 Uvicorn（多进程）
```bash
pip install gunicorn
```

修改启动命令：
```yaml
command: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 3. 启用 Nginx 缓存

在前端 Nginx 配置中添加：
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_pass http://backend:8021;
}
```

## 📞 技术支持

如遇问题，请：
1. 查看日志：`docker-compose -f docker-compose.prod.yml logs`
2. 检查配置：确认 .env.prod 文件正确
3. 参考文档：查看 README.md 和 DEPLOY.md
4. 提交 Issue：在 GitHub 仓库提交问题
