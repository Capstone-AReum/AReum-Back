from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.services.source_query import get_source_detail, get_all_source
from app.services.source_command import upload_album, upload_thumbnail, upload_voice_file, is_mp3
from app.schemas.source import AlbumItems, GalleryResponse, SourceDetail, UrlResponse

router=APIRouter()

#이미지 업로드
@router.post("/upload", response_model=AlbumItems)
async def upload_file(
    title: Optional[str] = Query("...") , 
    location: Optional[str] = Query("기타") ,
    files: List[UploadFile] = File(...), 
    db: Session = Depends(get_db)
) -> dict:
    new_album=upload_album(db=db, title=title, location=location, files=files, path="sources")
    return new_album

#대표 이미지 선택 및 모델링 진행
@router.post("/thumbnails", response_model= UrlResponse)
async def check_thumbnail(source_id: int, db: Session = Depends(get_db)):
    return await upload_thumbnail(db=db, source_id=source_id)

#음성 업로드
@router.patch("/voice", response_model=str)
async def upload_mp3( thumbnail_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_url=await upload_voice_file(db=db, thumbnail_id=thumbnail_id, file=file)
    return file_url

#앨범 전체 조회
@router.get("/all", response_model=List[GalleryResponse])
async def get_gallery(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1), db: Session = Depends(get_db)):
    return get_all_source(skip=skip, limit=limit, db=db)

#이미지 상세 조회
@router.get("/{source_id}/details", response_model=SourceDetail)
async def get_source(source_id: int, db: Session = Depends(get_db)):
    return get_source_detail(db=db, source_id=source_id)