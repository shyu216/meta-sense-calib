import numpy as np
import cv2
from typing import Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class CameraIntrinsics:
    matrix: np.ndarray
    distortion: np.ndarray
    width: int = 0
    height: int = 0

    @classmethod
    def from_json(cls, data: dict):
        # 支持两种JSON格式：
        # 1. 直接包含matrix和distortion的格式
        # 2. README中描述的包含FocalLength、PrincipalPoint等的格式
        if 'matrix' in data and 'distortion' in data:
            # 格式1：直接包含矩阵
            return cls(
                matrix=np.array(data['matrix']),
                distortion=np.array(data['distortion']),
                width=data.get('width', 0),
                height=data.get('height', 0)
            )
        elif 'FocalLength' in data and 'PrincipalPoint' in data:
            # 格式2：README中描述的格式
            fx = data['FocalLength']['x']
            fy = data['FocalLength']['y']
            cx = data['PrincipalPoint']['x']
            cy = data['PrincipalPoint']['y']
            width = data['Resolution']['x'] if 'Resolution' in data else 0
            height = data['Resolution']['y'] if 'Resolution' in data else 0
            
            matrix = np.array([
                [fx, 0, cx],
                [0, fy, cy],
                [0, 0, 1]
            ], dtype=np.float64)
            
            # 默认为零畸变
            distortion = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
            
            return cls(
                matrix=matrix,
                distortion=distortion,
                width=width,
                height=height
            )
        else:
            raise ValueError("Invalid JSON format for camera intrinsics")

    def to_dict(self) -> dict:
        return {
            'matrix': self.matrix.tolist(),
            'distortion': self.distortion.tolist(),
            'width': self.width,
            'height': self.height
        }


class PoseEstimator:
    def __init__(self, intrinsics: CameraIntrinsics):
        self.intrinsics = intrinsics

    def estimate_pose(
        self,
        object_points: np.ndarray,
        image_points: np.ndarray
    ) -> Optional[Dict]:
        success, rvec, tvec = cv2.solvePnP(
            object_points,
            image_points,
            self.intrinsics.matrix,
            self.intrinsics.distortion,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return None

        rotation_matrix, _ = cv2.Rodrigues(rvec)

        return {
            'rvec': rvec,
            'tvec': tvec,
            'rotation_matrix': rotation_matrix,
            'success': True
        }

    def estimate_pose_gauss_newton(
        self,
        object_points: np.ndarray,
        image_points: np.ndarray,
        initial_rvec: Optional[np.ndarray] = None,
        initial_tvec: Optional[np.ndarray] = None,
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> Optional[Dict]:
        if initial_rvec is None or initial_tvec is None:
            result = self.estimate_pose(object_points, image_points)
            if result is None:
                return None
            rvec = result['rvec']
            tvec = result['tvec']
        else:
            rvec = initial_rvec.copy()
            tvec = initial_tvec.copy()

        object_points = np.asarray(object_points)
        image_points = np.asarray(image_points)

        for _ in range(max_iterations):
            R, _ = cv2.Rodrigues(rvec)
            projected = (R @ object_points.T + tvec).T

            z = projected[:, 2:3]
            z[z < 1e-6] = 1e-6

            jacobian = np.zeros((2 * len(object_points), 6))
            residuals = np.zeros(2 * len(object_points))

            fx = self.intrinsics.matrix[0, 0]
            fy = self.intrinsics.matrix[1, 1]
            cx = self.intrinsics.matrix[0, 2]
            cy = self.intrinsics.matrix[1, 2]

            for i, (P, p_img) in enumerate(zip(projected, image_points)):
                x, y, z_val = P
                u_proj = fx * x / z_val + cx
                v_proj = fy * y / z_val + cy

                residuals[2*i] = p_img[0] - u_proj
                residuals[2*i + 1] = p_img[1] - v_proj

                d_u_d_rx = -fx * x * y / (z_val * z_val)
                d_u_d_ry = fx * (1 + x * x / (z_val * z_val))
                d_u_d_tx = -fx / z_val
                d_u_d_ty = 0
                d_u_d_rz = fy * y / (z_val * z_val)

                d_v_d_rx = -fy * (1 + y * y / (z_val * z_val))
                d_v_d_ry = fy * x * y / (z_val * z_val)
                d_v_d_tx = 0
                d_v_d_ty = -fy / z_val
                d_v_d_rz = -fx * x / (z_val * z_val)

                jacobian[2*i, :] = [
                    d_u_d_rx, d_u_d_ry, d_u_d_rz, d_u_d_tx, d_u_d_ty, 0
                ]
                jacobian[2*i + 1, :] = [
                    d_v_d_rx, d_v_d_ry, d_v_d_rz, 0, d_v_d_ty, d_v_d_rz
                ]

            delta = np.linalg.lstsq(jacobian, residuals, rcond=None)[0]

            rvec += delta[:3]
            tvec += delta[3:]

            if np.linalg.norm(delta) < tolerance:
                break

        rotation_matrix, _ = cv2.Rodrigues(rvec)

        return {
            'rvec': rvec,
            'tvec': tvec,
            'rotation_matrix': rotation_matrix,
            'success': True
        }

    def project_points(
        self,
        object_points: np.ndarray,
        rvec: np.ndarray,
        tvec: np.ndarray
    ) -> np.ndarray:
        projected, _ = cv2.projectPoints(
            object_points,
            rvec,
            tvec,
            self.intrinsics.matrix,
            self.intrinsics.distortion
        )
        return projected.squeeze()

    def compute_reprojection_error(
        self,
        object_points: np.ndarray,
        image_points: np.ndarray,
        rvec: np.ndarray,
        tvec: np.ndarray
    ) -> float:
        projected = self.project_points(object_points, rvec, tvec)
        errors = np.linalg.norm(projected - image_points, axis=1)
        return np.mean(errors)

    def transform_to_camera_coord(
        self,
        object_points: np.ndarray,
        rvec: np.ndarray,
        tvec: np.ndarray
    ) -> np.ndarray:
        R, _ = cv2.Rodrigues(rvec)
        camera_points = (R @ object_points.T + tvec).T
        return camera_points

    @staticmethod
    def rotation_to_euler(R: np.ndarray) -> np.ndarray:
        sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
        singular = sy < 1e-6

        if not singular:
            x = np.arctan2(R[2, 1], R[2, 2])
            y = np.arctan2(-R[2, 0], sy)
            z = np.arctan2(R[1, 0], R[0, 0])
        else:
            x = np.arctan2(-R[1, 2], R[1, 1])
            y = np.arctan2(-R[2, 0], sy)
            z = 0

        return np.array([x, y, z])

    @staticmethod
    def euler_to_rotation(euler: np.ndarray) -> np.ndarray:
        from scipy.spatial.transform import Rotation
        return Rotation.from_euler('xyz', euler).as_matrix()
