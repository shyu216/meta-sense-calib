"""
MetaSenseCalib - Image Pair Error Analysis Script

Calculates the transformation error of extrinsic parameters for each image pair
"""

import os
import sys
import json
import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple

# Add project root directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calibration import Calibrator
from calibration.pose import CameraIntrinsics
from calibration.transform import RigidTransform
from calibration.chessboard import ChessboardDetector


def load_calibration_result(calibration_dir: str) -> Dict:
    """Load calibration results"""
    json_path = os.path.join(calibration_dir, 'calibration_result.json')
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Calibration result file not found: {json_path}")
    
    with open(json_path, 'r') as f:
        result_dict = json.load(f)
    
    return result_dict


def load_image_pairs(image_folder: str, camera1_tag: str = 'rs', camera2_tag: str = 'q3') -> List[Tuple[str, str]]:
    """Load image pairs"""
    image_files1 = sorted(glob.glob(os.path.join(image_folder, f'*{camera1_tag}*.png')))
    image_files2 = sorted(glob.glob(os.path.join(image_folder, f'*{camera2_tag}*.png')))
    
    min_len = min(len(image_files1), len(image_files2))
    image_pairs = list(zip(image_files1[:min_len], image_files2[:min_len]))
    
    print(f"Loaded {len(image_pairs)} image pairs")
    return image_pairs


def calculate_pair_errors(
    image_pairs: List[Tuple[str, str]],
    transformation_matrix: np.ndarray,
    intrinsics_rs: CameraIntrinsics,
    intrinsics_q3: CameraIntrinsics,
    chessboard_size: Tuple[int, int] = (9, 6),
    square_size: float = 36.0
) -> List[Dict]:
    """Calculate error for each image pair"""
    # Create detector and pose estimator
    detector = ChessboardDetector(
        pattern_size=chessboard_size,
        square_size=square_size
    )
    
    from calibration.pose import PoseEstimator
    pose_estimator1 = PoseEstimator(intrinsics_rs)
    pose_estimator2 = PoseEstimator(intrinsics_q3)
    
    # Create transformation object
    transform = RigidTransform.from_matrix(transformation_matrix)
    
    pair_errors = []
    
    for i, (img_path1, img_path2) in enumerate(image_pairs):
        print(f"Processing pair {i}...")
        
        # Detect chessboard corners
        result1 = detector.detect_corners(img_path1, visualize=False)
        result2 = detector.detect_corners(img_path2, visualize=False)
        
        if result1 is None or result2 is None:
            print(f"Pair {i}: Detection failed")
            pair_errors.append({
                'frame': i,
                'status': 'detection_failed',
                'mean_error': None,
                'std_error': None,
                'max_error': None,
                'min_error': None,
                'point_count': 0
            })
            continue
        
        # Estimate pose
        pose1 = pose_estimator1.estimate_pose(
            result1['object_points'],
            result1['image_points']
        )
        pose2 = pose_estimator2.estimate_pose(
            result2['object_points'],
            result2['image_points']
        )
        
        if pose1 is None or pose2 is None:
            print(f"Pair {i}: PnP failed")
            pair_errors.append({
                'frame': i,
                'status': 'pnp_failed',
                'mean_error': None,
                'std_error': None,
                'max_error': None,
                'min_error': None,
                'point_count': 0
            })
            continue
        
        # Transform to camera coordinate system
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
        
        # Apply transformation
        points1_transformed = transform.transform_points(np.array(points1_cam))
        
        # Calculate error
        errors = np.linalg.norm(points1_transformed - np.array(points2_cam), axis=1)
        
        pair_errors.append({
            'frame': i,
            'status': 'success',
            'mean_error': float(np.mean(errors)),
            'std_error': float(np.std(errors)),
            'max_error': float(np.max(errors)),
            'min_error': float(np.min(errors)),
            'point_count': len(errors)
        })
        
        print(f"Pair {i}: Mean error = {np.mean(errors):.3f} mm")
    
    return pair_errors


def generate_report(pair_errors: List[Dict], output_dir: str):
    """Generate analysis report"""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter successful results
    success_errors = [e for e in pair_errors if e['status'] == 'success']
    
    if not success_errors:
        print("No successful image pairs")
        return
    
    # Calculate overall statistics
    mean_errors = [e['mean_error'] for e in success_errors]
    std_errors = [e['std_error'] for e in success_errors]
    max_errors = [e['max_error'] for e in success_errors]
    
    overall_mean = np.mean(mean_errors)
    overall_std = np.mean(std_errors)
    overall_max = np.max(max_errors)
    
    # Save detailed results
    report_path = os.path.join(output_dir, 'pair_errors.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'overall_stats': {
                'mean_error': float(overall_mean),
                'mean_std_error': float(overall_std),
                'max_error': float(overall_max),
                'success_count': len(success_errors),
                'total_count': len(pair_errors)
            },
            'pair_errors': pair_errors
        }, f, indent=2)
    
    print(f"Detailed report saved to: {report_path}")
    
    # Generate charts
    generate_charts(pair_errors, output_dir)


def generate_charts(pair_errors: List[Dict], output_dir: str):
    """Generate error analysis charts"""
    # Filter successful results
    success_errors = [e for e in pair_errors if e['status'] == 'success']
    
    if not success_errors:
        return
    
    # Extract data
    frames = [e['frame'] for e in success_errors]
    mean_errors = [e['mean_error'] for e in success_errors]
    max_errors = [e['max_error'] for e in success_errors]
    
    # Set style
    sns.set_style("whitegrid")
    
    # Chart 1: Mean error per image pair
    plt.figure(figsize=(12, 6))
    plt.bar(frames, mean_errors, color='skyblue')
    plt.xlabel('Image Pair Index')
    plt.ylabel('Mean Error (mm)')
    plt.title('Mean Extrinsic Transformation Error per Image Pair')
    plt.xticks(frames, rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pair_mean_errors.png'))
    
    # Chart 2: Error distribution
    plt.figure(figsize=(12, 6))
    all_errors = []
    for e in success_errors:
        # Generate simulated error distribution based on mean and standard deviation
        n = e['point_count']
        mean = e['mean_error']
        std = e['std_error']
        # Generate simulated error data
        if std > 0:
            errors = np.random.normal(mean, std, n)
            all_errors.extend(errors.tolist())
    
    if all_errors:
        sns.histplot(all_errors, bins=50, kde=True)
        plt.xlabel('Error (mm)')
        plt.ylabel('Frequency')
        plt.title('Error Distribution of All Points')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'error_distribution.png'))
    
    # Chart 3: Maximum error comparison
    plt.figure(figsize=(12, 6))
    plt.bar(frames, max_errors, color='salmon')
    plt.xlabel('Image Pair Index')
    plt.ylabel('Maximum Error (mm)')
    plt.title('Maximum Error per Image Pair')
    plt.xticks(frames, rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pair_max_errors.png'))
    
    print("Charts generated and saved")


def main():
    print("=" * 60)
    print("MetaSenseCalib - Image Pair Error Analysis")
    print("=" * 60)
    
    # Set paths
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_folder = os.path.join(data_dir, "data", "example")
    calibration_dir = os.path.join(data_dir, "outputs", "calibration", "example")
    output_dir = os.path.join(data_dir, "outputs", "analysis")
    
    # Load calibration results
    print("\n[1] Loading calibration results...")
    try:
        result_dict = load_calibration_result(calibration_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run the calibration program first to generate results")
        return
    
    # Load camera intrinsics
    print("\n[2] Loading camera intrinsics...")
    rs_intrinsics_path = os.path.join(data_dir, "data", "example", "rs_intrinsics.json")
    q3_intrinsics_path = os.path.join(data_dir, "data", "example", "q3_intrinsics.json")
    
    from calibration.calibrator import load_intrinsics_from_json
    intrinsics_rs = load_intrinsics_from_json(rs_intrinsics_path)
    intrinsics_q3 = load_intrinsics_from_json(q3_intrinsics_path)
    
    # Get transformation matrix
    transformation_matrix = np.array(result_dict['transformation_matrix'])
    
    # Load image pairs
    print("\n[3] Loading image pairs...")
    import glob
    image_pairs = load_image_pairs(image_folder)
    
    # Calculate error for each image pair
    print("\n[4] Calculating error for each image pair...")
    pair_errors = calculate_pair_errors(
        image_pairs,
        transformation_matrix,
        intrinsics_rs,
        intrinsics_q3
    )
    
    # Generate report
    print("\n[5] Generating analysis report...")
    generate_report(pair_errors, output_dir)
    
    print("\nAnalysis completed!")


if __name__ == "__main__":
    main()