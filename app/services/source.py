from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
import secrets

from app.utils.s3_utils import upload_to_s3
from app.models.source import Source, Album
from app.schemas.source import SourceBase, SourceDetail, GalleryResponse

def get_source(db: Session, source_id: int):
    return db.query(Source).filter(Source.id==source_id).first()

def get_album(db: Session, album_id: int):
    return db.query(Album).filter(Album.id==album_id).first()
    
def get_source_detail(db: Session, source_id: int):
    source=get_source(db=db, source_id=source_id)
    if not source:
        raise HTTPException(status_code=404, detail="No such source")
    album=get_album(db=db, album_id=source.album_id)
    if not album:
        raise HTTPException(status_code=404, detail="No such album")
    return SourceDetail(id=source.id, url=source.url, created_at=source.created_at, title=album.title)

def get_all_source(page: int, db: Session):
    skip=(page-1)*10
    total_count=db.query(Source).count()
    images=db.query(Source).order_by(Source.created_at.desc()).offset(skip).limit(10).all()

    image_list = [SourceBase(id=image.id, url=image.url, created_at=image.created_at) for image in images]
    return GalleryResponse(images=image_list, total_count=total_count, page=page, per_page=10)

#random한 이름으로 이미지 이름 변경
def change_filename(file: UploadFile) -> UploadFile:
    random_name = secrets.token_urlsafe(16)
    file.filename=f"{random_name}.png"
    return file

def upload_album(db: Session, title: str, files: List[UploadFile], path: str):
    try:
        new_album=Album(title=title)
        db.add(new_album)
        db.commit()
    
        for file in files:
            opt_file=change_filename(file)
            file_url=upload_to_s3(opt_file, path)
            new_entry = Source(url=file_url, album_id=new_album.id)
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)
        db.refresh(new_album)
        return new_album
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))