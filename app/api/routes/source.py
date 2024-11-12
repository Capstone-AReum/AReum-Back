from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.source import upload_album
from app.schemas.source import AlbumItems

router=APIRouter()

@router.post("/upload", response_model=AlbumItems)
async def upload_file(title: str, files: List[UploadFile] = File(...), db: Session = Depends(get_db)) -> dict:
    new_album=upload_album(db=db, title=title, files=files, path="sources")
    return new_album
