import os
import cv2
import numpy as np
from rembg import remove
from PIL import Image
import io
import time

RESULT_FOLDER = 'static/results'
os.makedirs(RESULT_FOLDER, exist_ok=True)


async def process_image(file):
    file_path = os.path.join(RESULT_FOLDER, f"processed_{file.filename}")
    with open(file_path, 'wb') as f:
        f.write(await file.read())
    with open(file_path, 'rb') as input_file:
        result = remove(input_file.read())
    with open(file_path, 'wb') as output_file:
        output_file.write(result)
    return file_path


async def process_video(file):
    file_path = os.path.join(RESULT_FOLDER, file.filename)
    with open(file_path, 'wb') as f:
        f.write(await file.read())

    cap = cv2.VideoCapture(file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * 0.3)
    frame_count = 0
    processed_frame_count = 0
    success, frame = cap.read()

    while success:
        if frame_count % frame_interval == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)

            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            buffer.seek(0)
            processed_data = remove(buffer.getvalue())

            result_frame = Image.open(io.BytesIO(processed_data))
            result_path = os.path.join(RESULT_FOLDER, f"frame_{frame_count:04d}.png")
            result_frame.save(result_path)
            processed_frame_count += 1

        success, frame = cap.read()
        frame_count += 1

    cap.release()
    return file_path  # 이 경우 전체 동영상이 아닌 개별 프레임이 저장됨
