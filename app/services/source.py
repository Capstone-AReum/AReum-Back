from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
import secrets

from app.utils.s3_utils import upload_to_s3
from app.models.source import Source, Album

def get_source(db: Session, source_id: int):
    return db.query(Source).filter(Source.id==source_id).first()

def get_album(db: Session, album_id: int):
    return db.query(Album).filter(Album.id==album_id).first()

#random한 이름으로 이미지 이름 변경
def change_filename(file: UploadFile) -> UploadFile:
    random_name = secrets.token_urlsafe(16)
    file.filename=f"{random_name}.jpeg"
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