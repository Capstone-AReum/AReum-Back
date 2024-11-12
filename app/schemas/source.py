from pydantic import BaseModel
from typing import List
import datetime

class SourceBase(BaseModel):
    id: int
    url: str
    created_at: datetime.datetime

    class Config:
        orm_mode: True

class AlbumBase(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime

    class Config:
        orm_mode: True

class AlbumItems(AlbumBase):
    items: List[SourceBase] = []