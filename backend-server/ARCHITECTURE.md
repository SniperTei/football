# 后端架构说明

## 分层架构

本项目采用经典的三层架构设计，职责分离清晰，便于维护和测试。

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (接口层)                    │
│  app/api/routes/                                        │
│  - 处理 HTTP 请求/响应                                    │
│  - 参数验证                                              │
│  - 调用 Service 层                                       │
│  - 返回标准响应格式                                       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Service Layer (业务逻辑层)               │
│  app/service/                                            │
│  - 实现业务逻辑                                          │
│  - 调用 Repository 层                                     │
│  - 事务管理                                              │
│  - 抛出业务异常                                          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│               Repository Layer (数据访问层)               │
│  app/repository/                                         │
│  - 封装数据库操作                                         │
│  - CRUD 基础方法                                          │
│  - 复杂查询                                              │
│  - 数据持久化                                             │
└─────────────────────────────────────────────────────────┘
```

## 各层说明

### 1. Repository 层（数据访问层）

**职责**：封装所有数据库操作

**特点**：
- 提供 CRUD 基础方法
- 不包含业务逻辑
- 可被多个 Service 复用
- 与模型一一对应

**示例**：
```python
# app/repository/team.py
class TeamRepository(BaseRepository[Team]):
    def get_by_name(self, name: str) -> Optional[Team]:
        return self.db.query(Team).filter(Team.name == name).first()

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        query = self.db.query(Team).filter(Team.name == name)
        if exclude_id:
            query = query.filter(Team.id != exclude_id)
        return query.first() is not None
```

**基类提供的方法**：
- `get_by_id(id)` - 根据 ID 获取
- `get_all(**filters)` - 获取所有，支持过滤
- `create(**kwargs)` - 创建
- `update(id, **kwargs)` - 更新
- `delete(id)` - 删除
- `exists(**kwargs)` - 检查是否存在
- `count(**filters)` - 统计数量

### 2. Service 层（业务逻辑层）

**职责**：实现业务逻辑

**特点**：
- 实现复杂业务规则
- 协调多个 Repository
- 事务管理
- 抛出业务异常

**示例**：
```python
# app/service/team_service.py
class TeamService:
    def __init__(self, db: Session):
        self.db = db
        self.team_repo = TeamRepository(db)

    def create_team(self, team_data: TeamCreate) -> Team:
        # 业务逻辑：检查球队名是否已存在
        if self.team_repo.name_exists(team_data.name):
            raise DuplicateException("球队", "名称", team_data.name)

        # 调用 Repository 层
        return self.team_repo.create(**team_data.model_dump())
```

**自定义异常**：
- `NotFoundException` - 资源不存在 (404)
- `DuplicateException` - 数据重复 (409)
- `ValidationException` - 验证失败 (400)

### 3. API 层（接口层）

**职责**：处理 HTTP 请求/响应

**特点**：
- 轻量级，只做请求/响应转换
- 调用 Service 层
- 不包含业务逻辑
- 统一错误处理

**示例**：
```python
# app/api/routes/teams.py
@router.post("", response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建球队（需要登录）"""
    service = TeamService(db)
    return service.create_team(team_data)
```

## 优势

### 1. 职责分离
- 每一层职责明确，修改某一层不影响其他层
- API 层专注于 HTTP 处理
- Service 层专注于业务逻辑
- Repository 层专注于数据访问

### 2. 易于测试
- Repository 层：可以 mock 数据库进行单元测试
- Service 层：可以 mock Repository 进行业务逻辑测试
- API 层：可以 mock Service 进行接口测试

### 3. 代码复用
- Service 可以被多个 API 复用
- Repository 可以被多个 Service 复用
- 避免重复代码

### 4. 易于扩展
- 添加新功能只需在对应层添加代码
- 更换数据库只需修改 Repository 层
- 修改业务逻辑不影响 API 层

## 目录结构

```
backend-server/
├── app/
│   ├── api/              # API 层
│   │   └── routes/       # 路由
│   ├── service/          # Service 层
│   │   ├── exceptions.py # 业务异常
│   │   ├── team_service.py
│   │   ├── player_service.py
│   │   ├── match_service.py
│   │   ├── stats_service.py
│   │   └── auth_service.py
│   ├── repository/       # Repository 层
│   │   ├── base.py       # 基类
│   │   ├── team.py
│   │   ├── player.py
│   │   ├── match.py
│   │   ├── user.py
│   │   └── match_player_stats.py
│   ├── models/           # 数据库模型
│   ├── schemas/          # Pydantic schemas
│   ├── core/             # 核心配置
│   └── main.py
```

## 请求流程

```
用户请求
   │
   ▼
┌─────────────┐
│  API Layer  │  1. 接收请求
│             │  2. 验证参数
│             │  3. 调用 Service
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ Service Layer│  1. 业务逻辑
│              │  2. 调用 Repository
│              │  3. 返回结果
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│ Repository Layer│  1. 数据库操作
│                 │  2. 返回数据
└─────────────────┘
```

## 最佳实践

### 1. API 层
- 保持轻量，只做请求/响应转换
- 不要包含业务逻辑
- 使用 FastAPI 依赖注入

### 2. Service 层
- 实现所有业务逻辑
- 使用自定义异常
- 一个 Service 类对应一个业务领域

### 3. Repository 层
- 封装所有数据库操作
- 继承 BaseRepository 获得基础 CRUD
- 添加特定的查询方法

### 4. 异常处理
- Service 层抛出业务异常
- 全局异常处理器统一处理
- 返回标准的错误响应格式
