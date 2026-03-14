"""
迁移脚本：删除 TeamMember 多对多关系表

说明：
- 现在使用 User.my_team_id 来管理用户和球队的关系（一个用户一个球队）
- TeamMember 表是旧的多对多关系残留，需要删除
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import get_db

def migrate():
    """执行迁移"""
    print("开始迁移：删除 TeamMember 表...")

    db = next(get_db())

    try:
        # 查看当前数据
        result = db.execute(text("SELECT COUNT(*) FROM team_members"))
        count = result.scalar()
        print(f"TeamMember 表当前有 {count} 条记录")

        # 删除表
        print("删除 team_members 表...")
        db.execute(text("DROP TABLE IF EXISTS team_members CASCADE"))
        db.commit()

        print("✅ team_members 表已删除")

        # 验证表已删除
        result = db.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='team_members'
        """))
        if result.first() is None:
            print("✅ 验证成功：team_members 表已不存在")
        else:
            print("❌ 验证失败：表仍然存在")

        print("迁移完成！")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
