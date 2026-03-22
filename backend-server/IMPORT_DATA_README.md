# 足球数据导入指南

## 概述

`import_football_data.py` 脚本用于将 `football_data.xlsx` 中的历史比赛数据导入到数据库中。

## 功能特性

✅ **自动创建球队和球员**
- 创建主队（默认名称"朋队"）
- 为所有 29 位球员创建记录
- 自动创建对手球队

✅ **导入比赛记录**
- 读取比赛日期、对手、比分
- 转换 Excel 日期格式
- 自动设置比赛状态为"已完成"

✅ **导入球员统计**
- 识别出勤球员（有进球或助攻记录）
- 记录进球数和助攻数
- 自动关联到对应比赛

## 前置准备

### 1. 安装依赖

```bash
pip install pandas openpyxl
```

或重新安装所有依赖：

```bash
pip install -r requirements.txt
```

### 2. 确保数据库已初始化

```bash
python init_db.py
```

### 3. 配置环境变量

确保已设置正确的数据库连接：

```bash
export ENV=dev  # 或其他环境
```

## 使用方法

### 基本用法

```bash
python import_football_data.py
```

这将使用默认配置：
- 文件：`football_data.xlsx`
- 主队名称：`朋队`

### 自定义参数

```bash
python import_football_data.py --file your_data.xlsx --team 你的球队名
```

参数说明：
- `--file`: Excel 文件路径（默认：football_data.xlsx）
- `--team`: 主队名称（默认：朋队）

## 导入过程

脚本会显示详细的导入日志：

```
开始导入足球数据: football_data.xlsx
============================================================

1. 读取 Excel 文件...
   读取到 32 行数据

2. 提取球员名单...
   发现 29 位球员:
   1. 朋队
   2. 会长
   3. 未来
   ...

3. 创建主队: 朋队
  ✓ 创建球队: 朋队

4. 创建球员...
    ✓ 创建球员: 朋队
    ✓ 创建球员: 会长
    ✓ 创建球员: 未来
    ...

5. 导入比赛数据...
  ✓ 行 2: 创建比赛 2024-08-01 vs 罗湖卫计委 (3:3)
    - 会长: 0球 1助攻
    - 小源: 3球 1助攻
    - 哈维: 0球 1助攻
  ✓ 行 3: 创建比赛 2024-08-05 vs 布心队 (5:6)
    - 未来: 1球 0助攻
    - 李强: 3球 0助攻
    - 小源: 3球 1助攻
    ...

============================================================
导入完成！
  总比赛场次: 30
  总球员统计记录: 180
  球队数量: 29
  球员数量: 29
============================================================
```

## 数据说明

### Excel 文件格式

```
日期       | 对手     | 比分  | 朋队(进球) | 朋队(助攻) | 会长(进球) | 会长(助攻) | ...
----------|---------|-------|-----------|-----------|-----------|-----------|----
45504     | 罗湖卫计委| 3:3   |           |           |           | 1         | ...
45508     | 布心队   | 5:6   |           |           |           |           | ...
```

### 日期转换

Excel 日期序列号（如 45504）会自动转换为正常日期格式（2024-08-01）

### 比分解析

比分格式 "3:3" 会自动解析为：
- `home_score`: 3
- `away_score`: 3

### 球员出勤判断

- 如果球员的"进球"或"助攻"列有数值 → 该球员出勤 ✅
- 如果两列都为空 → 该球员未出勤 ❌

## 注意事项

### ⚠️ 球员位置

由于 Excel 中没有记录球员位置，所有球员的 `position` 字段默认设置为 `"中场"`。

导入后需要手动在管理后台修改每个球员的实际位置（前锋、中场、后卫、门将）。

### ⚠️ 重复导入

脚本会检查：
- 如果球队已存在 → 不重复创建
- 如果球员已存在 → 不重复创建
- 如果比赛已存在（同日期、同对手）→ 跳过该场比赛
- 如果球员统计已存在 → 不重复创建

可以安全地多次运行导入脚本！

### ⚠️ 数据准确性

请确保 Excel 文件：
- 第一行是标题行（包含"进球"、"助攻"）
- 第二行开始是实际数据
- 日期列使用 Excel 日期格式
- 比分格式为 "A:B"

## 故障排除

### 错误：No module named 'pandas'

```bash
pip install pandas openpyxl
```

### 错误：数据库连接失败

检查 `.env.dev` 文件中的数据库配置：

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/football_platform_dev
```

### 错误：表不存在

先运行数据库初始化：

```bash
python init_db.py
```

### 警告：无效日期

如果某行的日期列无效，该行会被跳过，不影响其他数据的导入。

## 验证导入结果

导入完成后，可以通过以下方式验证：

### 1. 查看数据库

```python
from app.core.database import SessionLocal
from app.models.team import Team
from app.models.player import Player
from app.models.match import Match

db = SessionLocal()
print(f"球队数量: {db.query(Team).count()}")
print(f"球员数量: {db.query(Player).count()}")
print(f"比赛数量: {db.query(Match).count()}")
db.close()
```

### 2. 访问管理后台

启动后端和前端服务：
- 后端：`http://localhost:8000`
- 前端：`http://localhost:5173`

访问：
- `/admin/teams` - 查看导入的球队
- `/admin/players` - 查看导入的球员（记得修改位置）
- `/admin/matches` - 查看导入的比赛
- `/matches` - 查看比赛详情和球员统计

### 3. 查看统计数据

访问 `/stats` 页面，查看：
- 射手榜
- 助攻榜
- 出勤榜

所有数据应该都已经在统计中了！

## 后续操作

导入完成后，建议：

1. **修改球员位置**
   - 在管理后台为每个球员设置正确的位置
   - 位置：前锋、中场、后卫、门将

2. **添加球衣号码**
   - 为每个球员设置球衣号码

3. **补充比赛信息**
   - 添加比赛场地
   - 添加比赛备注

4. **检查数据准确性**
   - 验证比分是否正确
   - 验证球员统计是否准确

## 技术细节

### 数据模型

- **Team**: id, name, description, founded_year
- **Player**: id, team_id, name, position, jersey_number
- **Match**: id, home_team_id, away_team_id, match_date, home_score, away_score, status
- **MatchPlayer**: id, match_id, player_id, team_id, played, goals, assists

### 导入逻辑

1. 读取 Excel 文件
2. 提取 29 位球员名单
3. 创建主队和球员记录
4. 遍历每场比赛：
   - 转换日期格式
   - 解析比分
   - 创建或获取对手球队
   - 创建比赛记录
   - 为每个有数据的球员创建统计记录

### 日期转换

Excel 日期是自 1899-12-30 起的天数，例如：
- 45504 → 2024-08-01
- 45508 → 2024-08-05

## 联系方式

如有问题，请联系开发团队。
