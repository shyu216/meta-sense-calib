"""
MetaSenseCalib - 内参标定步骤可视化

展示内参标定的各个步骤，包括：
1. 棋盘格角点检测
2. 物理棋盘格距离应用
3. 像素与物理距离关系可视化
4. 标定结果展示
"""

import os
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calibration.chessboard import ChessboardDetector
from calibration.pose import CameraIntrinsics


def visualize_chessboard_detection(img_path: str, chessboard_size: Tuple[int, int] = (9, 6)) -> Dict:
    """
    可视化棋盘格角点检测
    
    Args:
        img_path: 图片路径
        chessboard_size: 棋盘格内角点数量
    
    Returns:
        检测结果
    """
    print("[步骤1] 棋盘格角点检测")
    
    # 创建棋盘格检测器
    detector = ChessboardDetector(
        pattern_size=chessboard_size,
        square_size=36.0
    )
    
    # 检测角点
    result = detector.detect_corners(img_path, visualize=True)
    
    if result is None:
        print("  角点检测失败")
        return None
    
    # 显示检测结果
    img = cv2.imread(img_path)
    vis_img = result['visualization']
    
    # 保存检测结果
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "example", "visualization")
    os.makedirs(output_dir, exist_ok=True)
    detection_path = os.path.join(output_dir, "chessboard_detection_step.png")
    cv2.imwrite(detection_path, vis_img)
    
    print(f"  检测到 {len(result['image_points'])} 个角点")
    print(f"  检测结果已保存到: {detection_path}")
    
    return result


def visualize_physical_distances(chessboard_size: Tuple[int, int] = (9, 6), square_size: float = 36.0):
    """
    可视化物理棋盘格距离
    
    Args:
        chessboard_size: 棋盘格内角点数量
        square_size: 棋盘格方块大小 (mm)
    """
    print("[步骤2] 物理棋盘格距离应用")
    
    # 生成棋盘格对象点
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2) * square_size
    
    # 可视化物理坐标
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # 绘制棋盘格
    for i in range(chessboard_size[1]):
        for j in range(chessboard_size[0]):
            ax.scatter(objp[i*chessboard_size[0]+j, 0], objp[i*chessboard_size[0]+j, 1], objp[i*chessboard_size[0]+j, 2], 
                      c='b', marker='o', s=50)
    
    # 绘制连接线
    for i in range(chessboard_size[1]):
        ax.plot(objp[i*chessboard_size[0]:(i+1)*chessboard_size[0], 0], 
                objp[i*chessboard_size[0]:(i+1)*chessboard_size[0], 1], 
                objp[i*chessboard_size[0]:(i+1)*chessboard_size[0], 2], 'r-')
    
    for j in range(chessboard_size[0]):
        ax.plot(objp[j::chessboard_size[0], 0], 
                objp[j::chessboard_size[0], 1], 
                objp[j::chessboard_size[0], 2], 'r-')
    
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title('Physical Chessboard Coordinates')
    ax.grid(True)
    
    # 保存可视化结果
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "example", "visualization")
    physical_path = os.path.join(output_dir, "physical_distances.png")
    plt.savefig(physical_path, bbox_inches='tight')
    plt.close()
    
    print(f"  物理棋盘格距离可视化已保存到: {physical_path}")
    
    return objp


def visualize_pixel_physical_relation(img_path: str, image_points: np.ndarray, obj_points: np.ndarray):
    """
    可视化像素与物理距离的关系
    
    Args:
        img_path: 图片路径
        image_points: 图像点 (像素坐标)
        obj_points: 对象点 (物理坐标)
    """
    print("[步骤3] 像素与物理距离关系可视化")
    
    # 加载图片
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    
    # 计算标定
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera([obj_points], [image_points], (w, h), None, None)
    
    if not ret:
        print("  标定失败")
        return None
    
    # 可视化像素与物理坐标对应关系
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 左图：图像点 (像素坐标)
    ax1.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ax1.scatter(image_points[:, 0, 0], image_points[:, 0, 1], c='r', s=20, marker='+')
    ax1.set_title('Image Points (Pixel Coordinates)')
    ax1.set_xlabel('Pixel X')
    ax1.set_ylabel('Pixel Y')
    ax1.grid(True)
    
    # 右图：物理坐标
    ax2.scatter(obj_points[:, 0], obj_points[:, 1], c='b', s=50, marker='o')
    ax2.set_title('Object Points (Physical Coordinates)')
    ax2.set_xlabel('Physical X (mm)')
    ax2.set_ylabel('Physical Y (mm)')
    ax2.grid(True)
    ax2.set_aspect('equal')
    
    # 保存可视化结果
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "example", "visualization")
    relation_path = os.path.join(output_dir, "pixel_physical_relation.png")
    plt.savefig(relation_path, bbox_inches='tight')
    plt.close()
    
    print(f"  像素与物理距离关系可视化已保存到: {relation_path}")
    
    return mtx, dist

def main():
    print("=" * 60)
    print("MetaSenseCalib - 内参标定步骤可视化")
    print("=" * 60)
    
    # 设置路径
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_path = os.path.join(data_dir, "data", "example", "rs_0000.png")
    
    if not os.path.exists(img_path):
        print(f"错误: 示例图片不存在: {img_path}")
        return
    
    print(f"使用示例图片: {img_path}")
    
    # 步骤1: 棋盘格角点检测
    detection_result = visualize_chessboard_detection(img_path)
    
    if detection_result is None:
        print("错误: 角点检测失败，无法继续")
        return
    
    # 步骤2: 物理棋盘格距离应用
    obj_points = visualize_physical_distances()
    
    # 步骤3: 像素与物理距离关系可视化
    image_points = detection_result['image_points']
    camera_matrix, distortion_coeffs = visualize_pixel_physical_relation(img_path, image_points, obj_points)
    
    if camera_matrix is None:
        print("错误: 标定失败，无法继续")
        return
    
    print("\n" + "=" * 60)
    print("内参标定步骤可视化完成！")
    print("所有可视化结果已保存到 outputs/example/visualization/ 目录")
    print("=" * 60)


if __name__ == "__main__":
    main()
