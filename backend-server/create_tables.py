"""
创建数据库表
只创建表，不插入数据
"""
from app.core.database import engine, Base
from app.models import User, Team, TeamMember, Player, Match, MatchPlayer

def create_tables():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成！")
    print("已创建的表：")
    print("- users (用户表)")
    print("- teams (球队表)")
    print("- team_members (球队成员权限表)")
    print("- players (球员表)")
    print("- matches (比赛表)")
    print("- match_players (比赛球员统计表)")

if __name__ == "__main__":
    create_tables()
