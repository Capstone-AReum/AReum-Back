from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.source import upload_album, get_source_detail, get_all_source, upload_thumbnail
from app.schemas.source import AlbumItems, GalleryResponse, SourceDetail

router=APIRouter()

#이미지 업로드
@router.post("/upload", response_model=AlbumItems)
async def upload_file(title: str, files: List[UploadFile] = File(...), db: Session = Depends(get_db)) -> dict:
    new_album=upload_album(db=db, title=title, files=files, path="sources")
    return new_album

#앨범 전체 조회
@router.get("/all", response_model=GalleryResponse)
async def get_gallery(page: int, db: Session = Depends(get_db)):
    return get_all_source(page=page, db=db)

#이미지 상세 조회
@router.get("/{source_id}/details", response_model=SourceDetail)
async def get_source(source_id: int, db: Session = Depends(get_db)):
    return get_source_detail(db=db, source_id=source_id)

#대표 이미지 선택 및 모델링 진행
@router.post("/thumbnails", response_model=str)
async def check_thumbnail(source_id: int, db: Session = Depends(get_db)):
    return await upload_thumbnail(db=db, source_id=source_id)