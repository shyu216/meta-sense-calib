import os
import json
import time
import glob
import numpy as np
import cv2
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field

from .chessboard import ChessboardDetector
from .pose import PoseEstimator, CameraIntrinsics
from .transform import RigidTransform


@dataclass
class CalibrationConfig:
    chessboard_size: Tuple[int, int] = (9, 6)
    square_size_mm: float = 36.0
    gamma_correction: bool = False
    gamma_value: float = 2.2
    image_scale: float = 1.0
    min_valid_frames: int = 3


@dataclass
class CalibrationResult:
    transformation_matrix: np.ndarray
    rotation_matrix: np.ndarray
    translation_vector: np.ndarray
    mean_error: float
    std_error: float
    max_error: float
    min_error: float
    valid_frame_count: int
    total_frame_count: int
    camera1_intrinsics: Optional[CameraIntrinsics] = None
    camera2_intrinsics: Optional[CameraIntrinsics] = None
    euler_angles: np.ndarray = field(default_factory=lambda: np.zeros(3))


class Calibrator:
    def __init__(
        self,
        camera1_intrinsics: Optional[CameraIntrinsics] = None,
        camera2_intrinsics: Optional[CameraIntrinsics] = None,
        intrinsics_rs: Optional[str] = None,  # RealSense内参JSON文件路径
        intrinsics_q3: Optional[str] = None,  # Quest3内参JSON文件路径
        config: Optional[CalibrationConfig] = None
    ):
        # 支持从JSON文件路径加载内参
        if intrinsics_rs:
            self.camera1_intrinsics = load_intrinsics_from_json(intrinsics_rs)
        else:
            self.camera1_intrinsics = camera1_intrinsics
        
        if intrinsics_q3:
            self.camera2_intrinsics = load_intrinsics_from_json(intrinsics_q3)
        else:
            self.camera2_intrinsics = camera2_intrinsics
            
        self.config = config or CalibrationConfig()

        self.detector = ChessboardDetector(
            pattern_size=self.config.chessboard_size,
            square_size=self.config.square_size_mm,
            need_gamma_correction=self.config.gamma_correction,
            gamma_value=self.config.gamma_value
        )

        self.pose_estimator1 = None
        self.pose_estimator2 = None

        self._setup_pose_estimators()

    def _setup_pose_estimators(self):
        if self.camera1_intrinsics:
            self.pose_estimator1 = PoseEstimator(self.camera1_intrinsics)
        if self.camera2_intrinsics:
            self.pose_estimator2 = PoseEstimator(self.camera2_intrinsics)

    def calibrate(
        self,
        image_folder: str,
        camera1_tag: str = 'rs',
        camera2_tag: str = 'q3',
        output_dir: Optional[str] = None,
        visualize: bool = False
    ) -> CalibrationResult:
        if output_dir is None:
            output_dir = f'outputs/calibration/{int(time.time())}'
        os.makedirs(output_dir, exist_ok=True)

        image_files1 = sorted(glob.glob(os.path.join(image_folder, f'*{camera1_tag}*.png')))
        image_files2 = sorted(glob.glob(os.path.join(image_folder, f'*{camera2_tag}*.png')))

        print(f"[Calibrator] Found {len(image_files1)} {camera1_tag} images")
        print(f"[Calibrator] Found {len(image_files2)} {camera2_tag} images")

        min_len = min(len(image_files1), len(image_files2))

        matched_points1 = []
        matched_points2 = []
        valid_frames = []

        for i in range(min_len):
            result1 = self.detector.detect_corners(image_files1[i], visualize=False)
            result2 = self.detector.detect_corners(image_files2[i], visualize=False)

            if result1 is None or result2 is None:
                print(f"[Calibrator] Frame {i}: Detection failed")
                continue

            pose1 = self.pose_estimator1.estimate_pose(
                result1['object_points'],
                result1['image_points']
            )
            pose2 = self.pose_estimator2.estimate_pose(
                result2['object_points'],
                result2['image_points']
            )

            if pose1 is None or pose2 is None:
                print(f"[Calibrator] Frame {i}: PnP failed")
                continue

            points1_cam = self.pose_estimator1.transform_to_camera_coord(
                result1['object_points'],
                pose1['rvec'],
                pose1['tvec']
            )
            points2_cam = self.pose_estimator2.transform_to_camera_coord(
                result2['object_points'],
                pose2['rvec'],
                pose2['tvec']
            )

            matched_points1.extend(points1_cam)
            matched_points2.extend(points2_cam)
            valid_frames.append(i)

            if visualize:
                img1_vis = cv2.drawChessboardCorners(
                    result1['image'].copy(),
                    self.config.chessboard_size,
                    result1['image_points'],
                    True
                )
                img2_vis = cv2.drawChessboardCorners(
                    result2['image'].copy(),
                    self.config.chessboard_size,
                    result2['image_points'],
                    True
                )
                cv2.imshow(f'{camera1_tag} Frame {i}', img1_vis)
                cv2.imshow(f'{camera2_tag} Frame {i}', img2_vis)
                cv2.waitKey(100)

        cv2.destroyAllWindows()

        if len(valid_frames) < self.config.min_valid_frames:
            raise ValueError(
                f"Not enough valid frames: {len(valid_frames)} < {self.config.min_valid_frames}"
            )

        print(f"[Calibrator] Valid frames: {len(valid_frames)}")

        transform = RigidTransform.estimate_svd(
            np.array(matched_points1),
            np.array(matched_points2)
        )

        points1_array = np.array(matched_points1)
        points2_array = np.array(matched_points2)

        transformed = transform.transform_points(points1_array)
        errors = np.linalg.norm(transformed - points2_array, axis=1)

        mean_error = np.mean(errors)
        std_error = np.std(errors)
        max_error = np.max(errors)
        min_error = np.min(errors)

        print(f"[Calibrator] Registration error:")
        print(f"  Mean: {mean_error:.3f} mm")
        print(f"  Std:  {std_error:.3f} mm")
        print(f"  Max:  {max_error:.3f} mm")
        print(f"  Min:  {min_error:.3f} mm")

        result = CalibrationResult(
            transformation_matrix=transform.matrix,
            rotation_matrix=transform.rotation,
            translation_vector=transform.translation,
            mean_error=mean_error,
            std_error=std_error,
            max_error=max_error,
            min_error=min_error,
            valid_frame_count=len(valid_frames),
            total_frame_count=min_len,
            camera1_intrinsics=self.camera1_intrinsics,
            camera2_intrinsics=self.camera2_intrinsics,
            euler_angles=transform.get_euler_angles(True)
        )

        self._save_results(result, output_dir)

        return result

    def _save_results(self, result: CalibrationResult, output_dir: str):
        npz_path = os.path.join(output_dir, 'calibration_result.npz')
        np.savez(
            npz_path,
            transformation_matrix=result.transformation_matrix,
            rotation_matrix=result.rotation_matrix,
            translation_vector=result.translation_vector,
            mean_error=result.mean_error,
            std_error=result.std_error,
            max_error=result.max_error,
            min_error=result.min_error,
            valid_frame_count=result.valid_frame_count,
            total_frame_count=result.total_frame_count,
            euler_angles=result.euler_angles
        )
        print(f"[Calibrator] Results saved to {npz_path}")

        json_dict = {
            'transformation_matrix': result.transformation_matrix.tolist(),
            'rotation_matrix': result.rotation_matrix.tolist(),
            'translation_vector': result.translation_vector.tolist(),
            'mean_error_mm': float(result.mean_error),
            'std_error_mm': float(result.std_error),
            'max_error_mm': float(result.max_error),
            'min_error_mm': float(result.min_error),
            'valid_frame_count': result.valid_frame_count,
            'total_frame_count': result.total_frame_count,
            'euler_angles_deg': result.euler_angles.tolist(),
            'camera1_intrinsics': self.camera1_intrinsics.to_dict() if self.camera1_intrinsics else None,
            'camera2_intrinsics': self.camera2_intrinsics.to_dict() if self.camera2_intrinsics else None
        }

        json_path = os.path.join(output_dir, 'calibration_result.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_dict, f, indent=2)
        print(f"[Calibrator] Results saved to {json_path}")


def load_intrinsics_from_json(json_path: str) -> CameraIntrinsics:
    with open(json_path, 'r') as f:
        data = json.load(f)
    return CameraIntrinsics.from_json(data)
