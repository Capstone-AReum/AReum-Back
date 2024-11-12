from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

class SourceBase(BaseModel):
    id: int
    url: str

    class Config:
        orm_mode: True

class AlbumBase(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode: True

class AlbumItems(AlbumBase):
    items: List[SourceBase] = []