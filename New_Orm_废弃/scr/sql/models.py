from sqlalchemy import Column, BigInteger, DECIMAL, VARCHAR
from .database import Base


# 数据表 ORM模型
class ORM_Data(Base):
    __tablename__ = 'data'
    t = Column(BigInteger, primary_key=True)
    key = Column(VARCHAR(20), primary_key=True)
    value = Column(DECIMAL(10, 2), primary_key=True)
    unit = Column(VARCHAR(20), primary_key=True)
