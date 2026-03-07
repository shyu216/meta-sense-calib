"""
MetaSenseCalib - 核心标定模块
"""

from .chessboard import ChessboardDetector
from .pose import PoseEstimator
from .transform import RigidTransform
from .calibrator import Calibrator

__all__ = [
    'ChessboardDetector',
    'PoseEstimator',
    'RigidTransform',
    'Calibrator'
]

__version__ = '0.1.0'
