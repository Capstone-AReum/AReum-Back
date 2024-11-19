from fastapi import APIRouter, HTTPException, UploadFile, File
from app.utils.pose_estimation import generate_rect
import subprocess
from pathlib import Path
import os, sys
router = APIRouter()

# 기본 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # AReum-Back 루트 디렉토리
PIFUHD_DIR = BASE_DIR / "pifuhd"
SAMPLE_IMAGES_DIR = PIFUHD_DIR / "sample_images"
RESULTS_DIR = PIFUHD_DIR / "results"
PIFUHD_CHECKPOINT_PATH = PIFUHD_DIR / "checkpoints" / "pifuhd.pt"  # PIFuHD 체크포인트
LIGHTWEIGHT_CHECKPOINT_PATH = BASE_DIR / "lightweight-human-pose-estimation.pytorch" / "checkpoint_iter_370000.pth"  # Lightweight-Human-Pose-Estimation 체크포인트
SIMPLE_TEST_PATH = PIFUHD_DIR / "apps" / "simple_test.py"

# 디렉토리 생성
SAMPLE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload_run/")
async def upload_and_run(file: UploadFile = File(...)):
    """
    업로드된 이미지를 저장하고 simple_test.py 실행
    """
    # 파일 저장
    file_location = SAMPLE_IMAGES_DIR / file.filename
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # 사각형 정보 생성
    try:
        rect_file = generate_rect(
            image_path=str(file_location),
            checkpoint_path=str(LIGHTWEIGHT_CHECKPOINT_PATH)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate rectangle data: {str(e)}")

    # simple_test.py 실행
    try:
        python_executable = Path(sys.executable)
        subprocess.run(
            [
                str(python_executable),
                str(SIMPLE_TEST_PATH),
                "--input_path", str(SAMPLE_IMAGES_DIR),
                "--out_path", str(RESULTS_DIR),
                "--ckpt_path", str(PIFUHD_CHECKPOINT_PATH),  # PIFuHD 체크포인트
                "--resolution", "512",
                "--use_rect"
            ],
            check=True
        )
        return {
            "status": "Model executed successfully",
            "results_dir": str(RESULTS_DIR),
            "rect_file": rect_file
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to run model: {str(e)}")
