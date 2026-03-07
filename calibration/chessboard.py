import numpy as np
import cv2
from typing import Tuple, Optional, Dict


class ChessboardDetector:
    def __init__(
        self,
        pattern_size: Tuple[int, int] = (9, 6),
        square_size: float = 36.0,
        need_gamma_correction: bool = False,
        gamma_value: float = 2.2
    ):
        self.pattern_size = pattern_size
        self.square_size = square_size
        self.need_gamma_correction = need_gamma_correction
        self.gamma_value = gamma_value

    def prepare_object_points(self) -> np.ndarray:
        objp = np.zeros(
            (self.pattern_size[0] * self.pattern_size[1], 3),
            np.float32
        )
        objp[:, :2] = np.mgrid[
            0:self.pattern_size[0],
            0:self.pattern_size[1]
        ].T.reshape(-1, 2)
        objp *= self.square_size
        return objp

    def detect_corners(
        self,
        image_path: str,
        visualize: bool = False
    ) -> Optional[Dict]:
        img = cv2.imread(image_path)
        if img is None:
            return None

        if self.need_gamma_correction:
            img = self._gamma_correction(img)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(
            gray,
            self.pattern_size,
            None
        )

        if not ret:
            return None

        criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            30,
            0.001
        )
        corners_subpix = cv2.cornerSubPix(
            gray,
            corners,
            (11, 11),
            (-1, -1),
            criteria
        )

        objp = self.prepare_object_points()

        result = {
            'object_points': objp,
            'image_points': corners_subpix,
            'image': img,
            'corners': corners,
            'success': True
        }

        if visualize:
            img_vis = img.copy()
            cv2.drawChessboardCorners(img_vis, self.pattern_size, corners_subpix, True)
            result['visualization'] = img_vis

        return result

    def detect_corners_from_array(
        self,
        image: np.ndarray,
        visualize: bool = False
    ) -> Optional[Dict]:
        if len(image.shape) == 2:
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(
            gray,
            self.pattern_size,
            None
        )

        if not ret:
            return None

        criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            30,
            0.001
        )
        corners_subpix = cv2.cornerSubPix(
            gray,
            corners,
            (11, 11),
            (-1, -1),
            criteria
        )

        objp = self.prepare_object_points()

        result = {
            'object_points': objp,
            'image_points': corners_subpix,
            'corners': corners,
            'success': True
        }

        if visualize:
            img_vis = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            cv2.drawChessboardCorners(img_vis, self.pattern_size, corners_subpix, True)
            result['visualization'] = img_vis

        return result

    def _gamma_correction(self, img: np.ndarray) -> np.ndarray:
        img_float = img.astype(np.float32) / 255.0
        img_gamma = np.power(img_float, 1.0 / self.gamma_value)
        return np.clip(img_gamma * 255, 0, 255).astype(np.uint8)

    def create_pattern_image(
        self,
        output_path: str,
        image_size: Tuple[int, int] = (1280, 720),
        border_bits: int = 1
    ) -> None:
        pattern = cv2.matmul(
            np.eye(3, dtype=np.uint8),
            255 * border_bits
        )
        pattern = cv2.resize(
            pattern,
            image_size,
            interpolation=cv2.INTER_NEAREST
        )
        cv2.imwrite(output_path, pattern)
