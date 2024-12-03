from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
import secrets, mimetypes

from app.utils.s3_utils import upload_to_s3, get_url_to_image
from app.utils.sf3d_utils import call_ex_api
from app.models.source import Source, Album, Thumbnail
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
    content_type, _=mimetypes.guess_type(file.filename)
    if not content_type:
        content_type="image/png"

    extension=mimetypes.guess_extension(content_type)
    if not extension:
        extension=".png"

    random_name = secrets.token_urlsafe(16)
    file.filename=f"{random_name}{extension}"
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
    
async def upload_thumbnail(db: Session, source_id: int):
    source=get_source(db=db, source_id=source_id)
    if not source:
        raise HTTPException(status_code=404, detail="No such source")
    
    result = get_url_to_image(source.url)

    #분기 만들기 : 배경제거 or 3d 모델링
    filename=result["filename"]
    image_data=result["image_data"]
    content_type=result["content_type"]
    file_url=await call_ex_api(filename, image_data, content_type)

    #대표 이미지 DB 작업
    new_thumbnail=Thumbnail(source_id=source.id, album_id=source.album_id, model_url=file_url)
    db.add(new_thumbnail)
    db.commit()
    db.refresh(new_thumbnail)
    return file_url