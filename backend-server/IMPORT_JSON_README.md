# JSON比赛数据导入指南

## 文件说明

- **2024_match_data.json** - 2024年比赛数据（32场）
- **2025_match_data.json** - 2025年比赛数据（70场）
- **stats.json** - 统计数据（出勤、进球、助攻排名）
- **import_match_data.py** - 数据导入脚本

## 快速开始

```bash
# 确保数据库已启动
uvicorn main:app --reload --port 8021

# 运行导入脚本
python import_match_data.py
```

## 导入结果

✅ **成功导入数据到数据库**:
- 球队: 60个（主队 FC Sniper + 59个对手）
- 球员: 34个
- 比赛: 93场
- 球员统计: 765条记录

## 数据结构

### 比赛数据
```json
{
  "date": "2024-07-31",
  "opponent": "罗湖卫计委",
  "score": {"home": 3, "away": 3},
  "player_stats": {
    "洗衣服": {"goals": 3, "assists": 0}
  },
  "attendance": ["朋队", "欧队", "会长"]
}
```

### 统计数据
```json
{
  "attendance": [{"player_name": "洗衣服", "attendance_count": 67}],
  "goals": [{"player_name": "智星", "goal_count": 64}],
  "assists": [{"player_name": "洗衣服", "assist_count": 90}]
}
```

## TOP 射手榜

| 排名 | 球员 | 进球 | 助攻 | 出场 |
|-----|------|-----|------|-----|
| 1 | 洗衣服 | 83 | 116 | 74 |
| 2 | 智星 | 77 | 42 | 57 |
| 3 | 啊原 | 40 | 17 | 25 |
| 4 | 小源 | 37 | 39 | 47 |
| 5 | 小李 | 35 | 28 | 48 |

## 数据验证SQL

### 查看导入统计
```sql
SELECT
  (SELECT COUNT(*) FROM teams) as 球队数,
  (SELECT COUNT(*) FROM players) as 球员数,
  (SELECT COUNT(*) FROM matches) as 比赛场数,
  (SELECT COUNT(*) FROM match_players) as 统计记录数;
```

### 查询射手榜
```sql
SELECT
  p.name as 球员,
  COUNT(mp.match_id) as 出场,
  SUM(mp.goals) as 进球,
  SUM(mp.assists) as 助攻
FROM players p
JOIN match_players mp ON p.id = mp.player_id
GROUP BY p.id, p.name
ORDER BY 进球 DESC
LIMIT 10;
```

### 查询最近比赛
```sql
SELECT
  m.match_date as 日期,
  t2.name as 对手,
  m.home_score || ':' || m.away_score as 比分
FROM matches m
JOIN teams t1 ON m.home_team_id = t1.id
JOIN teams t2 ON m.away_team_id = t2.id
ORDER BY m.match_date DESC
LIMIT 10;
```

## 特性

✅ **自动去重**: 重复运行不会重复导入
✅ **完整数据**: 包含比赛、出勤、进球、助攻
✅ **错误处理**: 单条数据失败不影响整体导入
✅ **详细日志**: 实时显示导入进度

## 注意事项

1. 所有球员默认位置为"未知"，需手动设置
2. 所有比赛默认为友谊赛类型
3. 已存在的数据会自动跳过
4. 支持重复安全运行
