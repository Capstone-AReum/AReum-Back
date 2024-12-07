from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
import cv2
import numpy as np
import secrets, mimetypes

from app.utils.s3_utils import upload_to_s3, get_url_to_image
from app.utils.sf3d_utils import call_ex_api
from app.models.source import Source, Album, Thumbnail

def get_source(db: Session, source_id: int):
    return db.query(Source).filter(Source.id==source_id).first()

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
    filename=result["filename"]
    image_data=result["image_data"]
    content_type=result["content_type"]
    
    await resolution_valid(image_data)
    file_url=await call_ex_api(filename, image_data, content_type)

    #대표 이미지 DB 작업
    new_thumbnail=Thumbnail(source_id=source.id, album_id=source.album_id, model_url=file_url)
    db.add(new_thumbnail)
    db.commit()
    db.refresh(new_thumbnail)
    return file_url

#이미지 해상도 validation    
async def resolution_valid(byte_image : bytes):
    image_array=np.frombuffer(byte_image, np.uint8)
    image=cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)

    height, width=image.shape[:2]
    
    if(height > 2048 or width > 2048):
        raise HTTPException(status_code=422, detail="Image resoultion is too big")