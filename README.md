# 足球球队数据管理平台

一个完整的足球球队数据管理系统，采用前后端分离架构，支持球队、球员、比赛信息的管理和多维度数据统计分析。

## 📋 目录

- [项目概览](#项目概览)
- [技术栈](#技术栈)
- [系统架构](#系统架构)
- [业务模块](#业务模块)
- [API 接口](#api-接口)
- [数据库设计](#数据库设计)
- [快速开始](#快速开始)
- [开发指南](#开发指南)
- [配置说明](#配置说明)
- [项目结构](#项目结构)
- [路由结构](#路由结构)
- [权限控制](#权限控制)
- [数据导入](#数据导入)
- [部署指南](#部署指南)

---

## 项目概览

### 核心功能

本平台提供足球数据的全方位管理：

- **球队管理**：球队信息维护（名称、Logo、简介、成立年份）
- **球员管理**：球员档案管理（姓名、号码、位置、所属球队）
- **比赛管理**：比赛记录管理（主客场、比分、场地、日期、状态）
- **比赛统计**：球员比赛表现数据（进球、助攻等详细统计）
- **数据统计分析**：
  - 🔥 射手榜：按进球数排名（支持按球队、年份、月份筛选）
  - 🎯 助攻榜：按助攻数排名（支持多种筛选条件）
  - 🏆 积分榜：球队积分排名（胜平负统计）
  - 📊 历史战绩：查询两队之间的对战记录和胜率分析

### 权限体系

- **公开访问**：所有数据查看功能无需登录即可访问
- **登录用户**：可以创建、编辑、删除数据
- **管理员**：拥有完整的系统管理权限

---

## 技术栈

### 后端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| **Python** | 3.10+ | 主要编程语言 |
| **FastAPI** | 0.115.0 | 现代化、高性能的 Web 框架，支持异步 |
| **SQLAlchemy** | 2.0.36 | Python SQL 工具包和 ORM 框架 |
| **PostgreSQL** | 12+ | 关系型数据库，通过 psycopg3 驱动 |
| **Pydantic** | 2.11.2+ | 数据验证和序列化，使用 Python 类型注解 |
| **JWT** | python-jose | 基于 JSON Web Token 的用户认证 |
| **Alembic** | 1.14.0 | 数据库迁移工具 |
| **Uvicorn** | latest | ASGI 服务器，用于运行 FastAPI |
| **pandas** | latest | 数据处理，用于 Excel 数据导入 |
| **openpyxl** | latest | Excel 文件读写支持 |

### 前端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| **Vue** | 3.4.0 | 渐进式 JavaScript 框架，使用 Composition API |
| **TypeScript** | 5.6.0 | JavaScript 的超集，提供类型安全 |
| **Vite** | 6.0.0 | 下一代前端构建工具，极速冷启动 |
| **Element Plus** | 2.8.0 | 基于 Vue 3 的组件库 |
| **Pinia** | 2.2.0 | Vue 官方推荐的状态管理库 |
| **Vue Router** | 4.4.0 | Vue.js 官方路由管理器 |
| **Axios** | 1.7.0 | 基于 Promise 的 HTTP 客户端 |
| **ECharts** | 6.0.0 | 强大的数据可视化图表库 |
| **@vueuse** | latest | Vue Composition API 工具集 |
| **unplugin-auto-import** | latest | 自动导入 Vue API |
| **unplugin-vue-components** | latest | 自动导入 Vue 组件 |

### 开发工具

- **环境管理**：支持 dev/test/prod 三种环境配置
- **代码规范**：TypeScript 类型检查 + ESLint（可配置）
- **测试框架**：pytest + pytest-asyncio
- **API 文档**：FastAPI 自动生成 Swagger/OpenAPI 文档
- **数据导入**：支持 Excel 批量导入历史数据

---

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户界面                              │
│                    (Vue 3 + Element Plus)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/Axios
┌────────────────────────▼────────────────────────────────────┐
│                      API Gateway                             │
│                        (FastAPI)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
┌────────▼────┐  ┌───────▼──────┐  ┌───▼────────┐
│   Auth      │  │   Service    │  │  Stats     │
│   Module    │  │   Layer      │  │  Service   │
└─────────────┘  └───────┬──────┘  └────────────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
     ┌────────▼──┐ ┌────▼─────┐ ┌─▼────────┐
     │ Repository│ │ Models   │ │ Schemas  │
     │   Layer   │ │  (ORM)   │ │(Pydantic)│
     └─────┬─────┘ └────┬─────┘ └──────────┘
           │            │
           └──────┬─────┘
                  │
         ┌────────▼─────────┐
         │   PostgreSQL     │
         │    Database      │
         └──────────────────┘
```

### 后端分层架构

后端采用清晰的分层架构设计：

```
app/
├── api/              # API 路由层 - 处理 HTTP 请求/响应
│   ├── deps.py       # 依赖注入（如数据库会话、认证）
│   ├── auth.py       # 认证相关路由
│   ├── teams.py      # 球队路由
│   ├── players.py    # 球员路由
│   ├── matches.py    # 比赛路由
│   ├── match_players.py # 比赛统计路由
│   └── stats.py      # 统计查询路由
│
├── service/          # 业务逻辑层 - 核心业务处理
│   ├── auth_service.py   # 认证业务逻辑
│   ├── team_service.py   # 球队业务逻辑
│   ├── player_service.py # 球员业务逻辑
│   └── match_service.py  # 比赛业务逻辑
│
├── repository/       # 数据访问层 - 数据库操作抽象
│   ├── base.py       # 基础 repository
│   ├── user.py       # 用户数据访问
│   ├── team.py       # 球队数据访问
│   ├── player.py     # 球员数据访问
│   └── match.py      # 比赛数据访问
│
├── models/           # 数据模型层 - SQLAlchemy ORM 模型
│   ├── user.py       # 用户模型
│   ├── team.py       # 球队模型
│   ├── player.py     # 球员模型
│   ├── match.py      # 比赛模型
│   └── match_player.py # 比赛统计模型
│
├── schemas/          # 数据验证层 - Pydantic schemas
│   ├── user.py       # 用户数据验证
│   ├── team.py       # 球队数据验证
│   ├── player.py     # 球员数据验证
│   ├── match.py      # 比赛数据验证
│   └── match_player.py # 比赛统计数据验证
│
├── core/             # 核心配置
│   ├── config.py     # 配置管理
│   ├── security.py   # 安全相关（JWT、密码哈希）
│   └── deps.py       # 全局依赖
│
└── utils/            # 工具函数
    └── ...
```

### 前端架构

前端采用 Vue 3 Composition API + Pinia 状态管理：

```
src/
├── api/              # API 接口封装层
│   ├── index.ts      # Axios 实例配置
│   ├── auth.ts       # 认证接口
│   ├── teams.ts      # 球队接口
│   ├── players.ts    # 球员接口
│   ├── matches.ts    # 比赛接口
│   └── stats.ts      # 统计接口
│
├── stores/           # Pinia 状态管理
│   ├── user.ts       # 用户状态（登录信息、Token）
│   ├── teams.ts      # 球队状态
│   └── matches.ts    # 比赛状态
│
├── router/           # 路由配置
│   └── index.ts      # 路由定义和守卫
│
├── views/            # 页面组件
│   ├── Login.vue     # 登录页
│   ├── Dashboard.vue # 首页/数据概览
│   ├── Teams.vue     # 球队列表
│   ├── Players.vue   # 球员列表
│   ├── Matches.vue   # 比赛列表
│   ├── Stats.vue     # 数据统计
│   └── admin/        # 管理页面
│       ├── TeamManagement.vue
│       ├── PlayerManagement.vue
│       └── MatchManagement.vue
│
├── components/       # 公共组件
│   ├── layouts/      # 布局组件
│   └── common/       # 通用组件
│
└── types/            # TypeScript 类型定义
    └── ...
```

### 数据流设计

```
用户操作
    ↓
Vue 组件触发 Action
    ↓
Pinia Store 调用 API
    ↓
Axios 发送 HTTP 请求
    ↓
FastAPI 接收请求
    ↓
Service 层处理业务逻辑
    ↓
Repository 层数据库操作
    ↓
PostgreSQL 执行 SQL
    ↓
返回数据逐层向上
    ↓
Vue 组件更新视图
```

---

## 业务模块

### 1. 用户认证模块

**功能**：用户注册、登录、权限验证

**核心特性**：
- JWT Token 认证机制
- 密码哈希存储（bcrypt）
- Token 自动刷新
- 前端路由守卫保护

**数据模型**：
- username: 用户名（唯一）
- password: 加密密码
- email: 邮箱
- role: 角色（admin/user）

### 2. 球队管理模块

**功能**：球队信息的增删改查

**数据字段**：
- name: 球队名称
- logo: 球队 Logo URL
- description: 球队简介
- founded_year: 成立年份

**业务规则**：
- 球队名称唯一性校验
- 删除球队前检查是否有关联球员或比赛
- 支持球队 Logo 图片上传

### 3. 球员管理模块

**功能**：球员档案管理

**数据字段**：
- name: 球员姓名
- number: 球衣号码
- position: 位置（前锋/中场/后卫/门将）
- team_id: 所属球队（外键）

**业务规则**：
- 同一球队内球衣号码唯一
- 删除球员前检查是否有比赛统计记录
- 支持按球队、位置筛选

### 4. 比赛管理模块

**功能**：比赛记录管理

**数据字段**：
- home_team_id: 主队（外键）
- away_team_id: 客队（外键）
- home_score: 主队得分
- away_score: 客队得分
- match_date: 比赛日期
- venue: 比赛场地
- match_type: 比赛类型（联赛/杯赛/友谊赛）
- status: 比赛状态（进行中/已结束）

**业务规则**：
- 主客队不能相同
- 比赛日期不能晚于当前时间（对于已结束比赛）
- 支持比赛状态更新
- 自动计算积分

### 5. 比赛统计模块

**功能**：记录球员在单场比赛中的表现

**数据字段**：
- match_id: 比赛ID（外键）
- player_id: 球员ID（外键）
- team_id: 所属球队ID（外键）
- goals: 进球数
- assists: 助攻数
- yellow_cards: 黄牌数
- red_cards: 红牌数

**业务规则**：
- 同一球员在同一场比赛只有一条统计记录
- 球员必须属于参赛球队之一
- 支持批量导入统计数据

### 6. 数据统计分析模块

**功能**：多维度数据统计和查询

**统计类型**：

#### 6.1 射手榜
- 按总进球数排名
- 筛选条件：球队、年份、月份、比赛类型
- 显示：排名、球员名、球队、进球数、出场次数

#### 6.2 助攻榜
- 按总助攻数排名
- 筛选条件：球队、年份、月份、比赛类型
- 显示：排名、球员名、球队、助攻数、出场次数

#### 6.3 积分榜
- 按积分排名
- 计分规则：胜3分、平1分、负0分
- 显示：排名、球队、场次、胜、平、负、进球、失球、净胜球、积分

#### 6.4 历史战绩
- 查询两队之间的对战历史
- 显示：总场次、胜、平、负、进球数、胜率
- 支持按比赛类型筛选

---

## API 接口

### 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Bearer Token (JWT)
- **响应格式**: JSON
- **API 文档**: `http://localhost:8000/docs` (Swagger UI)

### 统一响应格式

**成功响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误响应**：
```json
{
  "detail": "错误信息描述"
}
```

### 主要接口列表

#### 认证接口 `/api/auth`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/auth/register` | 用户注册 | 公开 |
| POST | `/auth/login` | 用户登录 | 公开 |
| GET | `/auth/me` | 获取当前用户信息 | 需登录 |

#### 球队接口 `/api/teams`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/teams/` | 获取球队列表 | 公开 |
| GET | `/teams/{id}` | 获取球队详情 | 公开 |
| POST | `/teams/` | 创建球队 | 需登录 |
| PUT | `/teams/{id}` | 更新球队 | 需登录 |
| DELETE | `/teams/{id}` | 删除球队 | 需登录 |

#### 球员接口 `/api/players`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/players/` | 获取球员列表 | 公开 |
| GET | `/players/{id}` | 获取球员详情 | 公开 |
| POST | `/players/` | 创建球员 | 需登录 |
| PUT | `/players/{id}` | 更新球员 | 需登录 |
| DELETE | `/players/{id}` | 删除球员 | 需登录 |

#### 比赛接口 `/api/matches`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/matches/` | 获取比赛列表 | 公开 |
| GET | `/matches/{id}` | 获取比赛详情 | 公开 |
| POST | `/matches/` | 创建比赛 | 需登录 |
| PUT | `/matches/{id}` | 更新比赛 | 需登录 |
| DELETE | `/matches/{id}` | 删除比赛 | 需登录 |

#### 比赛统计接口 `/api/match_players`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/match_players/` | 获取比赛统计列表 | 公开 |
| GET | `/match_players/{id}` | 获取统计详情 | 公开 |
| POST | `/match_players/` | 创建比赛统计 | 需登录 |
| PUT | `/match_players/{id}` | 更新比赛统计 | 需登录 |
| DELETE | `/match_players/{id}` | 删除比赛统计 | 需登录 |

#### 统计接口 `/api/stats`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/stats/top_scorers` | 射手榜 | 公开 |
| GET | `/stats/top_assists` | 助攻榜 | 公开 |
| GET | `/stats/standings` | 积分榜 | 公开 |
| GET | `/stats/head_to_head` | 历史战绩对比 | 公开 |
| GET | `/stats/team_stats/{id}` | 球队详细统计 | 公开 |

### 请求示例

#### 登录
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

#### 获取射手榜（带筛选）
```bash
curl -X GET "http://localhost:8000/api/stats/top_scorers?team_id=1&year=2024" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 创建球队
```bash
curl -X POST "http://localhost:8000/api/teams/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "曼联",
    "logo": "https://example.com/logo.png",
    "description": "英格兰足球俱乐部",
    "founded_year": 1878
  }'
```

---

## 数据库设计

### ER 图

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    User     │         │    Team     │         │   Player    │
├─────────────┤         ├─────────────┤         ├─────────────┤
│ id          │         │ id          │         │ id          │
│ username    │         │ name        │         │ name        │
│ password    │         │ logo        │         │ number      │
│ email       │         │ description │         │ position    │
│ role        │         │ founded_year│         │ team_id     │
│ created_at  │         │ created_at  │         │ created_at  │
└─────────────┘         └──────┬──────┘         └──────┬──────┘
                               │                       │
                               │    ┌─────────────────┘
                               │    │
                               ▼    ▼
                         ┌─────────────┐         ┌─────────────────┐
                         │   Match     │         │  MatchPlayer    │
                         ├─────────────┤         ├─────────────────┤
                         │ id          │         │ id              │
                         │ home_team   │────────▶│ match_id        │
                         │ away_team   │────────▶│ player_id       │
                         │ home_score  │         │ team_id         │
                         │ away_score  │         │ goals           │
                         │ match_date  │         │ assists         │
                         │ venue       │         │ yellow_cards    │
                         │ match_type  │         │ red_cards       │
                         │ status      │         │ created_at      │
                         │ created_at  │         └─────────────────┘
                         └─────────────┘
```

### 主要表结构

#### teams（球队表）
```sql
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    logo VARCHAR(255),
    description TEXT,
    founded_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### players（球员表）
```sql
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    number INTEGER,
    position VARCHAR(50),
    team_id INTEGER REFERENCES teams(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### matches（比赛表）
```sql
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    match_date TIMESTAMP NOT NULL,
    venue VARCHAR(100),
    match_type VARCHAR(50) DEFAULT 'league',
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### match_players（比赛统计表）
```sql
CREATE TABLE match_players (
    id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(id) ON DELETE CASCADE,
    player_id INTEGER REFERENCES players(id),
    team_id INTEGER REFERENCES teams(id),
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(match_id, player_id)
);
```

---

## 快速开始

### 环境要求

- **Python**: 3.10+
- **Node.js**: 18+
- **PostgreSQL**: 12+
- **Git**: 最新版本

### 1. 克隆项目

```bash
git clone <repository-url>
cd football_platform
```

### 2. 数据库设置

```bash
# 连接到 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE football_platform;

# 创建用户（可选）
CREATE USER football_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE football_platform TO football_user;

# 退出
\q
```

### 3. 后端设置

```bash
# 进入后端目录
cd backend-server

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量配置文件
cp .env.example .env

# 编辑 .env 文件，配置数据库连接
# DATABASE_URL=postgresql://username:password@localhost:5432/football_platform

# 初始化数据库（创建表并插入示例数据）
python init_db.py

# 启动后端服务
uvicorn main:app --reload --port 8000
```

后端将在 `http://localhost:8000` 启动

API 文档：`http://localhost:8000/docs`

### 4. 前端设置

```bash
# 打开新终端，进入前端目录
cd frontend-pc

# 安装依赖
npm install
# 或使用 bun（更快）
bun install

# 复制环境变量配置文件
cp .env.example .env

# 编辑 .env 文件，配置 API 地址
# VITE_API_BASE_URL=http://localhost:8000/api

# 启动开发服务器
npm run dev
# 或
bun run dev
```

前端将在 `http://localhost:5173` 启动

### 5. 访问应用

打开浏览器访问：`http://localhost:5173`

### 6. 默认账户

```
用户名: admin
密码: admin123
```

---

## 开发指南

### 后端开发

#### 添加新的 API 端点

1. 在 `app/schemas/` 中定义数据模型（Pydantic）
2. 在 `app/models/` 中定义数据库模型（SQLAlchemy）
3. 在 `app/repository/` 中创建数据访问层
4. 在 `app/service/` 中实现业务逻辑
5. 在 `app/api/` 中创建路由

示例：
```python
# app/api/teams.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.team import TeamCreate, TeamResponse
from app.service.team_service import TeamService

router = APIRouter()

@router.post("/", response_model=TeamResponse)
def create_team(
    team: TeamCreate,
    db: Session = Depends(get_db)
):
    service = TeamService(db)
    return service.create_team(team)
```

#### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_teams.py

# 查看覆盖率
pytest --cov=app tests/
```

### 前端开发

#### 添加新页面

1. 在 `src/views/` 中创建 Vue 组件
2. 在 `src/router/index.ts` 中添加路由
3. 在 `src/api/` 中添加 API 接口（如需要）

示例：
```typescript
// src/router/index.ts
{
  path: '/new-page',
  name: 'NewPage',
  component: () => import('@/views/NewPage.vue'),
  meta: { requiresAuth: true }
}
```

#### 组件开发规范

- 使用 `<script setup lang="ts">` 语法
- 使用 Composition API
- 定义清晰的 Props 和 Emits 类型
- 使用 Pinia 管理共享状态

---

## 配置说明

### 后端配置 (.env)

```bash
# 应用配置
APP_NAME="Football Platform"
APP_VERSION="1.0.0"
DEBUG=True

# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/football_platform

# JWT 配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 配置
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

### 前端配置 (.env)

```bash
# API 地址
VITE_API_BASE_URL=http://localhost:8000/api

# 应用标题
VITE_APP_TITLE=足球数据管理平台
```

---

## 项目结构

### 完整目录树

```
football_platform/
├── README.md                   # 项目文档
├── .gitignore                  # Git 忽略文件
│
├── backend-server/             # 后端服务
│   ├── main.py                 # FastAPI 应用入口
│   ├── init_db.py              # 数据库初始化脚本
│   ├── requirements.txt        # Python 依赖
│   ├── .env.example            # 环境变量示例
│   ├── alembic.ini             # 数据库迁移配置
│   │
│   ├── app/                    # 应用核心代码
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI 实例配置
│   │   │
│   │   ├── api/                # API 路由层
│   │   │   ├── __init__.py
│   │   │   ├── deps.py         # 依赖注入
│   │   │   ├── auth.py         # 认证路由
│   │   │   ├── teams.py        # 球队路由
│   │   │   ├── players.py      # 球员路由
│   │   │   ├── matches.py      # 比赛路由
│   │   │   ├── match_players.py # 比赛统计路由
│   │   │   └── stats.py        # 统计路由
│   │   │
│   │   ├── core/               # 核心配置
│   │   │   ├── __init__.py
│   │   │   ├── config.py       # 配置管理
│   │   │   └── security.py     # 安全相关
│   │   │
│   │   ├── models/             # 数据库模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── team.py
│   │   │   ├── player.py
│   │   │   ├── match.py
│   │   │   └── match_player.py
│   │   │
│   │   ├── schemas/            # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── team.py
│   │   │   ├── player.py
│   │   │   ├── match.py
│   │   │   └── match_player.py
│   │   │
│   │   ├── service/            # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── team_service.py
│   │   │   ├── player_service.py
│   │   │   └── match_service.py
│   │   │
│   │   ├── repository/         # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── team.py
│   │   │   ├── player.py
│   │   │   └── match.py
│   │   │
│   │   └── utils/              # 工具函数
│   │       └── __init__.py
│   │
│   ├── tests/                  # 测试目录
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_api/
│   │
│   └── alembic/                # 数据库迁移
│       ├── versions/
│       └── env.py
│
└── frontend-pc/                # 前端应用
    ├── package.json            # 前端依赖
    ├── tsconfig.json           # TypeScript 配置
    ├── vite.config.ts          # Vite 配置
    ├── index.html              # HTML 入口
    ├── .env.example            # 环境变量示例
    │
    ├── public/                 # 静态资源
    │   └── favicon.ico
    │
    └── src/                    # 源代码
        ├── main.ts             # 应用入口
        ├── App.vue             # 根组件
        │
        ├── api/                # API 接口
        │   ├── index.ts        # Axios 配置
        │   ├── auth.ts
        │   ├── teams.ts
        │   ├── players.ts
        │   ├── matches.ts
        │   └── stats.ts
        │
        ├── assets/             # 资源文件
        │   └── styles/
        │
        ├── components/         # 公共组件
        │   ├── layouts/
        │   │   ├── Header.vue
        │   │   ├── Footer.vue
        │   │   └── MainLayout.vue
        │   └── common/
        │
        ├── router/             # 路由配置
        │   └── index.ts
        │
        ├── stores/             # Pinia 状态
        │   ├── user.ts
        │   ├── teams.ts
        │   └── matches.ts
        │
        ├── types/              # TypeScript 类型
        │   └── index.ts
        │
        ├── utils/              # 工具函数
        │   └── index.ts
        │
        └── views/              # 页面组件
            ├── Login.vue
            ├── Register.vue
            ├── Dashboard.vue
            ├── Teams.vue
            ├── TeamDetail.vue
            ├── Players.vue
            ├── Matches.vue
            ├── MatchDetail.vue
            ├── Stats.vue
            ├── HeadToHead.vue
            └── admin/
                ├── TeamManagement.vue
                ├── PlayerManagement.vue
                └── MatchManagement.vue
```

---

## 路由结构

### 前端路由

```typescript
// src/router/index.ts
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/teams',
    name: 'Teams',
    component: () => import('@/views/Teams.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/teams/:id',
    name: 'TeamDetail',
    component: () => import('@/views/TeamDetail.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/teams/:id/history',
    name: 'TeamHistory',
    component: () => import('@/views/TeamHistory.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/players',
    name: 'Players',
    component: () => import('@/views/Players.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/matches',
    name: 'Matches',
    component: () => import('@/views/Matches.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/matches/:id',
    name: 'MatchDetail',
    component: () => import('@/views/MatchDetail.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('@/views/Stats.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/head-to-head',
    name: 'HeadToHead',
    component: () => import('@/views/HeadToHead.vue'),
    meta: { requiresAuth: false }
  },
  // 管理页面（需要登录）
  {
    path: '/admin',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'teams',
        name: 'AdminTeams',
        component: () => import('@/views/admin/TeamManagement.vue')
      },
      {
        path: 'players',
        name: 'AdminPlayers',
        component: () => import('@/views/admin/PlayerManagement.vue')
      },
      {
        path: 'matches',
        name: 'AdminMatches',
        component: () => import('@/views/admin/MatchManagement.vue')
      }
    ]
  }
]
```

### 后端 API 路由

```python
# main.py
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(teams.router, prefix="/api/teams", tags=["球队"])
app.include_router(players.router, prefix="/api/players", tags=["球员"])
app.include_router(matches.router, prefix="/api/matches", tags=["比赛"])
app.include_router(match_players.router, prefix="/api/match_players", tags=["比赛统计"])
app.include_router(stats.router, prefix="/api/stats", tags=["统计"])
```

---

## 权限控制

### 前端路由守卫

```typescript
// src/router/index.ts
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth

  if (requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})
```

### 后端 API 权限

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的认证凭据")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭据")

    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user

# 使用示例
@router.post("/")
async def create_team(
    team: TeamCreate,
    current_user: User = Depends(get_current_user)
):
    # 只有登录用户可以访问
    ...
```

---

## 数据导入

### Excel 数据导入功能

支持通过 Excel 文件批量导入历史数据。

#### 支持的导入类型

1. **球队数据导入**
2. **球员数据导入**
3. **比赛结果导入**
4. **比赛统计导入**

#### 使用方法

```bash
cd backend-server

# 运行导入脚本
python import_football_data.py

# 或导入特定年份的数据
python import_2025_data.py
```

#### Excel 格式要求

球队数据：
| name | logo | description | founded_year |
|------|------|-------------|--------------|
| 曼联 | https://... | 英格兰足球俱乐部 | 1878 |

比赛数据：
| home_team | away_team | home_score | away_score | match_date | venue | match_type |
|-----------|-----------|------------|------------|------------|-------|------------|
| 曼联 | 利物浦 | 2 | 1 | 2024-01-15 | 老特拉福德 | league |

---

## 部署指南

### Docker 部署

#### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: football_user
      POSTGRES_PASSWORD: football_pass
      POSTGRES_DB: football_platform
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend-server
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./backend-server:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://football_user:football_pass@db:5432/football_platform
    depends_on:
      - db

  frontend:
    build: ./frontend-pc
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

#### 部署步骤

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产环境配置

1. **设置环境变量**
   - `DEBUG=False`
   - 配置生产数据库连接
   - 设置强密码和 SECRET_KEY

2. **数据库优化**
   - 配置连接池
   - 添加数据库索引
   - 定期备份

3. **前端优化**
   - 构建生产版本：`npm run build`
   - 配置 CDN
   - 启用 Gzip 压缩

4. **安全配置**
   - 启用 HTTPS
   - 配置 CORS 白名单
   - 设置速率限制

---

## 项目特色

### ✨ 技术亮点

1. **现代化技术栈**
   - Vue 3 Composition API + TypeScript
   - FastAPI 异步高性能框架
   - PostgreSQL 关系型数据库

2. **完整的架构设计**
   - 前后端分离
   - 分层架构（API-Service-Repository）
   - RESTful API 设计

3. **类型安全**
   - 前端：TypeScript 类型检查
   - 后端：Pydantic 数据验证
   - 减少运行时错误

4. **权限系统**
   - JWT Token 认证
   - 基于角色的访问控制
   - 路由守卫保护

5. **数据可视化**
   - ECharts 图表展示
   - 多维度数据统计
   - 实时数据更新

6. **开发体验**
   - Vite 极速开发服务器
   - API 自动文档（Swagger）
   - 热重载支持

### 🚀 扩展能力

- [ ] AI 助手集成（预测胜率、智能分析）
- [ ] 实时数据推送（WebSocket）
- [ ] 移动端适配（响应式设计）
- [ ] 多语言支持（i18n）
- [ ] 数据导出（PDF/Excel）
- [ ] 球员表现分析雷达图
- [ ] 赛程管理系统
- [ ] 裁判管理
- [ ] 转会记录管理

---

## 常见问题

### Q: 如何重置数据库？

```bash
cd backend-server
python init_db.py
```

### Q: 如何修改 API 地址？

编辑 `frontend-pc/.env` 文件：
```bash
VITE_API_BASE_URL=http://your-api-url/api
```

### Q: 如何添加新的数据筛选？

在后端 `app/api/stats.py` 中添加筛选参数，在前端调用时传入相应参数。

### Q: 如何部署到生产环境？

参考 [部署指南](#部署指南) 章节，建议使用 Docker 进行容器化部署。

---

## License

MIT License

---

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
