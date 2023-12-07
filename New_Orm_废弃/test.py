from dotenv import load_dotenv

load_dotenv(override=True)

from scr.sql.database import engine, Base, SessionLocal
# from sqlalchemy.orm import Session
from scr.sql import crud

Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    db = SessionLocal()
    print(crud.get_key(db))
