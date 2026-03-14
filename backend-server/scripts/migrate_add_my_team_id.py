"""
数据库迁移脚本：添加 my_team_id 字段到 users 表
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


def migrate():
    """执行数据库迁移"""
    print("开始数据库迁移...")

    with engine.begin() as conn:
        # 1. 添加 my_team_id 列（如果不存在）
        print("1. 添加 my_team_id 列...")
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN my_team_id INTEGER REFERENCES teams(id) ON DELETE SET NULL"))
            print("   ✓ my_team_id 列添加成功")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("   ℹ my_team_id 列已存在，跳过")
            else:
                print(f"   ✗ 添加列失败: {e}")
                return False

        # 2. 为现有用户设置 my_team_id
        print("2. 为现有用户设置 my_team_id...")
        result = conn.execute(text("""
            UPDATE users
            SET my_team_id = (
                SELECT team_id
                FROM team_members
                WHERE team_members.user_id = users.id
                AND team_members.is_active = true
                ORDER BY
                    CASE permission
                        WHEN 'owner' THEN 1
                        WHEN 'admin' THEN 2
                        WHEN 'member' THEN 3
                    END,
                    created_at ASC
                LIMIT 1
            )
            WHERE my_team_id IS NULL
        """))
        print(f"   ✓ 更新了 {result.rowcount} 个用户的 my_team_id")

        # 3. 创建索引
        print("3. 创建索引...")
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_my_team_id ON users(my_team_id)"))
            print("   ✓ 索引创建成功")
        except Exception as e:
            print(f"   ✗ 创建索引失败: {e}")

        # 4. 验证迁移结果
        print("4. 验证迁移结果...")
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE my_team_id IS NOT NULL"))
        count = result.scalar()
        print(f"   ✓ 有 {count} 个用户设置了 my_team_id")

    print("\n数据库迁移完成！")
    return True


if __name__ == "__main__":
    try:
        success = migrate()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        sys.exit(1)
