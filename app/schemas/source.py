from pydantic import BaseModel
from typing import List
import datetime
from datetime import date

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
    location: str
    created_at: datetime.datetime

    class Config:
        orm_mode: True

class AlbumItems(AlbumBase):
    items: List[SourceBase] = []

class GalleryResponse(BaseModel):
    id: int
    url: str
    created_at: date

    class Config:
        orm_mode: True

class UrlResponse(BaseModel):
    id: int
    file_url: str

    class Config:
        orm_mode: True