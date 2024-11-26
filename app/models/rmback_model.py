from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey
from app.database import Base
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship

class BaseMin:
    id = Column(Integer, primary_key=True, index=True )
    created_at=Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at=Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

### 배경제거
class Rmback(BaseMin, Base):
    __tablename__ = "rmback"
    input_url = Column(String(255), nullable=False)  # 원본 파일 URL
    output_url = Column(String(255), nullable=True)  # 처리된 파일의 S3 URL
    status = Column(String(50), default="pending")  # 처리 상태: pending, completed, failed
    media_type = Column(String(50), nullable=False)  # "image" 또는 "video"

