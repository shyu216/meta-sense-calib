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
    
    # 增强可视化效果
    img = cv2.imread(img_path)
    vis_img = result['visualization']
    
    # 添加角点编号
    for i, corner in enumerate(result['image_points']):
        x, y = int(corner[0][0]), int(corner[0][1])
        cv2.putText(vis_img, str(i), (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # 创建对比图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    ax1.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ax1.set_title('Original Image')
    ax1.axis('off')
    
    ax2.imshow(cv2.cvtColor(vis_img, cv2.COLOR_BGR2RGB))
    ax2.set_title('Chessboard Detection')
    ax2.axis('off')
    
    # 保存检测结果
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "example", "visualization")
    os.makedirs(output_dir, exist_ok=True)
    detection_path = os.path.join(output_dir, "chessboard_detection_step.png")
    plt.savefig(detection_path, bbox_inches='tight')
    plt.close()
    
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
    
    # 创建更直观的可视化
    fig = plt.figure(figsize=(18, 8))
    
    # 2D 视图
    ax1 = fig.add_subplot(121)
    # 绘制棋盘格
    for i in range(chessboard_size[1]):
        for j in range(chessboard_size[0]):
            ax1.scatter(objp[i*chessboard_size[0]+j, 0], objp[i*chessboard_size[0]+j, 1], 
                      c='b', marker='o', s=50)
    
    # 绘制连接线
    for i in range(chessboard_size[1]):
        ax1.plot(objp[i*chessboard_size[0]:(i+1)*chessboard_size[0], 0], 
                objp[i*chessboard_size[0]:(i+1)*chessboard_size[0], 1], 'r-')
    
    for j in range(chessboard_size[0]):
        ax1.plot(objp[j::chessboard_size[0], 0], 
                objp[j::chessboard_size[0], 1], 'r-')
    
    # 添加坐标标签和距离标注
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.set_title(f'Physical Chessboard Coordinates (Square size: {square_size}mm)')
    ax1.grid(True)
    ax1.set_aspect('equal')
    
    # 添加距离标注
    ax1.annotate(f'{square_size}mm', xy=(square_size/2, 0), xytext=(square_size/2, -10),
                arrowprops=dict(arrowstyle='-', connectionstyle='arc3'),
                ha='center', va='top')
    ax1.annotate(f'{square_size}mm', xy=(0, square_size/2), xytext=(-10, square_size/2),
                arrowprops=dict(arrowstyle='-', connectionstyle='arc3'),
                ha='right', va='center')
    
    # 3D 视图
    ax2 = fig.add_subplot(122, projection='3d')
    # 绘制棋盘格
    for i in range(chessboard_size[1]):
        for j in range(chessboard_size[0]):
            ax2.scatter(objp[i*chessboard_size[0]+j, 0], objp[i*chessboard_size[0]+j, 1], objp[i*chessboard_size[0]+j, 2], 
                      c='b', marker='o', s=50)
    
    # 绘制连接线
    for i in range(chessboard_size[1]):
        ax2.plot(objp[i*chessboard_size[0]:(i+1)*chessboard_size[0], 0], 
                objp[i*chessboard_size[0]:(i+1)*chessboard_size[0], 1], 
                objp[i*chessboard_size[0]:(i+1)*chessboard_size[0], 2], 'r-')
    
    for j in range(chessboard_size[0]):
        ax2.plot(objp[j::chessboard_size[0], 0], 
                objp[j::chessboard_size[0], 1], 
                objp[j::chessboard_size[0], 2], 'r-')
    
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.set_zlabel('Z (mm)')
    ax2.set_title('3D Physical Chessboard Coordinates')
    ax2.grid(True)
    
    # 设置3D视角
    ax2.view_init(vertical_axis='y', azim=170, elev=10)
    
    # 保存可视化结果
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "example", "visualization")
    os.makedirs(output_dir, exist_ok=True)
    physical_path = os.path.join(output_dir, "physical_distances.png")
    plt.tight_layout()
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
    
    # 计算重投影误差
    mean_error = 0
    for i in range(len(obj_points)):
        imgpoints2, _ = cv2.projectPoints(obj_points, rvecs[0], tvecs[0], mtx, dist)
        error = cv2.norm(image_points, imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        mean_error += error
    mean_error = mean_error / len(obj_points)
    
    # 可视化像素与物理坐标对应关系
    fig = plt.figure(figsize=(18, 8))
    
    # 左图：图像点 (像素坐标) 与重投影点
    ax1 = fig.add_subplot(122)
    ax1.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ax1.scatter(image_points[:, 0, 0], image_points[:, 0, 1], c='r', s=20, marker='+', label='Detected Points')
    
    # 绘制重投影点
    imgpoints2, _ = cv2.projectPoints(obj_points, rvecs[0], tvecs[0], mtx, dist)
    ax1.scatter(imgpoints2[:, 0, 0], imgpoints2[:, 0, 1], c='g', s=20, marker='x', label='Reprojected Points')
    
    # 标记四个角点
    corner_indices = [0, 8, 45, 53]  # 左上、右上、左下、右下
    corner_colors = ['blue', 'green', 'yellow', 'cyan']
    corner_labels = ['Top-Left', 'Top-Right', 'Bottom-Left', 'Bottom-Right']
    for i, idx in enumerate(corner_indices):
        ax1.scatter(image_points[idx, 0, 0], image_points[idx, 0, 1], 
                    c=corner_colors[i], s=50, marker='o', label=corner_labels[i])
    
    # 绘制连接线
    for i in range(len(image_points)):
        ax1.plot([image_points[i, 0, 0], imgpoints2[i, 0, 0]], 
                 [image_points[i, 0, 1], imgpoints2[i, 0, 1]], 'y-', alpha=0.5)
    
    ax1.set_title('Image Points vs Reprojected Points')
    ax1.set_xlabel('Pixel X')
    ax1.set_ylabel('Pixel Y')
    ax1.legend()
    ax1.grid(True)
    
    # 右图：3D空间中的棋盘格平面
    ax2 = fig.add_subplot(121, projection='3d')
    
    # 将旋转向量转换为旋转矩阵
    R, _ = cv2.Rodrigues(rvecs[0])
    
    # 计算相机空间中的3D点
    camera_points = (R @ obj_points.T + tvecs[0]).T
    
    # --- 新增：修正 Y 轴方向 ---
    camera_points[:, 1] = -camera_points[:, 1] 

    camera_points[:, 0] = -camera_points[:, 0] 

    
    
    # 绘制棋盘格角点
    ax2.scatter(camera_points[:, 0], camera_points[:, 1], camera_points[:, 2], c='b', marker='o', s=50)
    
    # 计算棋盘格大小 (假设标准的9x6棋盘格)
    chessboard_cols, chessboard_rows = 9, 6
    
    # 绘制棋盘格边缘
    for i in range(chessboard_rows):
        row_points = camera_points[i*chessboard_cols:(i+1)*chessboard_cols]
        ax2.plot(row_points[:, 0], row_points[:, 1], row_points[:, 2], 'r-')
    
    for j in range(chessboard_cols):
        col_points = camera_points[j::chessboard_cols]
        ax2.plot(col_points[:, 0], col_points[:, 1], col_points[:, 2], 'r-')
    
    
    # 沿着y轴旋转90度
    ax2.view_init(vertical_axis='y', azim=170, elev=10)

    # 添加相机位置标记
    ax2.scatter(0, 0, 0, c='g', marker='^', s=100, label='Camera')

    # 标记四个角点（在ax2中）
    corner_indices = [0, 8, 45, 53]  # 左上、右上、左下、右下
    corner_colors = ['blue', 'green', 'yellow', 'cyan']
    corner_labels = ['Top-Left', 'Top-Right', 'Bottom-Left', 'Bottom-Right']
    for i, idx in enumerate(corner_indices):
        ax2.scatter(camera_points[idx, 0], camera_points[idx, 1], camera_points[idx, 2], 
                    c=corner_colors[i], s=100, marker='o', label=corner_labels[i])
        
    # 设置坐标轴标签
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.set_zlabel('Z (mm)')
    ax2.set_title('3D Chessboard in Camera Space')
    ax2.legend()
    ax2.grid(True)
    
    # 保存可视化结果
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "example", "visualization")
    os.makedirs(output_dir, exist_ok=True)
    relation_path = os.path.join(output_dir, "pixel_physical_relation.png")
    plt.tight_layout()
    plt.savefig(relation_path, bbox_inches='tight')
    # plt.show()
    plt.close()
    
    print(f"  像素与物理距离关系可视化已保存到: {relation_path}")
    print(f"  重投影误差: {mean_error:.4f} 像素")
    
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
