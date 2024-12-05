import os
import cv2
import io
import mimetypes
import requests
from rembg import remove
from PIL import Image
from sqlalchemy.orm import Session
from typing import Optional, List
from app.config import s3_client
from app.models.rmback_model import Rmback
from app.utils.s3_utils import upload_to_s3

class FileWrapper:
    def __init__(self, file_obj, filename):
        self.file = file_obj
        self.filename = filename

def create_rmback(db: Session, input_url: str, media_type: str) -> Rmback:
    """
    데이터베이스에 새로운 Rmback 레코드 생성
    """
    new_rmback = Rmback(input_url=input_url, media_type=media_type, status="pending")
    db.add(new_rmback)
    db.commit()
    db.refresh(new_rmback)
    return new_rmback

def update_rmback_status(db: Session, rmback_id: int, status: str, output_url: Optional[str] = None) -> Rmback:
    """
    Update the status and output URL of an Rmback record.
    """
    rmback = db.query(Rmback).filter(Rmback.id == rmback_id).first()
    if not rmback:
        raise ValueError("Rmback record not found")
    rmback.status = status
    if output_url:
        rmback.output_url = output_url
    db.commit()
    db.refresh(rmback)
    return rmback


async def process_image(url: str) -> str:
    """
    Process an image by removing its background and uploading to S3.
    Args:
        url (str): The input URL of the image.
    Returns:
        str: The S3 URL of the processed image.
    """
    try:
        # Step 1: Download the image from the provided URL
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Step 2: Determine the original file extension
        content_type = response.headers.get("Content-Type")
        if not content_type:
            raise RuntimeError("Unable to determine Content-Type from the URL response.")

        # Guess the file extension based on the content type
        extension = mimetypes.guess_extension(content_type)
        if not extension:
            raise RuntimeError("Unable to determine file extension from Content-Type.")

        # Step 3: Remove the background from the image
        processed_data = remove(response.content)

        # Step 4: Set the file name for the processed image
        file_name = url.split("/")[-1].split(".")[0] + f"_processed{extension}"

        # Step 5: Prepare a file-like object for the processed data
        file_like = io.BytesIO(processed_data)

        # Step 6: Wrap the file-like object with a filename
        file_like.name = file_name  # Assign the filename attribute
        wrapped_file = FileWrapper(file_like, file_name)

        # Step 7: Upload the processed file to S3
        s3_path = "rmback"  # S3 folder path
        file_url = upload_to_s3(file=wrapped_file, path=s3_path)

        return file_url
    except Exception as e:
        raise RuntimeError(f"Image processing failed: {str(e)}")



async def process_video(url: str) -> List[str]:
    """
    Process a video by extracting frames, removing backgrounds, and uploading frames to S3.
    Args:
        url (str): The input URL of the video.
    Returns:
        List[str]: A list of S3 URLs for the processed frames.
    """
    try:
        # Step 1: Download the video from URL
        video_response = requests.get(url, stream=True)
        video_response.raise_for_status()

        # Step 2: Load video into OpenCV
        video_bytes = io.BytesIO(video_response.content)
        cap = cv2.VideoCapture(video_bytes)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = max(1, int(fps * 0.3))
        frame_count = 0
        processed_frame_urls = []

        success, frame = cap.read()
        while success:
            if frame_count % frame_interval == 0:
                try:
                    # Convert frame to PIL Image
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)

                    # Remove background
                    buffer = io.BytesIO()
                    pil_image.save(buffer, format="PNG")
                    buffer.seek(0)
                    processed_data = remove(buffer.getvalue())

                    # Create file-like object with filename
                    file_name = f"frame_{frame_count:04d}_processed.png"
                    file_like = io.BytesIO(processed_data)
                    file_like.name = file_name  # Assign filename for upload_to_s3

                    # Upload processed frame to S3
                    s3_path = "processed/videos"  # S3 folder path for video frames
                    frame_url = upload_to_s3(
                        file=FileWrapper(file_like, file_name),
                        path=s3_path
                    )
                    processed_frame_urls.append(frame_url)
                except Exception as frame_error:
                    print(f"Error processing frame {frame_count}: {frame_error}")

            success, frame = cap.read()
            frame_count += 1

        # Release video capture
        cap.release()

        return processed_frame_urls
    except Exception as e:
        raise Exception(f"Video processing failed: {str(e)}")
