from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.stats import StatsBase, LocationBase
from app.services.source_query import get_all_albums, group_by_locations

router=APIRouter()

#날짜별 기록 빈도 통계
@router.get("/albums", response_model=List[StatsBase])
async def get_number_of_albums(db: Session = Depends(get_db)):
    return get_all_albums(db)

#장소별 통계
@router.get("/locations", response_model=List[LocationBase])
async def get_stats_of_locations(db: Session = Depends(get_db)):
    return group_by_locations(db)