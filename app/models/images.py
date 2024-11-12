from sqlalchemy import Table, Column, String, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class BaseMin:
    id = Column(Integer, primary_key=True, index=True )
    created_at=Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at=Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp()) 

#매핑 테이블
album=Table(
    'album', Base.metadata,
    Column('uuid', Integer, ForeignKey('uuid.id')),
    Column('title', Integer, ForeignKey('memo.id'))
)

class UUID(BaseMin, Base):
    __tablename__="uuid"
    url=Column(String(255), nullable=False, unique=True)

    uuid_items=relationship("Memo", secondary=album, back_populates="items")

class Memo(BaseMin, Base):
    __tablename__="memo"
    title=Column(String(30), nullable=False)

    items=relationship("UUID", secondary=album, back_populates="uuid_items")