# Football Platform Backend

足球球队数据管理平台后端服务

## 技术栈

- **Python 3.10+**
- **FastAPI** - 现代化 Web 框架
- **SQLAlchemy** - ORM
- **PostgreSQL** - 数据库
- **Pydantic** - 数据验证

## 项目结构

```
backend-server/
├── app/
│   ├── api/              # API 路由
│   │   ├── routes/       # 各模块路由
│   │   └── dependencies.py  # 依赖注入
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置
│   │   ├── database.py   # 数据库连接
│   │   └── security.py   # 安全相关（JWT、密码）
│   ├── models/           # 数据库模型
│   ├── schemas/          # Pydantic schemas
│   └── __init__.py
├── main.py               # 应用入口
├── init_db.py            # 数据库初始化脚本
├── requirements.txt      # 依赖包
└── .env.example          # 环境变量示例
```

## 快速开始

### 1. 安装依赖

```bash
cd backend-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置数据库

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
DATABASE_URL=postgresql://username:password@localhost:5432/football_platform
SECRET_KEY=your-secret-key-here
```

### 3. 创建 PostgreSQL 数据库

```bash
psql -U postgres
CREATE DATABASE football_platform;
\q
```

### 4. 初始化数据库

```bash
python init_db.py
```

这将创建表结构并插入示例数据，包括：
- 管理员账户：`admin` / `admin123`
- 5 支球队
- 12 名球员
- 5 场比赛及统计

### 5. 启动服务器

```bash
uvicorn main:app --reload --port 8000
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
- `GET /api/stats/top-scorers` - 射手榜
- `GET /api/stats/top-assists` - 助攻榜
- `GET /api/stats/head-to-head/{team1_id}/{team2_id}` - 两队历史战绩
- `GET /api/stats/league-table` - 积分榜

## 权限说明

- **公开访问**：所有 GET 请求都可以无需登录访问
- **需要登录**：所有 POST/PUT/DELETE 请求都需要在请求头中携带 JWT token

### 使用 JWT Token

登录后获取 token，在后续请求中添加请求头：

```
Authorization: Bearer <your-token>
```

## 数据模型

### User（用户）
- id, username, email, hashed_password
- is_active, is_admin

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
