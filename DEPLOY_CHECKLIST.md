# 测试环境部署检查清单

## 部署前检查

- [ ] 已拉取最新代码 `git pull`
- [ ] Docker 和 Docker Compose 已安装
- [ ] 端口 80、8021、5433 未被占用
- [ ] 已修改 `.env` 中的敏感配置（密码、密钥）

## 快速部署（Docker Compose）

```bash
# 1. 配置环境变量
cp .env.test.docker .env
vim .env  # 修改 POSTGRES_PASSWORD 和 SECRET_KEY

# 2. 启动服务
docker-compose up -d

# 3. 查看状态
docker-compose ps
docker-compose logs -f
```

## 验证部署

- [ ] 访问前端 http://localhost 正常显示
- [ ] 访问 API 文档 http://localhost:8021/docs 正常
- [ ] 健康检查 http://localhost:8021/health 返回 healthy
- [ ] 测试注册功能正常
- [ ] 测试登录功能正常（admin/admin234 或 cangming/cangming234）
- [ ] 测试球队列表加载正常

## 导入比赛数据（可选）

如果需要导入2024和2025年的比赛数据：

```bash
# 导入比赛数据（60个球队、34个球员、93场比赛）
docker-compose exec backend python import_match_data.py

# 验证数据导入成功
curl http://localhost:8021/api/teams
curl http://localhost:8021/api/matches
```

导入后的数据：
- 60个球队
- 34个球员（全部属于梅州客家队）
- 93场比赛（2024和2025年）
- 765条球员统计数据

## 常用命令

```bash
# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 重启服务
docker-compose restart

# 停止服务
docker-compose stop

# 删除容器（保留数据）
docker-compose down

# 完全清理（包括数据）
docker-compose down -v

# 进入后端容器
docker-compose exec backend bash

# 重新构建
docker-compose up -d --build
```

## 故障排查

### 端口冲突
```bash
# 查看端口占用
lsof -i :80
lsof -i :8021
lsof -i :5433
```

### 数据库问题
```bash
# 查看数据库日志
docker-compose logs postgres

# 进入数据库
docker-compose exec postgres psql -U postgres -d football_platform_test
```

### 后端问题
```bash
# 进入后端容器调试
docker-compose exec backend bash

# 手动初始化数据库
docker-compose exec backend python -c "from app.core.db_init import init_database; init_database()"
```

## 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin234 | 管理员 |
| cangming | cangming234 | 普通用户 |

## 清理环境

```bash
# 停止并删除所有容器和网络
docker-compose down

# 删除数据卷（⚠️ 会删除数据库数据）
docker-compose down -v

# 删除构建缓存
docker system prune -a
```
