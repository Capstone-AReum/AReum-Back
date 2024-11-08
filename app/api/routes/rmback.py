from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ...services.media_service import process_image, process_video
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]
    allowed_image_exts = {'png', 'jpg', 'jpeg'}
    allowed_video_exts = {'mp4', 'avi', 'mov', 'mkv'}

    if file_ext in allowed_image_exts:
        result_path = await process_image(file)
    elif file_ext in allowed_video_exts:
        result_path = await process_video(file)
    else:
        return {"error": "Invalid file format. Please upload an image or video file."}

    return RedirectResponse(url=f"/result?filename={os.path.basename(result_path)}")

@router.get("/result", response_class=HTMLResponse)
async def show_result(request: Request, filename: str):
    return templates.TemplateResponse("result.html", {"request": request, "filename": filename})
