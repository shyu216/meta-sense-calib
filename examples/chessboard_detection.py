"""
MetaSenseCalib - 棋盘格检测示例

用于生成 docs/images/chessboard_detection.png
"""

import os
import sys
import cv2
import numpy as np

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calibration.chessboard import ChessboardDetector

def main():
    print("=" * 60)
    print("MetaSenseCalib - 棋盘格检测示例")
    print("=" * 60)

    # 配置棋盘格检测参数
    chessboard_size = (9, 6)  # 棋盘格内角点数量
    square_size = 36.0  # 棋盘格方块大小（毫米）

    # 创建棋盘格检测器
    detector = ChessboardDetector(
        pattern_size=chessboard_size,
        square_size=square_size,
        need_gamma_correction=False,
        gamma_value=2.2
    )

    # 获取示例图像路径
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path = os.path.join(data_dir, "data", "example", "rs_0007.png")

    if not os.path.exists(image_path):
        print(f"错误: 示例图像不存在: {image_path}")
        print("请确保示例数据已正确下载")
        return

    print(f"\n[1] 加载示例图像: {image_path}")

    # 检测棋盘格
    result = detector.detect_corners(image_path, visualize=True)

    if result is None:
        print("[错误] 棋盘格检测失败")
        return

    print("[成功] 棋盘格检测完成")
    print(f"检测到的角点数量: {len(result['image_points'])}")

    # 生成可视化图像
    img = result['image']
    corners = result['image_points']

    # 绘制棋盘格角点
    cv2.drawChessboardCorners(img, chessboard_size, corners, True)

    # 添加标题
    cv2.putText(img, "Chessboard Detection", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 保存结果图像
    output_dir = os.path.join(data_dir, "docs", "images")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "chessboard_detection.png")
    cv2.imwrite(output_path, img)

    print(f"\n[2] 结果保存到: {output_path}")
    print("\n棋盘格检测示例完成！")

if __name__ == "__main__":
    main()
