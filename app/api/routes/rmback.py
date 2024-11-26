from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.media_service import process_image, process_video, create_rmback, update_rmback_status
from app.schemas.rmback import RmbackResponse

router = APIRouter()

@router.post("/rmback", response_model=RmbackResponse)
async def rmback(url: str, db: Session = Depends(get_db)):
    """
    Process media file (image or video) based on the input URL.
    """
    file_ext = url.split(".")[-1].lower()
    allowed_image_exts = {"png", "jpg", "jpeg"}
    allowed_video_exts = {"mp4", "avi", "mov", "mkv"}

    # Determine media type
    if file_ext in allowed_image_exts:
        media_type = "image"
    elif file_ext in allowed_video_exts:
        media_type = "video"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Create a new database record before processing
    new_rmback = create_rmback(db=db, input_url=url, media_type=media_type)

    try:
        # Process the media file
        if media_type == "image":
            output_url = await process_image(url)  # 단일 URL
        elif media_type == "video":
            output_url = await process_video(url)  # 리스트 URL

        # Update the record with success status
        update_rmback_status(db=db, rmback_id=new_rmback.id, status="completed", output_url=output_url)
    except Exception as e:
        # Update the record with failure status if an error occurs
        update_rmback_status(db=db, rmback_id=new_rmback.id, status="failed")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    # Return the response
    return RmbackResponse(
        id=new_rmback.id,
        input_url=url,
        output_url=output_url,
        status="completed",
        media_type=media_type,
        created_at=new_rmback.created_at
    )
