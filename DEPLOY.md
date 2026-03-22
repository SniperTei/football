# 足球球队管理平台 - 测试环境部署指南

## 部署方式选择

### 方式一：Docker Compose（推荐）

适用于快速部署测试环境，所有服务在一个 Docker 网络中运行。

#### 前置要求

- Docker 和 Docker Compose 已安装
- 端口 80、8021、5433 未被占用

#### 部署步骤

1. **配置环境变量**

```bash
# 复制环境变量模板
cp .env.test.docker .env

# 编辑 .env 文件，修改敏感配置
vim .env
```

**必须修改的配置：**
- `POSTGRES_PASSWORD`: 数据库密码
- `SECRET_KEY`: JWT 加密密钥（使用随机字符串）

2. **启动服务**

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看服务状态
docker-compose ps
```

3. **访问应用**

- 前端: http://localhost
- 后端 API: http://localhost:8021
- API 文档: http://localhost:8021/docs

4. **常用命令**

```bash
# 停止服务
docker-compose stop

# 启动服务
docker-compose start

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 重新构建并启动
docker-compose up -d --build

# 查看后端日志
docker-compose logs -f backend

# 进入后端容器
docker-compose exec backend bash

# 执行数据库初始化
docker-compose exec backend python -c "from app.core.db_init import init_database; init_database()"
```

---

### 方式二：传统部署

分别部署后端和前端。

#### 后端部署

1. **安装 Python 依赖**

```bash
cd backend-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **配置环境变量**

```bash
# 复制配置文件
cp .env.test .env.local

# 编辑配置
vim .env.local
```

**配置内容：**
```env
ENV=test
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/football_platform_test
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

3. **准备数据库**

```bash
# 创建数据库
createdb football_platform_test

# 初始化数据库（创建表和初始数据）
python -c "from app.core.db_init import init_database; init_database()"
```

4. **启动后端服务**

```bash
# 开发模式（带热重载）
uvicorn main:app --host 0.0.0.0 --port 8021 --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8021 --workers 4
```

5. **配置 Supervisor（可选）**

创建 `/etc/supervisor/conf.d/football-platform.conf`:

```ini
[program:football-platform]
directory=/path/to/backend-server
command=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8021
autostart=true
autorestart=true
stderr_logfile=/var/log/football-platform.err.log
stdout_logfile=/var/log/football-platform.out.log
```

---

#### 前端部署

1. **构建前端**

```bash
cd frontend-pc

# 安装依赖
npm ci

# 使用测试环境配置构建
cp .env.test .env.production
npm run build
```

2. **使用 Nginx 部署**

安装 Nginx 后，创建配置文件 `/etc/nginx/sites-available/football-platform`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/frontend-pc/dist;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Vue Router history 模式
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://localhost:8021/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/football-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 数据库管理

### 导入初始数据

如果需要导入比赛数据：

```bash
cd backend-server

# 导入比赛数据
python import_match_data.py

# 或者使用 Docker
docker-compose exec backend python import_match_data.py
```

### 数据库备份

```bash
# 备份
docker-compose exec postgres pg_dump -U postgres football_platform_test > backup.sql

# 恢复
docker-compose exec -T postgres psql -U postgres football_platform_test < backup.sql
```

---

## 测试账号

初始化后默认创建两个测试账号：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin  | admin234 | 管理员 | 系统管理员 |
| cangming | cangming234 | 普通用户 | 关联球队：梅州客家队 |

---

## 健康检查

部署后验证服务状态：

```bash
# 检查后端健康状态
curl http://localhost:8021/health

# 检查前端是否可访问
curl http://localhost

# 测试 API
curl http://localhost:8021/api/teams
```

---

## 常见问题

### 1. 端口冲突

如果端口被占用，修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8080:80"  # 前端改为 8080
  - "8022:8000"  # 后端改为 8022
```

### 2. 数据库连接失败

检查数据库是否正常启动：
```bash
docker-compose logs postgres
docker-compose ps
```

### 3. 前端无法访问后端 API

检查 `frontend-pc/.env.production` 中的 API 地址是否正确。

### 4. CORS 错误

检查后端 `main.py` 中的 CORS 配置是否包含前端域名。

---

## 生产环境注意事项

⚠️ **测试环境配置仅供测试使用，生产环境请务必：**

1. 修改所有默认密码
2. 使用强随机密钥作为 `SECRET_KEY`
3. 配置 HTTPS（使用 Let's Encrypt）
4. 限制数据库访问权限
5. 配置防火墙规则
6. 定期备份数据
7. 监控日志和性能
8. 设置资源限制

---

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build

# 查看更新状态
docker-compose logs -f
```
