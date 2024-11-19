import torch
import cv2
import numpy as np
from pathlib import Path

# 프로젝트 루트 경로를 PYTHONPATH에 추가
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LIGHTWEIGHT_DIR = PROJECT_ROOT / "lightweight-human-pose-estimation.pytorch"
CHECKPOINT_PATH = LIGHTWEIGHT_DIR / "checkpoint_iter_370000.pth"

# lightweight-human-pose-estimation 모델 경로 추가
import sys
sys.path.append(str(LIGHTWEIGHT_DIR))

# 필요한 모듈 임포트
from models.with_mobilenet import PoseEstimationWithMobileNet
from modules.keypoints import extract_keypoints, group_keypoints
from modules.load_state import load_state
from modules.pose import Pose
import demo


def generate_rect(image_path: str, checkpoint_path: str, output_dir: str = None) -> str:
    """
    Generate rectangle information for the input image using pose estimation.

    Args:
        image_path (str): Path to the input image.
        checkpoint_path (str): Path to the checkpoint file.
        output_dir (str, optional): Directory to save the generated rectangle file.

    Returns:
        str: Path to the generated rectangle file.

    Raises:
        FileNotFoundError: If the input image or checkpoint file is not found.
        RuntimeError: If the rectangle file is not generated successfully.
    """
    # Load the pose estimation model
    net = PoseEstimationWithMobileNet()

    if not Path(checkpoint_path).exists():
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")

    # GPU가 없는 경우 강제적으로 CPU를 사용
    device = torch.device("cpu")
    print(f"Using device: {device}")

    # 모델 로드 (CPU 전용)
    load_state(net, torch.load(checkpoint_path, map_location=device))
    net = net.to(device).eval()

    # Check if input image exists
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Input image not found: {image_path}")

    # Generate rectangle file
    output_path = image_path.with_name(f"{image_path.stem}_rect.txt")
    if output_dir:
        output_path = Path(output_dir) / output_path.name

    get_rect(net, [str(image_path)], 512, device)

    # Verify that the rectangle file was created
    if not output_path.exists():
        raise RuntimeError(f"Failed to generate rectangle file: {output_path}")

    return str(output_path)


def get_rect(net, images, height_size, device):
    """
    Generate bounding box rectangles for each pose in the images.

    Args:
        net: Trained pose estimation model.
        images (list): List of image file paths.
        height_size (int): Input height size for the model.
        device: PyTorch device (CPU or CUDA).

    Returns:
        None
    """
    net = net.to(device).eval()

    stride = 8
    upsample_ratio = 4
    num_keypoints = Pose.num_kpts

    for image in images:
        rect_path = image.replace('.%s' % (image.split('.')[-1]), '_rect.txt')
        img = cv2.imread(image, cv2.IMREAD_COLOR)
        heatmaps, pafs, scale, pad = demo.infer_fast(
            net, img, height_size, stride, upsample_ratio, cpu=True
        )  # CPU 강제 사용

        total_keypoints_num = 0
        all_keypoints_by_type = []
        for kpt_idx in range(num_keypoints):  # 19th for bg
            total_keypoints_num += extract_keypoints(
                heatmaps[:, :, kpt_idx], all_keypoints_by_type, total_keypoints_num
            )

        pose_entries, all_keypoints = group_keypoints(all_keypoints_by_type, pafs)
        for kpt_id in range(all_keypoints.shape[0]):
            all_keypoints[kpt_id, 0] = (all_keypoints[kpt_id, 0] * stride / upsample_ratio - pad[1]) / scale
            all_keypoints[kpt_id, 1] = (all_keypoints[kpt_id, 1] * stride / upsample_ratio - pad[0]) / scale

        rects = []
        for n in range(len(pose_entries)):
            if len(pose_entries[n]) == 0:
                continue
            valid_keypoints = []
            for kpt_id in range(num_keypoints):
                if pose_entries[n][kpt_id] != -1.0:  # Keypoint was found
                    x = int(all_keypoints[int(pose_entries[n][kpt_id]), 0])
                    y = int(all_keypoints[int(pose_entries[n][kpt_id]), 1])
                    valid_keypoints.append([x, y])

            valid_keypoints = np.array(valid_keypoints)
            if len(valid_keypoints) > 0:
                pmin = valid_keypoints.min(0)
                pmax = valid_keypoints.max(0)
                rects.append([pmin[0], pmin[1], pmax[0] - pmin[0], pmax[1] - pmin[1]])

        np.savetxt(rect_path, np.array(rects), fmt='%d')