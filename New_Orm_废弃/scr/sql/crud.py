from sqlalchemy.orm import Session
from .models import ORM_Data


# 获取所有key
def get_key(db: Session):
    return db.query(ORM_Data.key).group_by(ORM_Data.key).all()


# 获取某时间段某key所有value
def get_key_info(db: Session, key: str, st: int, et: int):
    return db.query(ORM_Data).filter(ORM_Data.key == key, ORM_Data.t > st, ORM_Data.t < et).all()
