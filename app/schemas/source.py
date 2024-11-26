from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import datetime

class SourceBase(BaseModel):
    id: int
    url: str
    created_at: datetime.datetime

    class Config:
        orm_mode: True

class SourceDetail(SourceBase):
    title: str

class AlbumBase(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime

    class Config:
        orm_mode: True

class AlbumItems(AlbumBase):
    items: List[SourceBase] = []

class GalleryResponse(BaseModel):
    images: List[SourceBase]
    total_count: int
    page: int
    per_page: int

    class Config:
        orm_mode: True
