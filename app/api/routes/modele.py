from fastapi import APIRouter, UploadFile, File
import os
import sys
import torch
from pifuhd.apps.recon import gen_mesh, gen_mesh_imgColor
from pifuhd.lib.model import HGPIFuMRNet, HGPIFuNetwNML
from pifuhd.lib.options import BaseOptions

router = APIRouter()
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "static/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 서브모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '../../pifuhd'))

# 모델 및 옵션 설정
cuda = torch.device("cuda" if torch.cuda.is_available() else "cpu")
parser = BaseOptions()

@router.post("/generate-3d-model")
async def generate_3d_model(file: UploadFile = File(...)):
    # 업로드 파일을 저장
    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(image_path, "wb") as f:
        f.write(await file.read())

    # .obj 파일이 저장될 경로 설정
    output_path = os.path.join(OUTPUT_FOLDER, f"{file.filename.split('.')[0]}.obj")

    # 모델 초기화 및 체크포인트 로드
    opt = parser.parse([])
    opt.load_netMR_checkpoint_path = "./pifuhd/checkpoints/pifuhd.pt"
    opt.dataroot = UPLOAD_FOLDER
    opt.results_path = OUTPUT_FOLDER
    opt.resolution = 512

    # 모델 초기화
    netG = HGPIFuNetwNML(opt).to(cuda)
    netMR = HGPIFuMRNet(opt, netG).to(cuda)
    netMR.load_state_dict(torch.load(opt.load_netMR_checkpoint_path, map_location=cuda))

    # 이미지 파일로 기본 데이터를 구성
    test_data = {
        'img': torch.zeros(1, 3, opt.resolution, opt.resolution).to(cuda),  # 임시 이미지 텐서
        'img_512': torch.zeros(1, 3, 512, 512).to(cuda),  # 기본 크기의 이미지 텐서
        'calib': torch.eye(4).unsqueeze(0).to(cuda),  # 캘리브레이션 텐서
        'b_min': torch.tensor([-1, -1, -1]).to(cuda),
        'b_max': torch.tensor([1, 1, 1]).to(cuda),
    }

    # 각 함수 호출하여 .obj 파일 생성
    gen_mesh(opt.resolution, netMR, cuda, test_data, output_path)  # 기본 메쉬 생성
    gen_mesh_imgColor(opt.resolution, netMR, cuda, test_data, output_path)  # 컬러 메쉬 생성

    return {"message": "3D model generated", "path": output_path}
