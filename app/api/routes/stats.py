from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.stats import StatsBase
from app.services.source_query import get_all_albums

router=APIRouter()

#날짜별 기록 빈도 통계
@router.get("/albums", response_model=List[StatsBase])
async def get_number_of_albums(db: Session = Depends(get_db)):
    return get_all_albums(db)