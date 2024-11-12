from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.utils.s3_utils import upload_to_s3
from sqlalchemy.orm import Session
from typing import List
import secrets

from app.models.images import UUID, Memo
from app.database import get_db

router=APIRouter()

#random한 이름으로 이미지 이름 변경
def change_filename(file: UploadFile) -> UploadFile:
    random_name = secrets.token_urlsafe(16)
    file.filename=f"{random_name}.jpeg"
    return file

@router.post("/upload")
async def upload_file(title: str, files: List[UploadFile] = File(...), db: Session = Depends(get_db)) -> dict:
    path="sources"
    new_memo=Memo(title=title)
    
    try:
        file_objects = []
        for file in files:
            opt_file=change_filename(file)
            file_url=upload_to_s3(opt_file, path)
            new_entry = UUID(url=file_url)
            new_entry.title=[new_memo]
            db.add(new_entry)
            file_objects.append(new_entry)
        new_memo.items = file_objects
        db.add(new_memo)
        db.commit()
        return {"msg" : "success"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))