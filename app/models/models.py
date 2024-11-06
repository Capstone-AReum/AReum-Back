from sqlalchemy import Column, String, Integer, DateTime, func
from app.database import Base

class BaseMin:
    id = Column(Integer, primary_key=True, index=True )
    created_at=Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at=Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp()) 
