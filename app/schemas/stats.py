from pydantic import BaseModel
from datetime import date

class StatsBase(BaseModel):
    date: date
    count : int

    class Config:
        orm_mode: True

class LocationBase(BaseModel):
    location: str
    count : int

    class Config:
        orm_mode: True