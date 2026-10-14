from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import config

engine = create_engine(config.database_url)
SessaoLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessaoLocal()
    try:
        yield db
    finally:
        db.close()