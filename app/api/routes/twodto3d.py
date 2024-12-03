from fastapi import APIRouter, UploadFile, File
from app.utils.sf3d_utils import call_ex_api

router=APIRouter()

#SF3D API 호출
@router.post("/sf3d", response_model=str)
async def upload_file(files: UploadFile = File(...)) -> dict:
    file_url=await call_ex_api(files=files)
    return file_url