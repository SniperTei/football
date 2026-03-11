# 足球球队数据管理平台

一个完整的足球球队数据管理系统，支持球队、球员、比赛信息的管理和统计查询。

## 功能特性

### 数据管理
- **球队管理**：创建、查看、编辑、删除球队信息
- **球员管理**：管理球员信息（姓名、号码、位置等）
- **比赛管理**：记录比赛结果、场地、日期等信息
- **球员统计**：记录每场比赛球员的进球、助攻等数据

### 数据统计
- **射手榜**：按进球数排名
- **助攻榜**：按助攻数排名
- **积分榜**：球队积分排名（胜平负统计）
- **球队统计**：胜率、场均进球等数据分析
- **历史战绩**：查询两队之间的对战记录和胜率

### 权限控制
- **公开访问**：所有数据查看功能无需登录
- **数据维护**：创建、编辑、删除操作需要登录

## 技术栈

### 后端
- Python 3.10+
- FastAPI - 现代化 Web 框架
- SQLAlchemy - ORM
- PostgreSQL - 关系型数据库
- JWT - 用户认证

### 前端
- Vue 3 - 渐进式 JavaScript 框架
- TypeScript - 类型安全
- Vite - 快速构建工具
- Element Plus - UI 组件库
- Pinia - 状态管理
- Axios - HTTP 客户端

## 快速开始

### 1. 环境要求
- Python 3.10+
- Node.js 18+
- PostgreSQL 12+

### 2. 后端设置

```bash
# 进入后端目录
cd backend-server

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量配置
cp .env.example .env

# 编辑 .env 文件，配置数据库连接
# DATABASE_URL=postgresql://username:password@localhost:5432/football_platform

# 创建数据库
psql -U postgres
CREATE DATABASE football_platform;
\q

# 初始化数据库（创建表并插入示例数据）
python init_db.py

# 启动后端服务
uvicorn main:app --reload --port 8000
```

后端 API 文档：http://localhost:8000/docs

### 3. 前端设置

```bash
# 进入前端目录
cd frontend-pc

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用：http://localhost:5173

### 4. 默认账户

后端初始化后，可以使用以下账户登录：

- **用户名**: `admin`
- **密码**: `admin123`

## 项目结构

```
football_platform/
├── backend-server/       # 后端服务
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据库模型
│   │   └── schemas/     # Pydantic schemas
│   ├── main.py          # 应用入口
│   ├── init_db.py       # 数据库初始化脚本
│   └── requirements.txt
│
└── frontend-pc/         # 前端应用
    ├── src/
    │   ├── api/         # API 接口
    │   ├── components/  # 公共组件
    │   ├── layouts/     # 布局组件
    │   ├── router/      # 路由配置
    │   ├── stores/      # 状态管理
    │   └── views/       # 页面组件
    └── package.json
```

## 主要功能页面

| 页面 | 路径 | 说明 | 权限 |
|------|------|------|------|
| 登录 | /login | 用户登录 | 公开 |
| 注册 | /register | 用户注册 | 公开 |
| 首页 | /dashboard | 数据概览 | 公开 |
| 球队列表 | /teams | 查看所有球队 | 公开 |
| 球队详情 | /teams/:id | 球队详细信息 | 公开 |
| 球员列表 | /players | 查看所有球员 | 公开 |
| 比赛列表 | /matches | 查看所有比赛 | 公开 |
| 比赛详情 | /matches/:id | 比赛详情和球员统计 | 公开 |
| 数据统计 | /stats | 射手榜、助攻榜、积分榜 | 公开 |
| 历史战绩 | /head-to-head | 两队对战历史查询 | 公开 |
| 球队管理 | /admin/teams | 增删改球队 | 需登录 |
| 球员管理 | /admin/players | 增删改球员 | 需登录 |
| 比赛管理 | /admin/matches | 增删改比赛 | 需登录 |

## 未来扩展

- [ ] AI 助手集成（预测胜率、分析比赛）
- [ ] 数据可视化图表（ECharts）
- [ ] 球员表现分析
- [ ] 赛程管理
- [ ] 移动端适配
- [ ] 多语言支持

## License

MIT
