# Football Platform Frontend

足球球队数据管理平台前端应用

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全
- **Vite** - 新一代前端构建工具
- **Element Plus** - Vue 3 UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端

## 项目结构

```
frontend-pc/
├── src/
│   ├── api/              # API 接口
│   │   ├── index.ts
│   │   ├── auth.ts
│   │   ├── teams.ts
│   │   ├── players.ts
│   │   ├── matches.ts
│   │   └── stats.ts
│   ├── assets/           # 静态资源
│   ├── components/       # 公共组件
│   ├── layouts/          # 布局组件
│   │   └── MainLayout.vue
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── stores/           # 状态管理
│   │   └── auth.ts
│   ├── views/            # 页面组件
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   ├── Dashboard.vue
│   │   ├── Teams.vue
│   │   ├── Players.vue
│   │   ├── Matches.vue
│   │   ├── Stats.vue
│   │   ├── HeadToHead.vue
│   │   ├── TeamDetail.vue
│   │   ├── MatchDetail.vue
│   │   └── admin/        # 管理页面
│   │       ├── Teams.vue
│   │       ├── Players.vue
│   │       └── Matches.vue
│   ├── App.vue
│   └── main.ts
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 快速开始

### 1. 安装依赖

```bash
cd frontend-pc
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

服务器将在 http://localhost:5173 启动

### 3. 构建生产版本

```bash
npm run build
```

## 功能说明

### 公开访问（无需登录）
- 首页概览
- 球队列表和详情
- 球员列表
- 比赛列表和详情
- 数据统计（射手榜、助攻榜、积分榜）
- 历史战绩查询

### 需要登录的功能
- 球队管理（增删改）
- 球员管理（增删改）
- 比赛管理（增删改）

## 路由说明

| 路径 | 说明 | 需要登录 |
|------|------|---------|
| `/login` | 登录页面 | 否 |
| `/register` | 注册页面 | 否 |
| `/dashboard` | 首页概览 | 否 |
| `/teams` | 球队列表 | 否 |
| `/teams/:id` | 球队详情 | 否 |
| `/players` | 球员列表 | 否 |
| `/matches` | 比赛列表 | 否 |
| `/matches/:id` | 比赛详情 | 否 |
| `/stats` | 数据统计 | 否 |
| `/head-to-head` | 历史战绩 | 否 |
| `/admin/teams` | 球队管理 | 是 |
| `/admin/players` | 球员管理 | 是 |
| `/admin/matches` | 比赛管理 | 是 |

## API 配置

API 请求通过 Vite 代理转发到后端服务器，配置在 `vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

确保后端服务器在 `http://localhost:8000` 运行。

## 默认账户

后端初始化后，可以使用以下账户登录：

- 用户名: `admin`
- 密码: `admin123`
