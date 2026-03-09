import os
import cv2
import numpy as np
import json
import argparse
import glob

# 尝试导入cupy，如果不可用则使用numpy
try:
    import cupy as cp
    USE_GPU = True
except ImportError:
    print("CuPy not available, using NumPy instead")
    cp = np
    USE_GPU = False


def load_calib(json_path, quest3_scale=1.0):
    """Load calibration data from JSON file
    
    Args:
        json_path: Path to calibration JSON file
        quest3_scale: Scale factor for Quest3 intrinsics
        
    Returns:
        T: Transformation matrix from RealSense to Quest3
        T_inv: Inverse transformation matrix
        K_rs: RealSense intrinsics matrix
        K_q3: Scaled Quest3 intrinsics matrix
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    T = np.array(data['transformation_matrix'])
    T_inv = np.linalg.inv(T)
    K_rs = np.array(data['realsense_intrinsics'])
    K_q3 = np.array(data['quest3_intrinsics'])
    
    # Scale Quest3 intrinsics
    K_q3_scaled = K_q3.copy()
    K_q3_scaled[0, 0] *= quest3_scale
    K_q3_scaled[1, 1] *= quest3_scale
    K_q3_scaled[0, 2] *= quest3_scale
    K_q3_scaled[1, 2] *= quest3_scale
    
    return T, T_inv, K_rs, K_q3_scaled


def warp_view(src_img, src_K, dst_K, T, out_shape, depth=100000):
    """Warp image from source camera view to destination camera view
    
    Args:
        src_img: Source image (grayscale)
        src_K: Source camera intrinsics
        dst_K: Destination camera intrinsics
        T: 4x4 transformation matrix
        out_shape: Output image shape (height, width)
        depth: Assumed depth for warping
        
    Returns:
        Warped image
    """
    h, w = out_shape
    
    # Generate target pixel grid
    v, u = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
    u_flat = u.ravel()
    v_flat = v.ravel()
    
    # Convert target pixels to camera coordinates
    fx, fy = dst_K[0, 0], dst_K[1, 1]
    cx, cy = dst_K[0, 2], dst_K[1, 2]
    x = (u_flat - cx) * depth / fx
    y = (v_flat - cy) * depth / fy
    
    # Create homogeneous points
    pts_dst = np.stack([x, y, np.full_like(x, depth)], axis=1)
    pts_dst_h = np.concatenate([pts_dst, np.ones((pts_dst.shape[0], 1), dtype=pts_dst.dtype)], axis=1)
    
    # Transform to source camera coordinate system
    Tinv = np.linalg.inv(T)
    pts_src_h = (Tinv @ pts_dst_h.T).T
    pts_src = pts_src_h[:, :3]
    
    # Convert source camera coordinates to pixels
    fx_s, fy_s = src_K[0, 0], src_K[1, 1]
    cx_s, cy_s = src_K[0, 2], src_K[1, 2]
    u_src = fx_s * pts_src[:, 0] / pts_src[:, 2] + cx_s
    v_src = fy_s * pts_src[:, 1] / pts_src[:, 2] + cy_s
    u_src = np.round(u_src).astype(np.int32)
    v_src = np.round(v_src).astype(np.int32)
    
    # Sample source image
    dst_img = np.zeros((h * w,), dtype=src_img.dtype)
    mask = (u_src >= 0) & (u_src < src_img.shape[1]) & (v_src >= 0) & (v_src < src_img.shape[0])
    dst_img[mask] = src_img[v_src[mask], u_src[mask]]
    dst_img = dst_img.reshape((h, w))
    
    return dst_img


def main():
    """Main function for video warp demo"""
    parser = argparse.ArgumentParser(description='Video warp demo for camera calibration')
    parser.add_argument('--calib', type=str, default='outputs/example/extrinsics/calibration_result.json',
                        help='Path to calibration JSON file')
    parser.add_argument('--rs_dir', type=str, default='data/example',
                        help='Directory containing RealSense images')
    parser.add_argument('--q3_dir', type=str, default='data/example',
                        help='Directory containing Quest3 images')
    parser.add_argument('--output', type=str, default='outputs/example/visualization/warp_demo.mp4',
                        help='Output video path')
    parser.add_argument('--scale', type=float, default=0.5,
                        help='Scale factor for Quest3 intrinsics')
    parser.add_argument('--fps', type=int, default=10,
                        help='Output video FPS')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Load calibration data
    print(f"Loading calibration from {args.calib}")
    T, T_inv, K_rs, K_q3 = load_calib(args.calib, quest3_scale=args.scale)
    
    # Load image paths
    rs_imgs = sorted(glob.glob(os.path.join(args.rs_dir, 'rs_*.png')))
    q3_imgs = sorted(glob.glob(os.path.join(args.q3_dir, 'q3_*.png')))
    
    if not rs_imgs or not q3_imgs:
        print("No images found! Please check the input directories.")
        return
    
    min_len = min(len(rs_imgs), len(q3_imgs))
    print(f"Found {len(rs_imgs)} RealSense images and {len(q3_imgs)} Quest3 images")
    print(f"Processing {min_len} image pairs")
    
    # Determine output size
    img_rs = cv2.imread(rs_imgs[0], 0)
    img_q3 = cv2.imread(q3_imgs[0], 0)
    
    if img_rs is None or img_q3 is None:
        print("Failed to read test images!")
        return
    
    h, w = img_rs.shape
    h2, w2 = img_q3.shape
    out_h = max(h, h2)
    out_w = max(w, w2)
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc, args.fps, (out_w * 2, out_h * 2), True)
    
    # Process each image pair
    for i in range(min_len):
        img_rs = cv2.imread(rs_imgs[i], 0)
        img_q3 = cv2.imread(q3_imgs[i], 0)
        
        if img_rs is None or img_q3 is None:
            print(f"Skipping frame {i} - failed to read images")
            continue
        
        # Perform warping
        rs2q3 = warp_view(img_rs, K_rs, K_q3, T, (out_h, out_w))
        q32rs = warp_view(img_q3, K_q3, K_rs, T_inv, (out_h, out_w))
        
        # Create canvas
        canvas = np.zeros((out_h * 2, out_w * 2), dtype=np.uint8)
        canvas[:h, :w] = img_rs
        canvas[:h2, w:w*2] = img_q3
        canvas[out_h:out_h+out_h, :out_w] = rs2q3
        canvas[out_h:out_h+out_h, out_w:out_w+out_w] = q32rs
        
        # Convert to color and add labels
        canvas_color = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
        cv2.putText(canvas_color, 'RealSense', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(canvas_color, 'Quest3', (w + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(canvas_color, 'RS->Q3', (10, out_h + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(canvas_color, 'Q3->RS', (w + 10, out_h + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Write frame
        out.write(canvas_color)
        print(f'Frame {i+1}/{min_len}')
    
    # Release resources
    out.release()
    print(f'Saved warp demo video to {args.output}')


if __name__ == '__main__':
    main()
