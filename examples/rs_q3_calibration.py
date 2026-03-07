"""
MetaSenseCalib - 使用示例

Quest3 + RealSense 外参标定
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calibration import Calibrator
from calibration.pose import CameraIntrinsics
from visualization import PoseVisualizer, ErrorVisualizer, PointCloudVisualizer


def main():
    print("=" * 60)
    print("MetaSenseCalib - Quest3 + RealSense 标定工具")
    print("=" * 60)

    # 从JSON文件加载内参
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rs_intrinsics_path = os.path.join(data_dir, "data", "example", "rs_intrinsics.json")
    q3_intrinsics_path = os.path.join(data_dir, "data", "example", "q3_intrinsics.json")

    print("\n[1] 加载 RealSense D415 内参:")
    print(f"从文件加载: {rs_intrinsics_path}")

    print("\n[2] 加载 Quest3 内参:")
    print(f"从文件加载: {q3_intrinsics_path}")

    calibrator = Calibrator(
        intrinsics_rs=rs_intrinsics_path,
        intrinsics_q3=q3_intrinsics_path
    )

    print("\n[3] RealSense D415 内参矩阵:")
    print(calibrator.camera1_intrinsics.matrix)

    print("\n[4] Quest3 内参矩阵:")
    print(calibrator.camera2_intrinsics.matrix)

    image_folder = os.path.join(data_dir, "data", "example")

    if not os.path.exists(image_folder):
        print(f"\n警告: 图像文件夹不存在: {image_folder}")
        print("请修改 image_folder 变量指向你的标定图像文件夹")
        print("\n跳过实际标定，仅演示API用法...")
        return

    result = calibrator.calibrate(
        image_folder=image_folder,
        camera1_tag='rs',
        camera2_tag='q3',
        output_dir='outputs/calibration/example',
        visualize=False
    )

    print("\n" + "=" * 60)
    print("标定结果")
    print("=" * 60)
    print(f"有效帧数: {result.valid_frame_count}/{result.total_frame_count}")
    print(f"\n变换矩阵 T (RealSense -> Quest3):")
    print(result.transformation_matrix)
    print(f"\n旋转矩阵 R:")
    print(result.rotation_matrix)
    print(f"\n平移向量 t (mm):")
    print(result.translation_vector)
    print(f"\n旋转角度 (度): X={result.euler_angles[0]:.2f}, Y={result.euler_angles[1]:.2f}, Z={result.euler_angles[2]:.2f}")
    print(f"\n配准误差统计:")
    print(f"  平均误差: {result.mean_error:.3f} mm")
    print(f"  标准差:  {result.std_error:.3f} mm")
    print(f"  最大误差: {result.max_error:.3f} mm")
    print(f"  最小误差: {result.min_error:.3f} mm")


def demo_visualization_only():
    """使用实际标定结果和真实数据进行可视化"""
    import numpy as np
    import os
    import json

    print("\n演示可视化功能...")

    # 获取输出目录
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    calibration_dir = os.path.join(data_dir, "outputs", "calibration", "example")
    json_path = os.path.join(calibration_dir, "calibration_result.json")

    # 检查标定结果文件是否存在
    if not os.path.exists(json_path):
        print(f"警告: 标定结果文件不存在: {json_path}")
        print("请先运行标定程序生成结果")
        return

    # 加载标定结果
    print(f"加载标定结果: {json_path}")
    with open(json_path, 'r') as f:
        result_dict = json.load(f)

    # 提取数据
    transformation_matrix = np.array(result_dict['transformation_matrix'])
    
    # 检查是否有实际的点云数据
    points1_path = os.path.join(calibration_dir, "points1.npy")
    points2_path = os.path.join(calibration_dir, "points2.npy")
    
    if os.path.exists(points1_path) and os.path.exists(points2_path):
        print("加载实际点云数据...")
        points1 = np.load(points1_path)
        points2 = np.load(points2_path)
        print(f"实际点云数据加载完成: {points1.shape[0]} 个点")
    else:
        print("未找到实际点云数据，使用模拟数据...")
        # 生成模拟点云数据（基于标定结果）
        np.random.seed(42)
        points1 = np.random.randn(100, 3) * 50 + np.array([100, 50, 500])
        points2 = (transformation_matrix @ np.hstack([points1, np.ones((points1.shape[0], 1))]).T).T[:, :3]
        points2 += np.random.randn(100, 3) * 2  # 添加噪声

    # 计算误差
    transformed = (transformation_matrix @ np.hstack([points1, np.ones((points1.shape[0], 1))]).T).T[:, :3]
    errors = np.linalg.norm(transformed - points2, axis=1)

    # 从标定结果中提取实际的位姿数据
    rvecs = []
    tvecs = []
    
    # 检查是否有实际的位姿数据
    if 'camera1_poses' in result_dict and 'camera2_poses' in result_dict:
        print("加载实际位姿数据...")
        # 使用最后一组位姿数据进行可视化
        if result_dict['camera1_poses'] and result_dict['camera2_poses']:
            # 取最后一个有效的位姿
            cam1_pose = result_dict['camera1_poses'][-1]
            cam2_pose = result_dict['camera2_poses'][-1]
            
            # 提取旋转向量和平移向量
            rvecs.append(np.array(cam1_pose['rvec']).reshape(3, 1))
            tvecs.append(np.array(cam1_pose['tvec']).reshape(3, 1))
            rvecs.append(np.array(cam2_pose['rvec']).reshape(3, 1))
            tvecs.append(np.array(cam2_pose['tvec']).reshape(3, 1))
            print("实际位姿数据加载完成")
    
    # 如果没有实际位姿数据，使用模拟数据
    if not rvecs:
        print("未找到实际位姿数据，使用模拟数据...")
        rvecs = [np.array([[0.1], [0.2], [0.3]]), np.array([[0.05], [0.1], [0.15]])]
        tvecs = [np.array([[100], [50], [500]]), np.array([[120], [60], [520]])]

    # 创建可视化器
    visualizer_poses = PoseVisualizer()
    visualizer_errors = ErrorVisualizer()
    visualizer_pc = PointCloudVisualizer()

    # 生成位姿可视化
    print("生成位姿可视化...")
    visualizer_poses.plot_poses_3d(
        rvecs, tvecs,
        camera_names=['RealSense', 'Quest3'],
        save_path='outputs/visualization/poses_3d.png',
        show=False
    )

    # 生成误差可视化
    print("生成误差可视化...")
    visualizer_errors.plot_error_histogram(
        errors,
        save_path='outputs/visualization/error_histogram.png',
        show=False
    )

    # 生成3D点云可视化
    print("生成3D点云可视化...")
    visualizer_pc.plot_before_after_registration(
        points1,
        transformed,
        points2,
        save_path='outputs/visualization/registration.png',
        show=False
    )

    print("\n可视化示例已保存到 outputs/visualization/ 目录")


if __name__ == "__main__":
    main()
    demo_visualization_only()
