from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.s3_utils import upload_to_s3

router=APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    try:
        file_url=upload_to_s3(file)
        return {"file_url": file_url}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))