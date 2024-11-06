from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(
    "mysql+pymysql://{username}:{password}@{host}:{port}/{name}".format(
        username=settings.DB_USER,
        password=settings.DB_PASS,
        host=settings.DB_URL,
        port=settings.DB_PORT,
        name=settings.DB_NAME,
    )
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()