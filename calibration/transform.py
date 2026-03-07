import numpy as np
from scipy.spatial.transform import Rotation
from typing import Tuple, Optional, Dict


class RigidTransform:
    def __init__(self):
        self.matrix = np.eye(4)
        self.rotation = np.eye(3)
        self.translation = np.zeros(3)

    @staticmethod
    def estimate_svd(
        points_source: np.ndarray,
        points_target: np.ndarray
    ) -> 'RigidTransform':
        points_source = np.asarray(points_source)
        points_target = np.asarray(points_target)

        if len(points_source) != len(points_target):
            min_len = min(len(points_source), len(points_target))
            points_source = points_source[:min_len]
            points_target = points_target[:min_len]

        centroid_source = np.mean(points_source, axis=0)
        centroid_target = np.mean(points_target, axis=0)

        centered_source = points_source - centroid_source
        centered_target = points_target - centroid_target

        H = centered_source.T @ centered_target

        U, S, Vt = np.linalg.svd(H)

        R = Vt.T @ U.T

        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = Vt.T @ U.T

        t = centroid_target - R @ centroid_source

        transform = RigidTransform()
        transform.rotation = R
        transform.translation = t
        transform.matrix[:3, :3] = R
        transform.matrix[:3, 3] = t

        return transform

    @staticmethod
    def estimate_umeyama(
        points_source: np.ndarray,
        points_target: np.ndarray,
        with_scale: bool = False
    ) -> 'RigidTransform':
        points_source = np.asarray(points_source)
        points_target = np.asarray(points_target)

        assert points_source.shape == points_target.shape

        m, n = points_source.shape

        mean_s = np.mean(points_source, axis=0)
        mean_t = np.mean(points_target, axis=0)

        sigma_s = np.sum((points_source - mean_s) ** 2) / n

        centered_s = points_source - mean_s
        centered_t = points_target - mean_t

        sigma_t = np.sum((centered_t ** 2).sum(axis=1)) / n

        cov = (centered_t.T @ centered_s) / n

        U, D, Vh = np.linalg.svd(cov)

        S = np.eye(m)
        if np.linalg.det(U) * np.linalg.det(Vh) < 0:
            S[m - 1, m - 1] = -1

        R = U @ S @ Vh
        scale = np.trace(np.diag(D) @ S) / sigma_s if with_scale else 1.0

        t = mean_t - scale * (R @ mean_s)

        transform = RigidTransform()
        transform.rotation = R
        transform.translation = t
        transform.matrix[:3, :3] = scale * R
        transform.matrix[:3, 3] = t

        return transform

    def transform_points(self, points: np.ndarray) -> np.ndarray:
        points = np.asarray(points)
        if points.shape[-1] != 4:
            points_homogeneous = np.hstack([
                points,
                np.ones((points.shape[0], 1))
            ])
        else:
            points_homogeneous = points

        transformed = (self.matrix @ points_homogeneous.T).T
        return transformed[:, :3]

    def inverse(self) -> 'RigidTransform':
        transform_inv = RigidTransform()
        transform_inv.rotation = self.rotation.T
        transform_inv.translation = -self.rotation.T @ self.translation
        transform_inv.matrix[:3, :3] = self.rotation.T
        transform_inv.matrix[:3, 3] = transform_inv.translation
        return transform_inv

    def get_euler_angles(self, degrees: bool = True) -> np.ndarray:
        rot = Rotation.from_matrix(self.rotation)
        return rot.as_euler('xyz', degrees=degrees)

    def get_quaternion(self) -> np.ndarray:
        rot = Rotation.from_matrix(self.rotation)
        return rot.as_quat()

    def get_rotation_angle_axis(self) -> Tuple[float, np.ndarray]:
        rot = Rotation.from_matrix(self.rotation)
        angle = rot.magnitude()
        return angle, rot.as_rotvec()

    @classmethod
    def from_matrix(cls, matrix: np.ndarray) -> 'RigidTransform':
        transform = cls()
        transform.matrix = matrix
        transform.rotation = matrix[:3, :3]
        transform.translation = matrix[:3, 3]
        return transform

    @classmethod
    def from_euler(cls, euler: np.ndarray, translation: np.ndarray) -> 'RigidTransform':
        transform = cls()
        rot = Rotation.from_euler('xyz', euler)
        transform.rotation = rot.as_matrix()
        transform.translation = translation
        transform.matrix[:3, :3] = transform.rotation
        transform.matrix[:3, 3] = translation
        return transform

    @classmethod
    def from_quaternion(cls, quaternion: np.ndarray, translation: np.ndarray) -> 'RigidTransform':
        transform = cls()
        rot = Rotation.from_quat(quaternion)
        transform.rotation = rot.as_matrix()
        transform.translation = translation
        transform.matrix[:3, :3] = transform.rotation
        transform.matrix[:3, 3] = translation
        return transform

    def to_dict(self) -> dict:
        return {
            'matrix': self.matrix.tolist(),
            'rotation': self.rotation.tolist(),
            'translation': self.translation.tolist(),
            'euler_angles_deg': self.get_euler_angles(True).tolist(),
            'quaternion': self.get_quaternion().tolist()
        }

    def __str__(self) -> str:
        euler = self.get_euler_angles(True)
        return (
            f"RigidTransform:\n"
            f"  Rotation Matrix:\n{self.rotation}\n"
            f"  Translation: {self.translation}\n"
            f"  Euler Angles (deg): X={euler[0]:.2f}, Y={euler[1]:.2f}, Z={euler[2]:.2f}"
        )


def estimate_rigid_transform_least_squares(
    points_source: np.ndarray,
    points_target: np.ndarray,
    method: str = 'svd'
) -> RigidTransform:
    if method == 'svd':
        return RigidTransform.estimate_svd(points_source, points_target)
    elif method == 'umeyama':
        return RigidTransform.estimate_umeyama(points_source, points_target)
    else:
        raise ValueError(f"Unknown method: {method}")
