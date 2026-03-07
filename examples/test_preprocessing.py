"""
MetaSenseCalib - 图片预处理效果测试脚本

测试不同预处理方法对棋盘格角点检测的影响
"""

import os
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calibration.chessboard import ChessboardDetector


def preprocess_image_original(img):
    """原始图片（无预处理）"""
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def preprocess_image_gamma(img, gamma=1.5):
    """伽马校正"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in range(256)]).astype(np.uint8)
    return cv2.LUT(gray, table)


def preprocess_image_contrast(img, alpha=1.5, beta=0):
    """对比度增强"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)


def preprocess_image_equalize(img):
    """直方图均衡化"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)


def preprocess_image_clahe(img, clipLimit=2.0, tileGridSize=(8, 8)):
    """自适应直方图均衡化"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
    return clahe.apply(gray)


def preprocess_image_combined(img):
    """组合预处理"""
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 伽马校正
    invGamma = 1.0 / 1.5
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in range(256)]).astype(np.uint8)
    gray = cv2.LUT(gray, table)
    
    # 对比度增强
    gray = cv2.convertScaleAbs(gray, alpha=1.2, beta=0)
    
    # 自适应直方图均衡化
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    
    return gray


def test_preprocessing_methods():
    """Test different preprocessing methods"""
    print("=" * 60)
    print("MetaSenseCalib - Image Preprocessing Effect Test")
    print("=" * 60)
    
    # Set paths
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path = os.path.join(data_dir, "data", "example", "rs_0017.png")
    output_dir = os.path.join(data_dir, "outputs", "analysis", "pair_17_preprocessing_test")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load image
    print(f"\n[1] Loading test image: {image_path}")
    img = cv2.imread(image_path)
    
    if img is None:
        print("Error: Image loading failed")
        return
    
    print(f"Image size: {img.shape[:2]}")
    
    # Preprocessing methods list
    preprocessing_methods = [
        ("Original", preprocess_image_original),
        ("Gamma Correction (1.5)", preprocess_image_gamma),
        ("Contrast Enhancement (1.5x)", preprocess_image_contrast),
        ("Histogram Equalization", preprocess_image_equalize),
        ("CLAHE", preprocess_image_clahe),
        ("Combined Preprocessing", preprocess_image_combined)
    ]
    
    # Create chessboard detector
    detector = ChessboardDetector(
        pattern_size=(9, 6),
        square_size=36.0,
        need_gamma_correction=False  # We handle gamma correction ourselves
    )
    
    # Test each preprocessing method
    results = []
    
    for method_name, preprocess_func in preprocessing_methods:
        print(f"\n[2] Testing preprocessing method: {method_name}")
        
        # Preprocess image
        processed_img = preprocess_func(img)
        
        # Save preprocessed image
        processed_path = os.path.join(output_dir, f"rs_0017_{method_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')}.png")
        # cv2.imwrite(processed_path, processed_img)
        
        # Detect chessboard corners
        result = detector.detect_corners_from_array(processed_img, visualize=True)
        
        if result is not None:
            # Draw chessboard corners
            vis_img = result['visualization']
            cv2.putText(vis_img, f"{method_name}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Save detection result
            detection_path = os.path.join(output_dir, f"rs_0017_{method_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')}_detection.png")
            cv2.imwrite(detection_path, vis_img)
            
            corner_count = len(result['image_points'])
            print(f"  Detected corner count: {corner_count}")
            
            results.append({
                'method': method_name,
                'corner_count': corner_count,
                'success': True,
                'processed_path': processed_path,
                'detection_path': detection_path
            })
        else:
            print("  Detection failed")
            # Skip failed detections
            continue
    
    # Generate analysis report
    print("\n[3] Generating analysis report...")
    generate_analysis_report(results, output_dir)
    
    print("\nTest completed! Results saved to:")
    print(f"  {output_dir}")


def generate_analysis_report(results: List[Dict], output_dir: str):
    """Generate analysis report"""
    # Create results table
    report_path = os.path.join(output_dir, "preprocessing_analysis.txt")
    with open(report_path, 'w') as f:
        f.write("MetaSenseCalib - Preprocessing Methods Analysis Report\n")
        f.write("=" * 60 + "\n")
        f.write(f"{'Preprocessing Method':<30} {'Corner Count':<10} {'Status':<10}\n")
        f.write("-" * 60 + "\n")
        
        for result in results:
            status = "Success" if result['success'] else "Failed"
            f.write(f"{result['method']:<30} {result['corner_count']:<10} {status:<10}\n")
        
        f.write("=" * 60 + "\n")
    
    print(f"Analysis report saved to: {report_path}")
    
    # Generate visualization chart
    plt.figure(figsize=(12, 6))
    methods = [r['method'] for r in results]
    corner_counts = [r['corner_count'] for r in results]
    
    bars = plt.bar(methods, corner_counts, color='skyblue')
    plt.xlabel('Preprocessing Method')
    plt.ylabel('Detected Corner Count')
    plt.title('Chessboard Corner Detection Performance of Different Preprocessing Methods')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height}', ha='center', va='bottom')
    
    chart_path = os.path.join(output_dir, "preprocessing_comparison.png")
    plt.savefig(chart_path)
    print(f"Comparison chart saved to: {chart_path}")


def main():
    test_preprocessing_methods()


if __name__ == "__main__":
    main()
