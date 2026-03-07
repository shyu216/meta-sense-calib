"""
MetaSenseCalib - 第17对图片详细分析脚本

专门分析第17对图片的误差情况
"""

import os
import sys
import json
import numpy as np
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calibration.pose import CameraIntrinsics, PoseEstimator
from calibration.transform import RigidTransform
from calibration.chessboard import ChessboardDetector


def load_calibration_result(calibration_dir: str) -> Dict:
    """加载标定结果"""
    json_path = os.path.join(calibration_dir, 'calibration_result.json')
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"标定结果文件不存在: {json_path}")
    
    with open(json_path, 'r') as f:
        result_dict = json.load(f)
    
    return result_dict


def analyze_pair_17():
    """分析第17对图片"""
    print("=" * 60)
    print("MetaSenseCalib - 第17对图片详细分析")
    print("=" * 60)
    
    # 设置路径
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_folder = os.path.join(data_dir, "data", "example")
    calibration_dir = os.path.join(data_dir, "outputs", "calibration", "example")
    output_dir = os.path.join(data_dir, "outputs", "analysis", "pair_17")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载标定结果
    print("\n[1] 加载标定结果...")
    try:
        result_dict = load_calibration_result(calibration_dir)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        print("请先运行标定程序生成结果")
        return
    
    # 加载内参
    print("\n[2] 加载相机内参...")
    rs_intrinsics_path = os.path.join(data_dir, "data", "example", "rs_intrinsics.json")
    q3_intrinsics_path = os.path.join(data_dir, "data", "example", "q3_intrinsics.json")
    
    from calibration.calibrator import load_intrinsics_from_json
    intrinsics_rs = load_intrinsics_from_json(rs_intrinsics_path)
    intrinsics_q3 = load_intrinsics_from_json(q3_intrinsics_path)
    
    # 获取变换矩阵
    transformation_matrix = np.array(result_dict['transformation_matrix'])
    
    # 创建变换对象
    transform = RigidTransform.from_matrix(transformation_matrix)
    
    # 加载第17对图片
    print("\n[3] 加载第17对图片...")
    rs_image_path = os.path.join(image_folder, "rs_0017.png")
    q3_image_path = os.path.join(image_folder, "q3_0017.png")
    
    if not os.path.exists(rs_image_path) or not os.path.exists(q3_image_path):
        print("错误: 第17对图片不存在")
        return
    
    print(f"RealSense 图片: {rs_image_path}")
    print(f"Quest3 图片: {q3_image_path}")
    
    # 读取图片
    rs_image = cv2.imread(rs_image_path)
    q3_image = cv2.imread(q3_image_path)
    
    # 显示图片尺寸
    print(f"\nRealSense 图片尺寸: {rs_image.shape[:2]}")
    print(f"Quest3 图片尺寸: {q3_image.shape[:2]}")
    
    # 创建检测器和位姿估计器
    detector = ChessboardDetector(
        pattern_size=(9, 6),
        square_size=36.0
    )
    
    pose_estimator1 = PoseEstimator(intrinsics_rs)
    pose_estimator2 = PoseEstimator(intrinsics_q3)
    
    # 检测棋盘格角点
    print("\n[4] 检测棋盘格角点...")
    result1 = detector.detect_corners(rs_image_path, visualize=True)
    result2 = detector.detect_corners(q3_image_path, visualize=True)
    
    if result1 is None:
        print("错误: RealSense 图片棋盘格检测失败")
        return
    
    if result2 is None:
        print("错误: Quest3 图片棋盘格检测失败")
        return
    
    print(f"RealSense 检测到的角点数量: {len(result1['image_points'])}")
    print(f"Quest3 检测到的角点数量: {len(result2['image_points'])}")
    
    # 绘制棋盘格角点和添加标题
    chessboard_size = (9, 6)
    
    # 处理 RealSense 图片
    rs_img = result1['image']
    rs_corners = result1['image_points']
    cv2.drawChessboardCorners(rs_img, chessboard_size, rs_corners, True)
    cv2.putText(rs_img, "Chessboard Detection - RealSense", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # 处理 Quest3 图片
    q3_img = result2['image']
    q3_corners = result2['image_points']
    cv2.drawChessboardCorners(q3_img, chessboard_size, q3_corners, True)
    cv2.putText(q3_img, "Chessboard Detection - Quest3", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # 保存检测结果
    cv2.imwrite(os.path.join(output_dir, "rs_0017_corners.png"), rs_img)
    cv2.imwrite(os.path.join(output_dir, "q3_0017_corners.png"), q3_img)
    print("\n角点检测结果已保存到:")
    print(f"  {os.path.join(output_dir, 'rs_0017_corners.png')}")
    print(f"  {os.path.join(output_dir, 'q3_0017_corners.png')}")
    
    # 估计位姿
    print("\n[5] 估计相机位姿...")
    pose1 = pose_estimator1.estimate_pose(
        result1['object_points'],
        result1['image_points']
    )
    pose2 = pose_estimator2.estimate_pose(
        result2['object_points'],
        result2['image_points']
    )
    
    if pose1 is None:
        print("错误: RealSense 位姿估计失败")
        return
    
    if pose2 is None:
        print("错误: Quest3 位姿估计失败")
        return
    
    print("RealSense 位姿:")
    print(f"  旋转向量: {pose1['rvec'].flatten()}")
    print(f"  平移向量: {pose1['tvec'].flatten()}")
    
    print("Quest3 位姿:")
    print(f"  旋转向量: {pose2['rvec'].flatten()}")
    print(f"  平移向量: {pose2['tvec'].flatten()}")
    
    # 转换到相机坐标系
    print("\n[6] 计算3D点云...")
    points1_cam = pose_estimator1.transform_to_camera_coord(
        result1['object_points'],
        pose1['rvec'],
        pose1['tvec']
    )
    points2_cam = pose_estimator2.transform_to_camera_coord(
        result2['object_points'],
        pose2['rvec'],
        pose2['tvec']
    )
    
    # 应用变换
    points1_transformed = transform.transform_points(np.array(points1_cam))
    
    # 计算误差
    errors = np.linalg.norm(points1_transformed - np.array(points2_cam), axis=1)
    
    print("\n[7] 误差分析:")
    print(f"平均误差: {np.mean(errors):.3f} mm")
    print(f"标准差: {np.std(errors):.3f} mm")
    print(f"最大误差: {np.max(errors):.3f} mm")
    print(f"最小误差: {np.min(errors):.3f} mm")
    
    # 保存误差数据
    np.save(os.path.join(output_dir, "errors.npy"), errors)
    np.save(os.path.join(output_dir, "points1_cam.npy"), np.array(points1_cam))
    np.save(os.path.join(output_dir, "points1_transformed.npy"), points1_transformed)
    np.save(os.path.join(output_dir, "points2_cam.npy"), np.array(points2_cam))
    
    # 生成误差分析图表
    print("\n[8] 生成误差分析图表...")
    generate_error_analysis(errors, output_dir)
    
    # 3D点云可视化
    print("\n[9] 生成3D点云可视化...")
    generate_3d_visualization(
        np.array(points1_cam),
        points1_transformed,
        np.array(points2_cam),
        output_dir
    )
    
    print("\n分析完成！结果已保存到:")
    print(f"  {output_dir}")


def generate_error_analysis(errors: np.ndarray, output_dir: str):
    """Generate error analysis charts"""
    # Set style
    sns.set_style("whitegrid")
    
    # Chart 1: Error distribution histogram
    plt.figure(figsize=(12, 6))
    sns.histplot(errors, bins=20, kde=True)
    plt.xlabel('Error (mm)')
    plt.ylabel('Frequency')
    plt.title('Error Distribution of Pair 17')
    plt.axvline(np.mean(errors), color='red', linestyle='--', label=f'Mean: {np.mean(errors):.2f} mm')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'error_distribution.png'))
    
    # Chart 2: Error scatter plot
    plt.figure(figsize=(12, 6))
    plt.scatter(range(len(errors)), errors, alpha=0.7)
    plt.axhline(np.mean(errors), color='red', linestyle='--', label=f'Mean: {np.mean(errors):.2f} mm')
    plt.xlabel('Corner Index')
    plt.ylabel('Error (mm)')
    plt.title('Error of Each Corner in Pair 17')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'error_scatter.png'))


def generate_3d_visualization(points1: np.ndarray, points1_transformed: np.ndarray, points2: np.ndarray, output_dir: str):
    """Generate 3D point cloud visualization"""
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure(figsize=(15, 10))
    
    # Subplot 1: Before registration
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.scatter(points1[:, 0], points1[:, 1], points1[:, 2], c='red', label='RealSense')
    ax1.scatter(points2[:, 0], points2[:, 1], points2[:, 2], c='blue', label='Quest3')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.set_zlabel('Z (mm)')
    ax1.set_title('Point Clouds Before Registration')
    ax1.legend()
    
    # Subplot 2: After registration
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.scatter(points1_transformed[:, 0], points1_transformed[:, 1], points1_transformed[:, 2], c='red', label='RealSense (Transformed)')
    ax2.scatter(points2[:, 0], points2[:, 1], points2[:, 2], c='blue', label='Quest3')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.set_zlabel('Z (mm)')
    ax2.set_title('Point Clouds After Registration')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '3d_visualization.png'))


def main():
    analyze_pair_17()


if __name__ == "__main__":
    main()
