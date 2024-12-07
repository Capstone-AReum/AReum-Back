from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
import cv2, subprocess, os, io
import numpy as np
import secrets, mimetypes

from app.utils.s3_utils import upload_to_s3, get_url_to_image
from app.utils.sf3d_utils import call_ex_api
from app.models.source import Source, Album, Thumbnail
from dotenv import load_dotenv

load_dotenv()

def get_source(db: Session, source_id: int):
    return db.query(Source).filter(Source.id==source_id).first()

def get_thumbnail(db: Session, thumbnail_id: int):
    return db.query(Thumbnail).filter(Thumbnail.id==thumbnail_id).first()

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

def upload_album(db: Session, title: str, location: str, files: List[UploadFile], path: str):
    try:
        new_album=Album(title=title, location=location)
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
    return { "id": new_thumbnail.id, "file_url": file_url }

#이미지 해상도 validation    
async def resolution_valid(byte_image : bytes):
    image_array=np.frombuffer(byte_image, np.uint8)
    image=cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)

    height, width=image.shape[:2]
    
    if(height > 2048 or width > 2048):
        raise HTTPException(status_code=422, detail="Image resoultion is too big")
    
#음성 파일 확장자 validation
async def is_mp3(file: UploadFile):
    content_type, _=mimetypes.guess_type(file.filename)
    extension=mimetypes.guess_extension(content_type)
    if extension==".mp3":
        return "mp3"
    elif extension==".mp4":
        return await mp4_to_mp3(file)
    else:
        raise HTTPException(status_code=422, detail="file.mp3 or file.mp4 only accepted")

#mp4 -> mp3 변환 by FFmpeg
async def mp4_to_mp3(file: UploadFile):
    ffmpeg_path=os.getenv("PATH_CONVERT_VIDEO", "/usr/bin/ffmpeg")
    input_video_path=f"temp_{file.filename}"
    #mp4파일 임시 파일로 저장
    with open(input_video_path, "wb") as f:
        f.write(await file.read())
    
    local_mp3_path = "temp_output.mp3"
    try:
        subprocess.run(
            [ffmpeg_path, '-i', input_video_path, '-ab', '192k', '-vn', '-acodec', 'libmp3lame', local_mp3_path],
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_video_path):
            os.remove(input_video_path)
    return "mp4"

#파일을 바이트로 읽어 UploadFile로 변환
async def convert_to_Uploadfile() -> UploadFile:
    with open("temp_output.mp3", "rb") as f:
        file_data = f.read()

    file_like = io.BytesIO(file_data)
    file_like.seek(0)

    if os.path.exists("temp_output.mp3"):
        os.remove("temp_output.mp3")

    return UploadFile(filename="temp_output.mp3", file=file_like)

async def upload_voice_file(db: Session, thumbnail_id: int, file: UploadFile):
    try:
        target_Thumbnail=get_thumbnail(db=db, thumbnail_id=thumbnail_id)
        if not target_Thumbnail:
            raise HTTPException(status_code=404, detail="No such thumbnail")
        
        #file validation
        file_type=await is_mp3(file=file)
        if file_type=="mp3":
            new_file=change_filename(file)
            file_url=upload_to_s3(new_file, "sounds")
        elif file_type=="mp4":
            converted_file=await convert_to_Uploadfile()
            new_file=change_filename(converted_file)
            file_url=upload_to_s3(new_file, "sounds")
        else:
            raise HTTPException(status_code=500, detail="File validation Failed")
        
        target_Thumbnail.voice_url = file_url
        db.commit()
        db.refresh(target_Thumbnail)
        return file_url
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))