"""
数据库初始化模块
负责在应用启动时自动创建数据库（如果不存在）并创建表结构
"""
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.database import Base

logger = logging.getLogger(__name__)


def init_database():
    """
    初始化数据库：检查目标数据库是否存在，不存在则创建
    然后创建所有表结构

    此函数连接到 PostgreSQL 的默认数据库 'postgres'，
    检查目标数据库是否存在，如果不存在则创建它，
    最后创建所有表结构。
    """
    # 从 DATABASE_URL 中提取数据库连接信息
    # 格式: postgresql+psycopg://user@host:port/database
    db_url = settings.DATABASE_URL

    # 构建连接到默认 postgres 数据库的 URL
    # 我们将数据库名称替换为 'postgres' 来连接到默认数据库
    if ":///" in db_url:
        # SQLite 格式，不需要创建数据库
        logger.info("Using SQLite database, skipping auto-creation")
        create_tables()
        return

    # 提取目标数据库名称
    # 格式: postgresql+psycopg://user@host:port/database
    parts = db_url.split("/")
    if len(parts) < 4:
        logger.error(f"Invalid DATABASE_URL format: {db_url}")
        return

    target_db = parts[-1].split("?")[0]  # 移除可能的查询参数

    # 构建连接到默认 postgres 数据库的 URL
    default_db_url = db_url.replace(f"/{target_db}", "/postgres")

    try:
        # 连接到默认数据库
        engine = create_engine(default_db_url, isolation_level="AUTOCOMMIT")

        with engine.connect() as conn:
            # 检查目标数据库是否存在
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname=:db_name"),
                {"db_name": target_db}
            )

            db_exists = result.scalar() is not None

            if db_exists:
                logger.info(f"Database '{target_db}' already exists")
            else:
                # 创建数据库
                # 注意：CREATE DATABASE 不能在事务中执行
                # 但我们设置了 AUTOCOMMIT，所以可以直接执行
                conn.execute(
                    text(f"CREATE DATABASE {target_db} ENCODING 'UTF8'")
                )
                logger.info(f"Database '{target_db}' created successfully")

        engine.dispose()

        # 创建表结构
        create_tables()

    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        raise


def create_tables():
    """创建所有数据库表"""
    try:
        from app.core.database import engine, SessionLocal
        from app.models.user import User
        from app.models.team import Team
        from app.core.security import get_password_hash

        # 创建表结构
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # 创建初始用户和球队
        db = SessionLocal()
        try:
            # 1. 先创建梅州客家队（需要ID来关联用户）
            existing_team = db.query(Team).filter(Team.name == "梅州客家队").first()
            if not existing_team:
                meizhou_team = Team(
                    name="梅州客家队",
                    description="梅州客家足球俱乐部",
                    founded_year=2023
                )
                db.add(meizhou_team)
                db.flush()
                logger.info("Team 梅州客家队 created successfully (ID: {})".format(meizhou_team.id))
            else:
                meizhou_team = existing_team
                logger.info("Team 梅州客家队 already exists (ID: {})".format(meizhou_team.id))

            # 2. 创建 admin 用户
            existing_admin = db.query(User).filter(User.username == "admin").first()
            if not existing_admin:
                admin_user = User(
                    username="admin",
                    email="admin@football.com",
                    hashed_password=get_password_hash("admin234"),
                    is_admin=True,
                    is_active=True
                )
                db.add(admin_user)
                db.flush()
                logger.info("Admin user created successfully (username: admin, password: admin234)")
            else:
                logger.info("Admin user already exists, skipping creation")

            # 3. 创建 cangming 用户（非管理员，关联梅州客家队）
            existing_cangming = db.query(User).filter(User.username == "cangming").first()
            if not existing_cangming:
                cangming_user = User(
                    username="cangming",
                    email="cangming@football.com",
                    hashed_password=get_password_hash("cangming234"),
                    my_team_id=meizhou_team.id,  # 关联梅州客家队
                    is_admin=False,
                    is_active=True
                )
                db.add(cangming_user)
                db.flush()
                logger.info("User cangming created successfully (username: cangming, password: cangming234, my_team_id: {})".format(meizhou_team.id))
            else:
                # 如果用户已存在但没有my_team_id，更新它
                if not existing_cangming.my_team_id:
                    existing_cangming.my_team_id = meizhou_team.id
                    db.flush()
                    logger.info("User cangming already exists, updated my_team_id to {}".format(meizhou_team.id))
                else:
                    logger.info("User cangming already exists with my_team_id: {}".format(existing_cangming.my_team_id))

            db.commit()

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create initial data: {e}")
            raise
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise
