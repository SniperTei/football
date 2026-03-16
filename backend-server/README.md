# Football Platform Backend

足球球队数据管理平台后端服务

## ⚠️ 安全警告

**重要：以下凭据仅供开发和测试使用，生产环境部署前必须修改！**

### 默认账户风险
- ❌ **禁止在生产环境使用默认账户**
- 默认管理员账户（admin/admin123）仅用于本地开发和测试
- 生产环境必须删除或修改默认账户密码

### 密钥和密码
- ❌ **禁止在生产环境使用示例密钥**
- JWT SECRET_KEY 必须使用强随机字符串（至少 32 位）
- 数据库密码必须使用强密码
- 建议使用密码生成器生成安全密钥

### 环境配置文件
- ✅ `.env.example` - 安全，可提交到版本控制
- ❌ `.env.dev`, `.env.test`, `.env.prod` - **禁止提交**
- 这些文件已添加到 `.gitignore`，请确保不要意外提交

### 生产环境检查清单
- [ ] 修改所有默认密码（管理员、数据库）
- [ ] 设置强随机 JWT SECRET_KEY
- [ ] 配置生产数据库（不使用 localhost）
- [ ] 启用 HTTPS
- [ ] 配置防火墙规则
- [ ] 设置日志监控
- [ ] 定期备份数据库

## 项目简介

一个功能完整的足球球队数据管理平台，支持球队管理、球员信息、比赛记录、数据统计等功能。提供 RESTful API 接口，采用 JWT 认证，支持管理员和普通用户两种角色。

## 技术栈

- **Python 3.10+**
- **FastAPI** - 现代化 Web 框架
- **SQLAlchemy** - ORM
- **PostgreSQL** - 数据库
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI 服务器
- **Alembic** - 数据库迁移

## 项目结构

```
backend-server/
├── app/
│   ├── api/              # API 路由
│   │   └── routes/       # 各模块路由
│   │       ├── auth.py   # 认证相关
│   │       ├── teams.py  # 球队管理
│   │       ├── players.py # 球员管理
│   │       ├── matches.py # 比赛管理
│   │       └── stats.py  # 数据统计
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置（支持多环境）
│   │   ├── database.py   # 数据库连接
│   │   └── security.py   # 安全相关（JWT、密码）
│   ├── models/           # 数据库模型
│   │   ├── user.py       # 用户模型
│   │   ├── team.py       # 球队模型
│   │   ├── player.py     # 球员模型
│   │   ├── match.py      # 比赛模型
│   │   └── match_player.py # 比赛球员统计
│   ├── repository/       # 数据访问层
│   │   ├── user.py       # 用户数据访问
│   │   ├── team.py       # 球队数据访问
│   │   ├── player.py     # 球员数据访问
│   │   ├── match.py      # 比赛数据访问
│   │   └── match_player.py # 球员统计数据访问
│   ├── schemas/          # Pydantic schemas
│   │   ├── auth.py       # 认证相关 schema
│   │   ├── team.py       # 球队 schema
│   │   ├── player.py     # 球员 schema
│   │   ├── match.py      # 比赛 schema
│   │   └── user.py       # 用户 schema
│   ├── service/          # 业务逻辑层
│   │   ├── auth_service.py
│   │   ├── team_service.py
│   │   ├── player_service.py
│   │   └── match_service.py
│   ├── utils/            # 工具函数
│   │   ├── response.py   # 统一响应格式
│   │   └── dependencies.py # 依赖注入
│   └── __init__.py
├── main.py               # 应用入口
├── init_db.py            # 数据库初始化脚本
├── requirements.txt      # 依赖包
├── .env.example          # 环境变量示例
├── .env.dev             # 开发环境配置
├── .env.test            # 测试环境配置
└── .env.prod            # 生产环境配置
```

## 快速开始

### 1. 安装依赖

```bash
cd backend-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量

根据运行环境复制对应的配置文件：

```bash
# 开发环境
cp .env.example .env.dev

# 测试环境
cp .env.example .env.test

# 生产环境
cp .env.example .env.prod
```

编辑 `.env.dev`（或其他环境的配置文件）：

```env
# 环境配置
ENV=dev

# 数据库配置
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/football_platform_dev

# JWT 配置
SECRET_KEY=dev-secret-key-change-in-production

# 应用配置
APP_NAME=Football Platform
DEBUG=True
```

**⚠️ 安全提示：**
- ❌ **生产环境必须修改 `SECRET_KEY` 为强随机字符串（至少 32 位）**
- ❌ **生产环境必须修改数据库密码**
- ✅ `.env.*` 文件已添加到 `.gitignore`，不会被提交到版本控制
- 💡 可以使用 `python -c "import secrets; print(secrets.token_urlsafe(32))"` 生成安全的 SECRET_KEY

### 3. 启动服务器

```bash
# 开发环境（使用 .env.dev）
export ENV=dev
uvicorn main:app --reload --port 8000

# 测试环境
export ENV=test
uvicorn main:app --reload --port 8000

# 生产环境
export ENV=prod
uvicorn main:app --port 8000
```

服务器将在 http://localhost:8000 启动

### 4. 初始化数据库

首次运行需要创建数据库表和初始管理员账户：

```bash
# 初始化数据库（创建表和管理员账户）
python init_db.py
```

这将创建：
- 所有数据库表
- 默认管理员账户：用户名 `admin`，密码 `admin123

**⚠️ 警告：这是开发和测试用的默认账户，生产环境必须修改或删除！**

### 5. 启动服务器

```bash
# 开发环境（使用 .env.dev）
export ENV=dev
uvicorn main:app --reload --port 8000

# 测试环境
export ENV=test
uvicorn main:app --reload --port 8000

# 生产环境
export ENV=prod
uvicorn main:app --port 8000
```

服务器将在 http://localhost:8000 启动

### 6. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 认证 `/api/auth`
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### 球队 `/api/teams`
- `GET /api/teams` - 获取所有球队（公开）
- `GET /api/teams/{id}` - 获取球队详情（公开）
- `POST /api/teams` - 创建球队（需登录）
- `PUT /api/teams/{id}` - 更新球队（需登录）
- `DELETE /api/teams/{id}` - 删除球队（需登录）

### 球员 `/api/players`
- `GET /api/players` - 获取所有球员（公开）
- `GET /api/players/{id}` - 获取球员详情（公开）
- `POST /api/players` - 创建球员（需登录）
- `PUT /api/players/{id}` - 更新球员（需登录）
- `DELETE /api/players/{id}` - 删除球员（需登录）

### 比赛 `/api/matches`
- `GET /api/matches` - 获取所有比赛（公开）
- `GET /api/matches/{id}` - 获取比赛详情（公开）
- `POST /api/matches` - 创建比赛（需登录）
- `PUT /api/matches/{id}` - 更新比赛（需登录）
- `DELETE /api/matches/{id}` - 删除比赛（需登录）

### 统计 `/api/stats`
- `GET /api/stats/teams/{id}` - 球队统计
- `GET /api/stats/top-scorers` - 射手榜（支持 team_id 和 limit 参数）
- `GET /api/stats/top-assists` - 助攻榜（支持 team_id 和 limit 参数）
- `GET /api/stats/top-attendance` - 出勤榜（支持 team_id 和 limit 参数）
- `GET /api/stats/head-to-head/{team1_id}/{team2_id}` - 两队历史战绩
- `GET /api/stats/league-table` - 积分榜

## 权限说明

### 用户角色

系统支持三种用户角色，每种角色有不同的权限：

1. **未登录用户**
   - 可以浏览所有公开数据（球队、球员、比赛、统计）
   - 无法进行任何修改操作

2. **普通用户**
   - 可以创建一个球队（创建后 `my_team_id` 会被设置）
   - 只能修改自己球队的数据（球员、比赛、统计）
   - 可以编辑比赛信息，但仅限主队是自己球队的比赛

3. **管理员**
   - `is_admin` 字段为 `true`
   - 可以创建多个球队（`my_team_id` 保持为 `null`）
   - 可以管理所有球队、球员和比赛数据
   - 拥有所有数据的修改和删除权限

### API 权限

- **公开访问**：所有 GET 请求都可以无需登录访问
- **需要登录**：所有 POST/PUT/DELETE 请求都需要在请求头中携带 JWT token
- **权限验证**：
  - 球队操作：管理员可以操作所有球队，普通用户只能操作自己的球队
  - 比赛操作：管理员可以操作所有比赛，普通用户只能操作主队是自己球队的比赛
  - 球员操作：管理员可以操作所有球员，普通用户只能操作自己球队的球员

### 使用 JWT Token

登录后获取 token，在后续请求中添加请求头：

```
Authorization: Bearer <your-token>
```

## 数据模型

### User（用户）
- id, username, email, hashed_password
- is_active, is_admin
- my_team_id - 关联的球队ID（管理员为 null）

### Team（球队）
- id, name, description, logo_url
- founded_year

### Player（球员）
- id, name, jersey_number, position
- birth_date, photo_url, team_id

### Match（比赛）
- id, home_team_id, away_team_id
- home_score, away_score
- match_date, match_venue, notes

### MatchPlayerStats（比赛球员统计）
- id, match_id, player_id
- goals, assists, minutes_played

## 项目架构

本项目采用分层架构，分为以下几层：

### 1. 路由层 (api/routes/)
- 处理 HTTP 请求和响应
- 参数验证
- 调用业务逻辑层

### 2. 业务逻辑层 (service/)
- 实现核心业务逻辑
- 权限验证
- 事务管理
- 调用数据访问层

### 3. 数据访问层 (repository/)
- 封装数据库操作
- 提供 CRUD 接口
- 处理 ORM 映射

### 4. 模型层 (models/)
- SQLAlchemy ORM 模型定义
- 数据库表结构

### 5. 数据验证层 (schemas/)
- Pydantic 模型定义
- 请求和响应数据验证

这种分层架构的优势：
- 职责分离，便于维护
- 易于测试
- 可扩展性强

## 开发建议

### 添加新功能
1. 在 `models/` 中定义数据库模型
2. 在 `schemas/` 中定义请求/响应模型
3. 在 `repository/` 中实现数据访问
4. 在 `service/` 中实现业务逻辑
5. 在 `api/routes/` 中添加路由

### 数据库迁移
使用 Alembic 进行数据库迁移：
```bash
# 生成迁移脚本
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 测试
```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html
```
