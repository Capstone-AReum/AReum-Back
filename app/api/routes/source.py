from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.source import upload_album, get_source_detail, get_all_source
from app.schemas.source import AlbumItems, GalleryResponse

router=APIRouter()

@router.post("/upload", response_model=AlbumItems)
async def upload_file(title: str, files: List[UploadFile] = File(...), db: Session = Depends(get_db)) -> dict:
    new_album=upload_album(db=db, title=title, files=files, path="sources")
    return new_album

@router.get("/all", response_model=GalleryResponse)
async def get_gallery(page: int, db: Session = Depends(get_db)):
    return get_all_source(page=page, db=db)

@router.get("/{source_id}/detail")
async def get_source(source_id: int, db: Session = Depends(get_db)) -> dict:
    source_detail=get_source_detail(db=db, source_id=source_id)
    return source_detail