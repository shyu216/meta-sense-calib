import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Optional, Tuple
from matplotlib.animation import FuncAnimation
import os


class PointCloudVisualizer:
    def __init__(self, figure_size: Tuple[int, int] = (12, 6)):
        self.figure_size = figure_size

    def plot_before_after_registration(
        self,
        points_before: np.ndarray,
        points_after: np.ndarray,
        points_target: np.ndarray,
        sample_index: Optional[int] = None,
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        if sample_index is not None:
            if sample_index < len(points_before):
                points_before = points_before[sample_index:sample_index+1]
                points_after = points_after[sample_index:sample_index+1]
                points_target = points_target[sample_index:sample_index+1]
            else:
                sample_index = 0

        fig = plt.figure(figsize=self.figure_size)

        ax1 = fig.add_subplot(121, projection='3d')
        ax1.scatter(
            -points_before[:, 0], -points_before[:, 1], points_before[:, 2],
            c='red', s=50, alpha=0.6, label='Source (Before)'
        )
        ax1.scatter(
            -points_target[:, 0], -points_target[:, 1], points_target[:, 2],
            c='blue', s=50, alpha=0.6, label='Target'
        )
        ax1.set_title('Before Registration')
        ax1.set_xlabel('X (mm)')
        ax1.set_ylabel('Y (mm)')
        ax1.set_zlabel('Z (mm)')
        ax1.legend()
        
        ax1.view_init(vertical_axis='y', azim=170, elev=10)

        ax2 = fig.add_subplot(122, projection='3d')
        ax2.scatter(
            -points_after[:, 0], -points_after[:, 1], points_after[:, 2],
            c='red', s=50, alpha=0.6, label='Source (After)'
        )
        ax2.scatter(
            -points_target[:, 0], -points_target[:, 1], points_target[:, 2],
            c='blue', s=50, alpha=0.6, label='Target'
        )
        ax2.set_title('After Registration')
        ax2.set_xlabel('X (mm)')
        ax2.set_ylabel('Y (mm)')
        ax2.set_zlabel('Z (mm)')
        ax2.legend()

        ax2.view_init(vertical_axis='y', azim=170, elev=10)

        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[PointCloudVisualizer] Saved to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_point_cloud_3d(
        self,
        points: np.ndarray,
        color: Optional[np.ndarray] = None,
        title: str = "3D Point Cloud",
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        fig = plt.figure(figsize=self.figure_size)
        ax = fig.add_subplot(111, projection='3d')

        if color is not None:
            scatter = ax.scatter(
                points[:, 0], points[:, 1], points[:, 2],
                c=color, cmap='viridis', s=20, alpha=0.7
            )
            plt.colorbar(scatter, ax=ax, label='Color Value')
        else:
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=20, alpha=0.7)

        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        ax.set_title(title)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_multi_cloud_comparison(
        self,
        point_clouds: List[Tuple[np.ndarray, str]],
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        n = len(point_clouds)
        fig = plt.figure(figsize=(6 * n, 6))

        for i, (points, label) in enumerate(point_clouds):
            ax = fig.add_subplot(1, n, i + 1, projection='3d')
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=10, alpha=0.6)
            ax.set_title(label)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')

        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def create_registration_animation(
        self,
        points_source: np.ndarray,
        points_target: np.ndarray,
        transformation_matrices: List[np.ndarray],
        output_path: str,
        fps: int = 10
    ) -> None:
        fig = plt.figure(figsize=self.figure_size)
        ax = fig.add_subplot(111, projection='3d')

        def update(frame):
            ax.clear()

            T = transformation_matrices[frame]
            points_transformed = (T @ np.hstack([
                points_source,
                np.ones((points_source.shape[0], 1))
            ]).T).T[:, :3]

            ax.scatter(
                points_transformed[:, 0],
                points_transformed[:, 1],
                points_transformed[:, 2],
                c='red', s=20, alpha=0.6, label='Source'
            )
            ax.scatter(
                points_target[:, 0],
                points_target[:, 1],
                points_target[:, 2],
                c='blue', s=20, alpha=0.6, label='Target'
            )

            ax.set_xlabel('X (mm)')
            ax.set_ylabel('Y (mm)')
            ax.set_zlabel('Z (mm)')
            ax.set_title(f'Registration Step {frame + 1}/{len(transformation_matrices)}')
            ax.legend()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        anim = FuncAnimation(fig, update, frames=len(transformation_matrices))
        anim.save(output_path, writer='pillow', fps=fps)
        print(f"[PointCloudVisualizer] Animation saved to {output_path}")

    def plot_chessboard_frames(
        self,
        object_points: np.ndarray,
        camera_poses: List[Tuple[np.ndarray, np.ndarray]],
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        fig = plt.figure(figsize=self.figure_size)
        ax = fig.add_subplot(111, projection='3d')

        object_points_mean = np.mean(object_points, axis=0)

        for i, (rvec, tvec) in enumerate(camera_poses):
            from scipy.spatial.transform import Rotation
            R = Rotation.from_rotvec(rvec.flatten()).as_matrix()

            origin = tvec.flatten()
            scale = 30

            x_axis = origin + R[:, 0] * scale
            y_axis = origin + R[:, 1] * scale
            z_axis = origin + R[:, 2] * scale

            color = plt.cm.viridis(i / len(camera_poses))

            ax.plot([origin[0], x_axis[0]], [origin[1], x_axis[1]], [origin[2], x_axis[2]],
                    c='r', linewidth=2)
            ax.plot([origin[0], y_axis[0]], [origin[1], y_axis[1]], [origin[2], y_axis[2]],
                    c='g', linewidth=2)
            ax.plot([origin[0], z_axis[0]], [origin[1], z_axis[1]], [origin[2], z_axis[2]],
                    c='b', linewidth=2)

            ax.scatter(*origin, c=[color], s=50)

            cb_center = origin + R[:, 2] * 100
            ax.scatter(*cb_center, c='orange', s=30, marker='x')

        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        ax.set_title('Chessboard Frames Over Time')

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig


def visualize_pointcloud_registration(
    rs_points: np.ndarray,
    q3_points: np.ndarray,
    transformation_matrix: np.ndarray,
    output_dir: str,
    show: bool = False
) -> None:
    output_dir = os.path.join(output_dir, 'visualization')
    os.makedirs(output_dir, exist_ok=True)

    visualizer = PointCloudVisualizer()

    print("[PointCloudVisualization] Generating 3D plots...")

    transformed = (transformation_matrix @ np.hstack([
        rs_points,
        np.ones((rs_points.shape[0], 1))
    ]).T).T[:, :3]

    visualizer.plot_before_after_registration(
        rs_points, transformed, q3_points,
        save_path=os.path.join(output_dir, 'registration_comparison.png'),
        show=show
    )

    visualizer.plot_point_cloud_3d(
        rs_points,
        title="RealSense Points",
        save_path=os.path.join(output_dir, 'rs_points_3d.png'),
        show=show
    )

    visualizer.plot_point_cloud_3d(
        q3_points,
        title="Quest3 Points",
        save_path=os.path.join(output_dir, 'q3_points_3d.png'),
        show=show
    )

    print("[PointCloudVisualization] Done!")
