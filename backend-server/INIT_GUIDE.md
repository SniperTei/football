# 梅州客家队数据初始化指南

## 系统初始化

系统会在首次启动时自动初始化以下内容：

### 用户账号

| 用户名 | 密码 | 角色 | 邮箱 |
|--------|------|------|------|
| admin | admin234 | 管理员 | admin@football.com |
| cangming | cangming234 | 普通用户 | cangming@football.com |

### 球队信息

- **梅州客家队** (ID: 1)
  - 描述: 梅州客家足球俱乐部
  - 成立年份: 2023
  - 所有球员均属于此球队

## 数据导入

### 比赛数据
- **2024_match_data.json** - 2024年32场比赛
- **2025_match_data.json** - 2025年70场比赛

### 导入步骤

```bash
# 1. 启动服务器（自动初始化数据库、用户、球队）
cd backend-server
uvicorn main:app --reload --port 8021

# 2. 在另一个终端运行导入脚本
python import_match_data.py
```

### 导入结果

#### 数据统计
- **球队**: 60个（梅州客家队 + 59个对手球队）
- **球员**: 34人（全部归属梅州客家队）
- **比赛**: 93场（2024年30场 + 2025年63场）
- **球员统计**: 765条记录

#### TOP 5 射手榜
| 排名 | 球员 | 进球 | 助攻 | 出场 |
|-----|------|-----|------|-----|
| 1 | 洗衣服 | 83 | 116 | 74 |
| 2 | 智星 | 77 | 42 | 57 |
| 3 | 啊原 | 40 | 17 | 25 |
| 4 | 小源 | 37 | 39 | 47 |
| 5 | 小李 | 35 | 28 | 48 |

## 登录测试

### Admin 账号
```bash
curl -X POST http://localhost:8021/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin234"}'
```

### Cangming 账号
```bash
curl -X POST http://localhost:8021/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"cangming","password":"cangming234"}'
```

## 数据库结构

### Teams 表
```sql
-- 梅州客家队是主队，所有比赛的主队都是它
SELECT * FROM teams WHERE name = '梅州客家队';
```

### Players 表
```sql
-- 所有34个球员都归属梅州客家队
SELECT p.*, t.name as team_name
FROM players p
JOIN teams t ON p.team_id = t.id
WHERE t.name = '梅州客家队';
```

### Matches 表
```sql
-- 梅州客家队作为主队的所有比赛
SELECT m.*, ht.name as home_team, at.name as away_team
FROM matches m
JOIN teams ht ON m.home_team_id = ht.id
JOIN teams at ON m.away_team_id = at.id
WHERE ht.name = '梅州客家队'
ORDER BY m.match_date DESC;
```

### Match_Players 表
```sql
-- 梅州客家队球员的比赛统计
SELECT
  p.name as 球员,
  COUNT(mp.match_id) as 出场次数,
  SUM(mp.goals) as 进球,
  SUM(mp.assists) as 助攻
FROM players p
JOIN match_players mp ON p.id = mp.player_id
JOIN matches m ON mp.match_id = m.id
WHERE p.team_id = 1  -- 梅州客家队
GROUP BY p.id, p.name
ORDER BY 进球 DESC;
```

## 重要说明

1. **所有比赛都是梅州客家队的主场比赛**
   - home_team_id = 1 (梅州客家队)
   - away_team_id = 对手球队ID

2. **所有球员都属于梅州客家队**
   - team_id = 1 (梅州客家队)
   - 默认位置为"未知"，可后续修改

3. **数据可以重复导入**
   - 已存在的数据会自动跳过
   - 不会产生重复记录

4. **初始化脚本位置**
   - 数据库初始化: `app/core/db_init.py`
   - 数据导入脚本: `import_match_data.py`

## 故障排查

### 问题：数据库初始化失败
**解决方案**: 删除数据库重新启动
```bash
psql -U zhengnan -d postgres -c "DROP DATABASE IF EXISTS football_platform_dev;"
# 然后重新启动服务器
```

### 问题：导入时提示"梅州客家队不存在"
**解决方案**: 先启动服务器完成初始化，再运行导入脚本

### 问题：登录失败
**解决方案**: 检查密码是否正确
- admin/admin234
- cangming/cangming234

## 数据验证

### 验证用户
```bash
psql -U zhengnan -d football_platform_dev -c "SELECT id, username, is_admin FROM users;"
```

### 验证球队
```bash
psql -U zhengnan -d football_platform_dev -c "SELECT id, name FROM teams WHERE name = '梅州客家队';"
```

### 验证球员
```bash
psql -U zhengnan -d football_platform_dev -c "SELECT COUNT(*) FROM players WHERE team_id = 1;"
```

### 验证比赛
```bash
psql -U zhengnan -d football_platform_dev -c "SELECT COUNT(*) FROM matches WHERE home_team_id = 1;"
```
