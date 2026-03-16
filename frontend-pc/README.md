# Football Platform Frontend

足球球队数据管理平台前端应用

## ⚠️ 安全警告

**重要：以下凭据仅供开发和测试使用，生产环境部署前必须修改！**

### 默认账户风险
- ❌ **禁止在生产环境使用默认账户**
- 默认管理员账户（admin/admin123）仅用于本地开发和测试
- 生产环境必须删除或修改默认账户密码

### API 配置
- 开发环境使用 `http://localhost:8000` 作为后端地址
- 生产环境必须配置实际的后端服务器地址
- 确保 API 服务器使用 HTTPS 协议

### 环境变量
- 生产环境部署时，不要在前端代码中硬编码敏感信息
- 使用环境变量管理配置
- 确保 `.env` 文件不被提交到版本控制

### 生产环境检查清单
- [ ] 修改后端默认账户密码
- [ ] 配置生产环境 API 地址
- [ ] 启用 HTTPS
- [ ] 配置 CSP（内容安全策略）
- [ ] 移除开发调试工具
- [ ] 优化构建产物（npm run build）
- [ ] 配置 CDN 加速

## 项目简介

一个功能完整的足球球队数据管理平台前端应用，支持球队管理、球员信息、比赛记录、数据统计等功能。采用 Vue 3 + TypeScript 开发，使用 Element Plus 作为 UI 组件库，提供现代化的用户界面和流畅的用户体验。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全
- **Vite** - 新一代前端构建工具
- **Element Plus** - Vue 3 UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端
- **ECharts** - 数据可视化图表

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
- **首页概览** - 快速查看平台数据概览
- **球队列表和详情** - 浏览所有球队，查看球队详细信息和球员名单
- **球队历史战绩** - 查看球队的历史比赛记录和战绩统计
- **球员列表** - 浏览所有球员信息
- **比赛列表和详情** - 查看所有比赛记录，查看比赛详情和球员统计
- **数据统计** - 查看射手榜、助攻榜、出勤榜等排名数据
  - 榜首球员高亮显示（紫色渐变卡片）
  - 支持按球队筛选
  - 可调整显示数量（5-50名）
- **历史战绩查询** - 查询任意两支球队之间的历史对战记录

### 管理功能（需要登录）

#### 管理员专属功能
- **球队管理** - 创建、编辑、删除所有球队
  - 管理员可以创建多个球队
  - 可以管理任何球队的信息
- **球员管理** - 创建、编辑、删除所有球员
  - 可以管理任何球队的球员
- **比赛管理** - 创建、编辑、删除所有比赛
  - 可以管理任何比赛

#### 球队拥有者功能
- **球队管理** - 创建和管理自己的球队
  - 普通用户只能创建一个球队
  - 只能管理自己球队的球员和比赛
- **球员管理** - 管理自己球队的球员
- **比赛管理** - 管理自己球队的比赛（作为主队的比赛）
  - 编辑比赛比分
  - 管理出场球员
  - 修改进球和助攻数据

### 比赛详情编辑
- 从比赛列表或管理页面进入比赛详情
- 管理员和球队拥有者可以编辑比赛信息
- 支持编辑：
  - 比赛基本信息（日期、场地、比分）
  - 出场球员列表
  - 球员统计数据（进球、助攻）

### 响应式设计
- 适配桌面端和平板设备
- 统计页面采用 2 列网格布局
- 优化的表格显示，避免横向滚动

## 路由说明

### 公开页面
| 路径 | 说明 | 组件 |
|------|------|------|
| `/` | 重定向到首页 | - |
| `/dashboard` | 首页概览 | Dashboard.vue |
| `/teams` | 球队列表 | Teams.vue |
| `/teams/:id` | 球队详情 | TeamDetail.vue |
| `/teams/:id/history` | 球队历史战绩 | TeamHistory.vue |
| `/players` | 球员列表 | Players.vue |
| `/matches` | 比赛列表 | Matches.vue |
| `/matches/:id` | 比赛详情 | MatchDetail.vue |
| `/stats` | 数据统计 | Stats.vue |
| `/head-to-head` | 历史战绩查询 | HeadToHead.vue |
| `/register` | 用户注册 | Register.vue |

### 管理页面
| 路径 | 说明 | 权限要求 |
|------|------|---------|
| `/admin/teams` | 球队管理 | 管理员或球队拥有者 |
| `/admin/players` | 球员管理 | 管理员或球队拥有者 |
| `/admin/matches` | 比赛管理 | 管理员或球队拥有者（仅主队比赛） |

### 导航行为
- **管理员用户**：
  - 点击"球队"菜单跳转到 `/admin/teams`
  - 点击"比赛"菜单跳转到 `/admin/matches`
  - 可以管理所有球队、球员和比赛

- **球队拥有者**：
  - 点击"球队"菜单跳转到 `/teams`（普通列表页）
  - 点击"比赛"菜单跳转到 `/matches`（普通列表页）
  - 可以在管理页面管理自己球队的球员和比赛

- **未登录用户**：
  - 所有管理操作会触发登录弹窗
  - 登录后根据用户角色跳转到相应页面

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

## 状态管理

使用 Pinia 进行状态管理，主要的 Store：

### Auth Store (stores/auth.ts)
管理用户认证状态和权限：
- `token` - JWT 认证令牌
- `user` - 当前登录用户信息
- `isAuthenticated` - 是否已登录
- `isAdmin` - 是否为管理员
- `loginDialogRequired` - 是否显示登录弹窗

主要方法：
- `login(username, password)` - 用户登录
- `register(username, email, password)` - 用户注册
- `logout()` - 退出登录
- `showLoginDialog()` - 显示登录弹窗
- `hideLoginDialog()` - 隐藏登录弹窗

## UI/UX 特性

### 统计页面优化
- **榜首高亮**：使用紫色渐变卡片展示第一名球员，突出显示关键数据
- **简化表格**：每个排行榜只显示 5 列（排名、球员、号码、球队、统计数据）
- **2 列布局**：采用响应式网格布局，一行显示 2 个统计卡片
- **筛选功能**：支持按球队筛选排名数据
- **数量控制**：可调整显示 5-50 名的排名数据

### 登录体验
- **弹窗登录**：未登录用户访问管理功能时，通过弹窗形式进行登录
- **跳转保持**：登录后自动跳转到之前尝试访问的页面
- **角色导航**：根据用户角色自动调整导航菜单和跳转逻辑

### 响应式设计
- **断点适配**：针对桌面端和平板设备进行优化
- **表格优化**：避免横向滚动，提供更好的数据浏览体验
- **卡片布局**：使用卡片和网格布局，提升视觉效果

## 开发建议

### 添加新页面
1. 在 `src/views/` 中创建 Vue 组件
2. 在 `src/router/index.ts` 中添加路由配置
3. 如需权限控制，添加 `meta: { requiresAuth: true }`

### 添加新 API
1. 在 `src/api/` 中创建对应的 API 模块
2. 定义 TypeScript 接口用于类型安全
3. 在组件中导入并使用

### 状态管理
1. 在 `src/stores/` 中创建新的 Pinia store
2. 使用 `storeToRefs` 确保响应式
3. 在组件中通过 `useXxxStore()` 访问

## 默认账户

**⚠️ 警告：以下是开发和测试用的默认账户，生产环境必须修改或删除！**

### 管理员账户
- 用户名: `admin`
- 密码: `admin123`
- 权限: 可以管理所有球队、球员和比赛

**生产环境安全建议：**
- 登录后立即修改默认密码
- 或直接删除此默认账户，创建新的管理员账户

### 测试账户
- 可以通过注册页面创建普通用户账户
- 普通用户创建球队后将成为球队拥有者
- 球队拥有者只能管理自己球队的数据

## 常见问题

### 1. 如何判断当前用户权限？
```typescript
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { isAdmin, user } = storeToRefs(authStore)

// 判断是否为管理员
if (isAdmin.value) {
  // 管理员逻辑
}

// 判断是否为球队拥有者
const hasTeam = user.value?.my_team_id != null
if (hasTeam) {
  // 球队拥有者逻辑
}
```

### 2. 如何触发登录弹窗？
```typescript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
authStore.showLoginDialog()
```

### 3. 如何配置 API 代理？
在 `vite.config.ts` 中修改 `server.proxy` 配置：
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://your-backend-url',
      changeOrigin: true
    }
  }
}
```
