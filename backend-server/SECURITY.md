# 安全配置指南

## 环境变量配置

本项目使用环境变量来存储敏感信息，请勿将包含真实凭据的 `.env` 文件提交到代码仓库。

### 必需的环境变量

复制 `.env.example` 为 `.env.dev`（或对应环境的文件），并配置以下变量：

#### 后端 (backend-server)

```bash
# 数据库连接（必需）
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/football_platform_dev

# JWT 密钥（必需）
# 生产环境请使用强随机字符串，可用以下命令生成：
# openssl rand -hex 32
SECRET_KEY=your-secret-key-here

# 其他配置（有默认值）
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
APP_NAME=Football Platform
DEBUG=True
```

#### 前端 (frontend-pc)

```bash
# API 地址（必需）
VITE_API_BASE_URL=http://localhost:8000

# 应用标题（可选）
VITE_APP_TITLE=足球球队管理平台
```

## 安全建议

### 开发环境

1. **数据库密码**：不要使用默认的 `postgres` 密码
   ```bash
   # 在 PostgreSQL 中创建新用户
   CREATE USER football_user WITH PASSWORD 'your-secure-password';
   GRANT ALL PRIVILEGES ON DATABASE football_platform_dev TO football_user;
   ```

2. **JWT 密钥**：使用强随机字符串
   ```bash
   openssl rand -hex 32
   ```

3. **环境变量文件**：确保 `.env.*` 文件在 `.gitignore` 中
   - ✅ `.env.example` - 可以提交（仅包含示例）
   - ❌ `.env`, `.env.dev`, `.env.prod` 等 - 不能提交

### 生产环境

1. **使用环境变量**：不要在代码中硬编码敏感信息
2. **使用 HTTPS**：确保 API 通信加密
3. **定期更新密钥**：定期更换 JWT 密钥和数据库密码
4. **限制数据库权限**：使用专用数据库用户，不要使用 postgres 超级用户
5. **关闭 DEBUG 模式**：生产环境设置 `DEBUG=False`

## 检查清单

提交代码前，请确认：

- [ ] 没有提交 `.env` 文件（只有 `.env.example`）
- [ ] 没有硬编码的密码、API密钥或token
- [ ] `.gitignore` 文件配置正确
- [ ] 生产环境的密钥足够强
- [ ] 数据库使用专用用户（非postgres）
- [ ] DEBUG 模式在生产环境关闭
