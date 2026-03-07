import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple, Dict
import seaborn as sns
import os


class ErrorVisualizer:
    def __init__(self, figure_size: Tuple[int, int] = (10, 6)):
        self.figure_size = figure_size
        plt.style.use('seaborn-v0_8-whitegrid')

    def plot_error_histogram(
        self,
        errors: np.ndarray,
        bins: int = 30,
        save_path: Optional[str] = None,
        show: bool = True,
        title: str = "Registration Error Distribution"
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=self.figure_size)

        ax.hist(errors, bins=bins, color='steelblue', alpha=0.7, edgecolor='black')

        mean_err = np.mean(errors)
        std_err = np.std(errors)

        ax.axvline(mean_err, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_err:.3f} mm')
        ax.axvline(mean_err + std_err, color='orange', linestyle=':', linewidth=2, label=f'±1σ: {std_err:.3f} mm')
        ax.axvline(mean_err - std_err, color='orange', linestyle=':', linewidth=2)

        ax.set_xlabel('Error (mm)', fontsize=12)
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.legend(fontsize=10)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[ErrorVisualizer] Saved histogram to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_error_by_frame(
        self,
        errors: np.ndarray,
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=self.figure_size)

        frames = np.arange(len(errors))

        ax.plot(frames, errors, 'b-', linewidth=1, alpha=0.7)
        ax.scatter(frames, errors, c='blue', s=30, alpha=0.6)

        mean_err = np.mean(errors)
        ax.axhline(mean_err, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_err:.3f} mm')

        ax.set_xlabel('Frame', fontsize=12)
        ax.set_ylabel('Error (mm)', fontsize=12)
        ax.set_title('Error by Frame', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_error_heatmap_2d(
        self,
        points: np.ndarray,
        errors: np.ndarray,
        grid_size: Tuple[int, int] = (10, 10),
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=(10, 8))

        x_min, x_max = points[:, 0].min(), points[:, 0].max()
        y_min, y_max = points[:, 1].min(), points[:, 1].max()

        x_bins = np.linspace(x_min, x_max, grid_size[0] + 1)
        y_bins = np.linspace(y_min, y_max, grid_size[1] + 1)

        heatmap = np.zeros(grid_size)
        counts = np.zeros(grid_size)

        for point, error in zip(points, errors):
            x_idx = np.searchsorted(x_bins, point[0]) - 1
            y_idx = np.searchsorted(y_bins, point[1]) - 1
            x_idx = np.clip(x_idx, 0, grid_size[0] - 1)
            y_idx = np.clip(y_idx, 0, grid_size[1] - 1)
            heatmap[y_idx, x_idx] += error
            counts[y_idx, x_idx] += 1

        heatmap = np.divide(heatmap, counts, out=np.zeros_like(heatmap), where=counts > 0)

        im = ax.imshow(heatmap, extent=[x_min, x_max, y_min, y_max],
                       origin='lower', cmap='YlOrRd', aspect='auto')
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Error (mm)', fontsize=12)

        ax.set_xlabel('X (mm)', fontsize=12)
        ax.set_ylabel('Y (mm)', fontsize=12)
        ax.set_title('2D Error Heatmap', fontsize=14)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_cdf(
        self,
        errors: np.ndarray,
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=self.figure_size)

        sorted_errors = np.sort(errors)
        cdf = np.arange(1, len(sorted_errors) + 1) / len(sorted_errors)

        ax.plot(sorted_errors, cdf, 'b-', linewidth=2)
        ax.fill_between(sorted_errors, 0, cdf, alpha=0.3)

        percentiles = [50, 90, 95, 99]
        for p in percentiles:
            val = np.percentile(errors, p)
            ax.axvline(val, color='red', linestyle='--', alpha=0.5)
            ax.axhline(p / 100, color='red', linestyle='--', alpha=0.5)
            ax.annotate(f'{p}%: {val:.2f}mm', xy=(val, p / 100),
                        xytext=(val + 0.5, p / 100 - 0.1),
                        fontsize=9, color='red')

        ax.set_xlabel('Error (mm)', fontsize=12)
        ax.set_ylabel('Cumulative Probability', fontsize=12)
        ax.set_title('Cumulative Distribution Function', fontsize=14)
        ax.grid(True, alpha=0.3)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_error_components(
        self,
        errors_x: np.ndarray,
        errors_y: np.ndarray,
        errors_z: np.ndarray,
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        components = [errors_x, errors_y, errors_z]
        titles = ['X Component', 'Y Component', 'Z Component']
        colors = ['red', 'green', 'blue']

        for ax, comp, title, color in zip(axes, components, titles, colors):
            ax.hist(comp, bins=30, color=color, alpha=0.7, edgecolor='black')
            ax.axvline(np.mean(comp), color='black', linestyle='--', linewidth=2,
                       label=f'Mean: {np.mean(comp):.3f}')
            ax.set_xlabel('Error (mm)')
            ax.set_ylabel('Count')
            ax.set_title(title)
            ax.legend()

        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_error_boxplot(
        self,
        error_groups: Dict[str, np.ndarray],
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=self.figure_size)

        labels = list(error_groups.keys())
        data = list(error_groups.values())

        bp = ax.boxplot(data, labels=labels, patch_artist=True)

        colors = plt.cm.Set3(np.linspace(0, 1, len(data)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)

        ax.set_xlabel('Group', fontsize=12)
        ax.set_ylabel('Error (mm)', fontsize=12)
        ax.set_title('Error Distribution by Group', fontsize=14)
        ax.grid(True, alpha=0.3, axis='y')

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_summary_statistics(
        self,
        errors: np.ndarray,
        save_path: Optional[str] = None,
        show: bool = True
    ) -> plt.Figure:
        stats = {
            'Mean': np.mean(errors),
            'Std': np.std(errors),
            'Min': np.min(errors),
            'Max': np.max(errors),
            'Median': np.median(errors),
            '50%': np.percentile(errors, 50),
            '90%': np.percentile(errors, 90),
            '95%': np.percentile(errors, 95),
            '99%': np.percentile(errors, 99)
        }

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        names = list(stats.keys())[:5]
        values = [stats[k] for k in names]
        colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(names)))

        bars = ax1.bar(names, values, color=colors, edgecolor='black')
        ax1.set_ylabel('Value (mm)')
        ax1.set_title('Basic Statistics')
        ax1.grid(True, alpha=0.3, axis='y')

        for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=9)

        names_p = ['50%', '90%', '95%', '99%']
        values_p = [stats[k] for k in names_p]
        colors_p = plt.cm.Reds(np.linspace(0.3, 0.9, len(names_p)))

        bars_p = ax2.bar(names_p, values_p, color=colors_p, edgecolor='black')
        ax2.set_ylabel('Value (mm)')
        ax2.set_title('Percentiles')
        ax2.grid(True, alpha=0.3, axis='y')

        for bar, val in zip(bars_p, values_p):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        return fig


def visualize_calibration_errors(
    points_source: np.ndarray,
    points_target: np.ndarray,
    transformation_matrix: np.ndarray,
    output_dir: str,
    show: bool = False
) -> None:
    import os
    output_dir = os.path.join(output_dir, 'visualization')
    os.makedirs(output_dir, exist_ok=True)

    transformed = (transformation_matrix @ np.hstack([
        points_source,
        np.ones((points_source.shape[0], 1))
    ]).T).T[:, :3]

    errors = np.linalg.norm(transformed - points_target, axis=1)

    visualizer = ErrorVisualizer()

    print("[ErrorVisualization] Generating error plots...")

    visualizer.plot_error_histogram(errors, save_path=os.path.join(output_dir, 'error_histogram.png'), show=show)
    visualizer.plot_cdf(errors, save_path=os.path.join(output_dir, 'error_cdf.png'), show=show)
    visualizer.plot_summary_statistics(errors, save_path=os.path.join(output_dir, 'error_summary.png'), show=show)

    print("[ErrorVisualization] Done!")
