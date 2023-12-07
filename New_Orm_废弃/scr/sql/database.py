import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

__host = os.getenv('DATABASE_HOST')
__user = os.getenv('DATABASE_USER')
__passwd = os.getenv('DATABASE_PASSWD')
__port = int(os.getenv('DATABASE_PORT'))
__db = os.getenv('DATABASE_DB')

SQLALCHEMY_DATABASE_URI: str = f'mysql+pymysql://{__user}:{__passwd}@{__host}:{__port}/{__db}?charset=utf8'
engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
# 这个类的每一个实例都是一个数据库的会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 来创建每个数据库模型或类（ORM 模型）
Base = declarative_base()
