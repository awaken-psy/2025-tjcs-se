import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from app.logger import db_logger

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATABASE_DIR = os.path.join(PROJECT_ROOT, "data")

# 确保数据库目录存在
os.makedirs(DATABASE_DIR, exist_ok=True)

# 数据库配置
DATABASE_CONFIG = {
    "mysql": {
        "driver": "mysql+pymysql",
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "3306"),
        "username": os.getenv("DB_USERNAME", "root"),
        "password": os.getenv("DB_PASSWORD", "114514"),
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
        "database": os.getenv("DB_PATH", os.path.join(DATABASE_DIR, "timecapsule.db")),
        "echo": os.getenv("DB_ECHO", "false").lower() == "true"
    }
}


def get_database_url():
    """获取数据库连接URL"""
    db_type = os.getenv("DB_TYPE", "mysql").lower()

    if db_type == "mysql":
        config = DATABASE_CONFIG["mysql"]
        # 对用户名和密码进行URL编码以处理特殊字符
        username_encoded = quote_plus(config['username'])
        password_encoded = quote_plus(config['password'])
        return f"{config['driver']}://{username_encoded}:{password_encoded}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"
    else:
        # 默认使用SQLite
        config = DATABASE_CONFIG["sqlite"]
        return f"sqlite:///{config['database']}"


def create_engine_with_config()->Engine:
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
    """创建数据库表"""
    try:
        db_logger.info("开始创建数据库表...")
        Base.metadata.create_all(bind=engine)
        db_logger.info("数据库表创建成功！")
    except Exception as e:
        db_logger.error(f"创建数据库表时出错: {e}, 这可能是由于权限问题或路径不存在导致的")
        # 不要抛出异常，让应用继续运行
        db_logger.warning(f"程序将在没有数据库的情况下运行")


def drop_tables():
    """删除所有表（用于测试和开发）
    """
    Base.metadata.drop_all(bind=engine)
    print("所有数据库表已删除")
