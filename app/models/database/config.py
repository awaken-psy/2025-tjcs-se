import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 数据库配置
DATABASE_CONFIG = {
    "mysql": {
        "driver": "mysql+pymysql",
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "3306"),
        "username": os.getenv("DB_USERNAME", "timecapsule_user"),
        "password": os.getenv("DB_PASSWORD", "timecapsule_password"),
        "database": os.getenv("DB_DATABASE", "timecapsule"),
        "charset": "utf8mb4",
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "echo": os.getenv("DB_ECHO", "false").lower() == "true"
    },
    "sqlite": {
        "driver": "sqlite",
        "database": os.getenv("DB_PATH", "/tmp/timecapsule.db"),
        "echo": os.getenv("DB_ECHO", "false").lower() == "true"
    }
}


def get_database_url():
    """获取数据库连接URL"""
    db_type = os.getenv("DB_TYPE", "mysql").lower()

    if db_type == "sqlite":
        config = DATABASE_CONFIG["sqlite"]
        return f"sqlite:///{config['database']}"

    # 默认使用MySQL
    config = DATABASE_CONFIG["mysql"]
    return (
        f"{config['driver']}://{config['username']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}"
        f"?charset={config['charset']}"
    )


def create_engine_with_config():
    """创建数据库引擎"""
    db_url = get_database_url()
    db_type = os.getenv("DB_TYPE", "mysql").lower()

    if db_type == "mysql":
        config = DATABASE_CONFIG["mysql"]
        return create_engine(
            db_url,
            pool_size=config["pool_size"],
            max_overflow=config["max_overflow"],
            pool_recycle=config["pool_recycle"],
            pool_pre_ping=config["pool_pre_ping"],
            echo=config["echo"]
        )
    else:
        config = DATABASE_CONFIG["sqlite"]
        return create_engine(db_url, echo=config["echo"])


# 创建数据库引擎
engine = create_engine_with_config()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """创建所有表"""
    # 导入所有模型以确保它们被注册
    from app.models.database.user import User, UserFriend
    from app.models.database.capsule import Capsule, CapsuleMedia
    from app.models.database.unlock_condition import UnlockCondition
    from app.models.database.unlock_record import UnlockRecord, UnlockAttempt
    from app.models.database.capsule_interaction import CapsuleInteraction

    Base.metadata.create_all(bind=engine)
    print("所有数据库表创建完成")


def drop_tables():
    """删除所有表（用于测试和开发）"""
    Base.metadata.drop_all(bind=engine)
    print("所有数据库表已删除")