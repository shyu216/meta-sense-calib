"""
MetaSenseCalib - 单个摄像头内参标定示例

测试 RealSense 和 Quest3 摄像头的内参标定，并与内置参数对比
"""

import os
import sys
import json
import numpy as np
import cv2
from typing import Dict, List, Tuple

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calibration.chessboard import ChessboardDetector
from calibration.pose import CameraIntrinsics


def calibrate_camera(image_folder: str, camera_tag: str, chessboard_size: Tuple[int, int] = (9, 6), square_size: float = 36.0) -> Dict:
    """
    标定单个摄像头的内参
    
    Args:
        image_folder: 图片文件夹路径
        camera_tag: 摄像头标签 (rs 或 q3)
        chessboard_size: 棋盘格内角点数量
        square_size: 棋盘格方块大小 (mm)
    
    Returns:
        内参标定结果
    """
    print(f"\n[1] 开始标定 {camera_tag.upper()} 摄像头内参...")
    
    # 加载图片
    image_files = sorted([f for f in os.listdir(image_folder) if camera_tag in f and f.endswith('.png')])
    if not image_files:
        print(f"错误: 未找到 {camera_tag} 标签的图片")
        return None
    
    print(f"找到 {len(image_files)} 张 {camera_tag} 图片")
    
    # 创建棋盘格检测器
    detector = ChessboardDetector(
        pattern_size=chessboard_size,
        square_size=square_size
    )
    
    # 准备对象点和图像点
    objpoints = []  # 3D 点
    imgpoints = []  # 2D 点
    
    # 生成棋盘格对象点
    objp = detector.prepare_object_points()
    
    # 处理每张图片
    for img_file in image_files:
        img_path = os.path.join(image_folder, img_file)
        result = detector.detect_corners(img_path, visualize=False)
        
        if result is not None:
            objpoints.append(objp)
            imgpoints.append(result['image_points'])
            print(f"  处理成功: {img_file}")
        else:
            print(f"  处理失败: {img_file}")
    
    if len(objpoints) < 5:
        print("错误: 成功检测的图片数量不足，需要至少5张")
        return None
    
    # 读取第一张图片获取尺寸
    first_img = cv2.imread(os.path.join(image_folder, image_files[0]))
    h, w = first_img.shape[:2]
    
    # 标定相机
    print("\n[2] 执行相机标定...")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, (w, h), None, None
    )
    
    if not ret:
        print("错误: 标定失败")
        return None
    
    # 计算重投影误差
    print("\n[3] 计算重投影误差...")
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        mean_error += error
    
    mean_error /= len(objpoints)
    
    print(f"  平均重投影误差: {mean_error:.3f} pixels")
    
    # 构建结果
    result = {
        'camera_tag': camera_tag,
        'image_count': len(objpoints),
        'image_size': (w, h),
        'camera_matrix': mtx.tolist(),
        'distortion_coefficients': dist.tolist(),
        'mean_reprojection_error': mean_error,
        'rvecs': [rvec.tolist() for rvec in rvecs],
        'tvecs': [tvec.tolist() for tvec in tvecs]
    }
    
    return result


def load_builtin_intrinsics(camera_tag: str) -> Dict:
    """
    加载内置的相机内参
    
    Args:
        camera_tag: 摄像头标签 (rs 或 q3)
    
    Returns:
        内置内参（转换为标准格式）
    """
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    intrinsics_path = os.path.join(data_dir, "data", "example", f"{camera_tag}_intrinsics.json")
    
    if not os.path.exists(intrinsics_path):
        print(f"警告: 未找到 {camera_tag} 的内置内参文件")
        return None
    
    with open(intrinsics_path, 'r') as f:
        intrinsics = json.load(f)
    
    # 转换为标准相机矩阵格式
    if 'FocalLength' in intrinsics and 'PrincipalPoint' in intrinsics:
        # 构建相机矩阵
        fx = intrinsics['FocalLength']['x']
        fy = intrinsics['FocalLength']['y']
        cx = intrinsics['PrincipalPoint']['x']
        cy = intrinsics['PrincipalPoint']['y']
        skew = intrinsics.get('Skew', 0.0)
        
        camera_matrix = [
            [fx, skew, cx],
            [0, fy, cy],
            [0, 0, 1]
        ]
        
        # 构建标准格式
        standard_intrinsics = {
            'camera_matrix': camera_matrix,
            'distortion_coefficients': [[0, 0, 0, 0, 0]],  # 假设无畸变
            'image_size': (intrinsics['Resolution']['x'], intrinsics['Resolution']['y'])
        }
        
        return standard_intrinsics
    
    return intrinsics


def compare_intrinsics(calibrated: Dict, builtin: Dict) -> Dict:
    """
    比较标定内参与内置内参
    
    Args:
        calibrated: 标定得到的内参
        builtin: 内置的内参
    
    Returns:
        对比结果
    """
    if not calibrated or not builtin:
        return None
    
    # 提取相机矩阵
    calib_mtx = np.array(calibrated['camera_matrix'])
    builtin_mtx = np.array(builtin['camera_matrix'])
    
    # 计算差异
    diff_mtx = calib_mtx - builtin_mtx
    
    # 计算百分比差异（避免除以零）
    percent_diff = []
    for i in range(3):
        row = []
        for j in range(3):
            if builtin_mtx[i, j] != 0:
                row.append((diff_mtx[i, j] / builtin_mtx[i, j]) * 100)
            else:
                row.append(0)
        percent_diff.append(row)
    
    # 提取畸变系数
    calib_dist = np.array(calibrated['distortion_coefficients'])
    builtin_dist = np.array(builtin['distortion_coefficients'])
    
    # 计算畸变系数差异
    diff_dist = calib_dist - builtin_dist
    
    # 计算畸变系数百分比差异（避免除以零）
    percent_diff_dist = []
    for i in range(len(diff_dist[0])):
        if builtin_dist[0, i] != 0:
            percent_diff_dist.append((diff_dist[0, i] / builtin_dist[0, i]) * 100)
        else:
            percent_diff_dist.append(0)
    
    comparison = {
        'calibrated_matrix': calib_mtx.tolist(),
        'builtin_matrix': builtin_mtx.tolist(),
        'matrix_difference': diff_mtx.tolist(),
        'matrix_percent_difference': percent_diff,
        'calibrated_distortion': calib_dist.tolist(),
        'builtin_distortion': builtin_dist.tolist(),
        'distortion_difference': diff_dist.tolist(),
        'distortion_percent_difference': percent_diff_dist,
        'mean_reprojection_error': calibrated['mean_reprojection_error']
    }
    
    return comparison


def save_calibration_result(result: Dict, output_dir: str):
    """
    保存标定结果
    
    Args:
        result: 标定结果
        output_dir: 输出目录
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存标定结果
    output_path = os.path.join(output_dir, f"{result['camera_tag']}_intrinsics_calibrated.json")
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n标定结果已保存到: {output_path}")


def main():
    print("=" * 60)
    print("MetaSenseCalib - 单个摄像头内参标定")
    print("=" * 60)
    
    # 设置路径
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_folder = os.path.join(data_dir, "data", "example")
    output_dir = os.path.join(data_dir, "outputs", "example", "intrinsics")
    
    # 标定参数
    chessboard_size = (9, 6)
    square_size = 36.0  # 棋盘格方块大小 (mm)
    
    # 标定 RealSense 摄像头
    print("\n" + "-" * 60)
    print("RealSense 摄像头内参标定")
    print("-" * 60)
    rs_result = calibrate_camera(image_folder, "rs", chessboard_size, square_size)
    
    if rs_result:
        save_calibration_result(rs_result, output_dir)
        
        # 加载内置内参
        rs_builtin = load_builtin_intrinsics("rs")
        if rs_builtin:
            print("\n" + "-" * 60)
            print("RealSense 内参对比")
            print("-" * 60)
            rs_comparison = compare_intrinsics(rs_result, rs_builtin)
            if rs_comparison:
                print("\n[标定内参] 相机矩阵:")
                print(np.array(rs_comparison['calibrated_matrix']))
                print("\n[内置内参] 相机矩阵:")
                print(np.array(rs_comparison['builtin_matrix']))
                print("\n[差异] 相机矩阵:")
                print(np.array(rs_comparison['matrix_difference']))
                print("\n[百分比差异] 相机矩阵:")
                print(np.array(rs_comparison['matrix_percent_difference']))
                print(f"\n平均重投影误差: {rs_comparison['mean_reprojection_error']:.3f} pixels")
    
    # 标定 Quest3 摄像头
    print("\n" + "-" * 60)
    print("Quest3 摄像头内参标定")
    print("-" * 60)
    q3_result = calibrate_camera(image_folder, "q3", chessboard_size, square_size)
    
    if q3_result:
        save_calibration_result(q3_result, output_dir)
        
        # 加载内置内参
        q3_builtin = load_builtin_intrinsics("q3")
        if q3_builtin:
            print("\n" + "-" * 60)
            print("Quest3 内参对比")
            print("-" * 60)
            q3_comparison = compare_intrinsics(q3_result, q3_builtin)
            if q3_comparison:
                print("\n[标定内参] 相机矩阵:")
                print(np.array(q3_comparison['calibrated_matrix']))
                print("\n[内置内参] 相机矩阵:")
                print(np.array(q3_comparison['builtin_matrix']))
                print("\n[差异] 相机矩阵:")
                print(np.array(q3_comparison['matrix_difference']))
                print("\n[百分比差异] 相机矩阵:")
                print(np.array(q3_comparison['matrix_percent_difference']))
                print(f"\n平均重投影误差: {q3_comparison['mean_reprojection_error']:.3f} pixels")
    
    print("\n" + "=" * 60)
    print("内参标定完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
