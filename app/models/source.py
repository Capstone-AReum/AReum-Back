from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import pytz

kst_tz=pytz.timezone("Asia/Seoul")

class BaseMin:
    id = Column(Integer, primary_key=True, index=True )
    created_at=Column(DateTime, nullable=False, default=lambda: datetime.now(kst_tz))
    updated_at=Column(DateTime, nullable=False, default=lambda: datetime.now(kst_tz), onupdate=lambda: datetime.now(kst_tz)) 

class Source(BaseMin, Base):
    __tablename__="sources"
    url=Column(String(255), nullable=False, unique=True)
    album_id=Column(Integer, ForeignKey('albums.id'))

    owner=relationship("Album", back_populates="items")

class Album(BaseMin, Base):
    __tablename__="albums"
    title=Column(String(30), nullable=False)
    location=Column(String(30), nullable=True)

    items=relationship("Source", back_populates="owner")

class Thumbnail(BaseMin, Base):
    __tablename__="thumbnails"
    source_id=Column(Integer, ForeignKey('sources.id'), nullable=False)
    album_id=Column(Integer, ForeignKey('albums.id'), nullable=False)
    model_url=Column(String(255), nullable=False, unique=True)

    source = relationship("Source", backref=None)
    album = relationship("Album", backref=None)