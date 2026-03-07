import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Optional, Tuple, Dict
import matplotlib.patches as mpatches
import os


class PoseVisualizer:
    def __init__(self, figure_size: Tuple[int, int] = (12, 8)):
        self.figure_size = figure_size

    def plot_poses_3d(
        self,
        rvecs: List[np.ndarray],
        tvecs: List[np.ndarray],
        labels: Optional[List[str]] = None,
        camera_names: Optional[List[str]] = None,
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        fig = plt.figure(figsize=self.figure_size)
        ax = fig.add_subplot(111, projection='3d')

        colors = ['red', 'blue', 'green', 'orange', 'purple']
        camera_names = camera_names or ['Camera'] * len(rvecs)

        for i, (rvec, tvec) in enumerate(zip(rvecs, tvecs)):
            R, _ = self._rodrigues(rvec)

            origin = tvec.flatten()
            x_axis = origin + R[:, 0] * 50
            y_axis = origin + R[:, 1] * 50
            z_axis = origin + R[:, 2] * 50

            color = colors[i % len(colors)]
            label = camera_names[i]

            ax.plot(
                [origin[0], x_axis[0]],
                [origin[1], x_axis[1]],
                [origin[2], x_axis[2]],
                c='r', linewidth=2, alpha=0.8
            )
            ax.plot(
                [origin[0], y_axis[0]],
                [origin[1], y_axis[1]],
                [origin[2], y_axis[2]],
                c='g', linewidth=2, alpha=0.8
            )
            ax.plot(
                [origin[0], z_axis[0]],
                [origin[1], z_axis[1]],
                [origin[2], z_axis[2]],
                c='b', linewidth=2, alpha=0.8
            )

            ax.scatter(*origin, c=color, s=100, label=label, marker='o')

        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        ax.set_title('Camera Poses in 3D')
        ax.legend()

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[PoseVisualizer] Saved to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_poses_2d_top_view(
        self,
        rvecs: List[np.ndarray],
        tvecs: List[np.ndarray],
        labels: Optional[List[str]] = None,
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=(8, 8))

        colors = ['red', 'blue', 'green', 'orange', 'purple']

        for i, (rvec, tvec) in enumerate(zip(rvecs, tvecs)):
            R, _ = self._rodrigues(rvec)
            origin = tvec.flatten()

            x_axis = origin + R[:, 0] * 50
            y_axis = origin + R[:, 1] * 50

            color = colors[i % len(colors)]
            label = labels[i] if labels else f'Camera {i}'

            ax.arrow(
                origin[0], origin[1],
                x_axis[0] - origin[0], x_axis[1] - origin[1],
                head_width=5, head_length=3, fc=color, ec=color
            )

            ax.scatter(origin[0], origin[1], c=color, s=100, label=label)

        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_title('Camera Poses (Top View)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis('equal')

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_trajectory(
        self,
        tvecs: List[np.ndarray],
        labels: Optional[List[str]] = None,
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        fig = plt.figure(figsize=self.figure_size)
        ax = fig.add_subplot(111, projection='3d')

        tvecs_array = np.array([tvec.flatten() for tvec in tvecs])

        ax.plot(tvecs_array[:, 0], tvecs_array[:, 1], tvecs_array[:, 2],
                'b-', linewidth=2, alpha=0.7)
        ax.scatter(tvecs_array[:, 0], tvecs_array[:, 1], tvecs_array[:, 2],
                  c=range(len(tvecs_array)), cmap='viridis', s=50)

        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        ax.set_title('Camera Trajectory')
        ax.legend() if labels else None

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_coordinate_frames(
        self,
        transformation_matrices: List[np.ndarray],
        labels: Optional[List[str]] = None,
        scale: float = 50.0,
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        fig = plt.figure(figsize=self.figure_size)
        ax = fig.add_subplot(111, projection='3d')

        for i, T in enumerate(transformation_matrices):
            origin = T[:3, 3]
            R = T[:3, :3]

            x_axis = origin + R[:, 0] * scale
            y_axis = origin + R[:, 1] * scale
            z_axis = origin + R[:, 2] * scale

            label = labels[i] if labels else f'Frame {i}'

            ax.plot([origin[0], x_axis[0]], [origin[1], x_axis[1]], [origin[2], x_axis[2]],
                    c='r', linewidth=2, label=f'{label}-X' if i == 0 else None)
            ax.plot([origin[0], y_axis[0]], [origin[1], y_axis[1]], [origin[2], y_axis[2]],
                    c='g', linewidth=2, label=f'{label}-Y' if i == 0 else None)
            ax.plot([origin[0], z_axis[0]], [origin[1], z_axis[1]], [origin[2], z_axis[2]],
                    c='b', linewidth=2, label=f'{label}-Z' if i == 0 else None)

            ax.scatter(*origin, s=100)

        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        ax.set_title('Coordinate Frames')
        ax.legend()

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_poses_timeline(
        self,
        tvecs: List[np.ndarray],
        rvecs: Optional[List[np.ndarray]] = None,
        labels: Optional[List[str]] = None,
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        tvecs_array = np.array([tvec.flatten() for tvec in tvecs])

        fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

        axes[0].plot(tvecs_array[:, 0], 'r-', label='X')
        axes[0].set_ylabel('X (mm)')
        axes[0].set_title('Position Timeline')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()

        axes[1].plot(tvecs_array[:, 1], 'g-', label='Y')
        axes[1].set_ylabel('Y (mm)')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()

        axes[2].plot(tvecs_array[:, 2], 'b-', label='Z')
        axes[2].set_ylabel('Z (mm)')
        axes[2].set_xlabel('Frame')
        axes[2].grid(True, alpha=0.3)
        axes[2].legend()

        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    @staticmethod
    def _rodrigues(rvec: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        from scipy.spatial.transform import Rotation
        rot = Rotation.from_rotvec(rvec.flatten())
        return rot.as_matrix(), rot.as_euler('xyz')


def visualize_calibration_result(
    result_dict: dict,
    output_dir: str,
    show: bool = False
) -> None:
    import os
    output_dir = os.path.join(output_dir, 'visualization')
    os.makedirs(output_dir, exist_ok=True)

    visualizer = PoseVisualizer()

    print("[Visualization] Generating plots...")

    if 'poses' in result_dict:
        poses = result_dict['poses']
        rvecs = [p['rvec'] for p in poses]
        tvecs = [p['tvec'] for p in poses]
        visualizer.plot_poses_3d(rvecs, tvecs, save_path=os.path.join(output_dir, 'poses_3d.png'), show=show)

    print("[Visualization] Done!")
