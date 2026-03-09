# Intrinsics Calibration Detailed Guide

## 1. Intrinsics Calibration Principle

Intrinsics calibration is the fundamental step in camera calibration, which describes the internal optical characteristics of a camera and establishes the mapping relationship between pixel coordinates and 3D space.

### 1.1 Camera Model

The camera imaging process can be described using the pinhole camera model:

```
[ u ]   [ f_x  0  c_x ] [ X ]
[ v ] = [  0  f_y c_y ] [ Y ]
[ 1 ]   [  0   0   1 ] [ Z ]
```

Where:
-  (u, v)  are pixel coordinates
-  (X, Y, Z)  are 3D space coordinates
-  f_x, f_y  are focal lengths (in pixels)
-  c_x, c_y  are principal point coordinates (in pixels)

### 1.2 Pixel to Ray Relationship

The essence of intrinsics calibration is to establish a **mapping from pixel coordinates to spatial rays**. Each pixel corresponds to a ray in space that starts from the camera's optical center, passes through the pixel, and extends to infinity.

![Pixel to Ray Relationship](https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=camera%20pixel%20to%20ray%20mapping%20diagram%2C%20optical%20axis%2C%20focal%20length%2C%20principal%20point&image_size=square_hd)

## 2. Intrinsics Calibration Steps

### 2.1 Preparation

1. **Chessboard Preparation**: Use a standard chessboard with known square size (e.g., 36mm)
2. **Image Capture**: Take at least 10-20 images of the chessboard from different angles
3. **Software Preparation**: Use libraries like OpenCV for corner detection and calibration calculation

### 2.2 Calibration Process

1. **Corner Detection**: Use `findChessboardCorners` to detect internal corners of the chessboard
2. **Sub-pixel Refinement**: Use `cornerSubPix` to improve corner detection accuracy
3. **Correspondence Establishment**: Establish correspondence between pixel points and physical chessboard points
4. **Intrinsics Calculation**: Use `calibrateCamera` function to solve for camera intrinsics
5. **Calibration Verification**: Calculate reprojection error to evaluate calibration quality

## 3. Actual Calibration Results Analysis

### 3.1 RealSense D415 Calibration Results

| Parameter | Calibrated Value | Built-in Value | Difference |
|-----------|------------------|----------------|------------|
| Focal Length fx | 609.21 | 610.33 | -0.18% |
| Focal Length fy | 597.05 | 609.95 | -2.11% |
| Principal Point cx | 334.48 | 325.21 | +2.85% |
| Principal Point cy | 235.44 | 229.97 | +2.38% |
| Mean Reprojection Error | 0.139 pixels | - | - |

### 3.2 Quest3 Calibration Results

| Parameter | Calibrated Value | Built-in Value | Difference |
|-----------|------------------|----------------|------------|
| Focal Length fx | 879.60 | 869.13 | +1.20% |
| Focal Length fy | 863.39 | 869.13 | -0.66% |
| Principal Point cx | 646.87 | 644.64 | +0.35% |
| Principal Point cy | 641.39 | 639.26 | +0.33% |
| Mean Reprojection Error | 0.017 pixels | - | - |

### 3.3 Result Analysis

1. **Calibration Accuracy**:
   - Quest3 calibration accuracy is very high, with mean reprojection error of only 0.017 pixels
   - RealSense calibration accuracy is also good, with mean reprojection error of 0.139 pixels

2. **Difference from Built-in Parameters**:
   - Quest3 calibration results are very close to built-in parameters, with differences within 1.3%
   - RealSense calibration results have some differences from built-in parameters, especially for fy value (-2.11%)

3. **Recommendations**:
   - For high-precision applications, use the calibrated intrinsics
   - For general applications, built-in parameters can also meet requirements

## 4. Visualization Results

### 4.1 Chessboard Corner Detection

![Chessboard Corner Detection](../../outputs/example/visualization/chessboard_detection_step.png)

### 4.2 Physical Chessboard Distances

![Physical Chessboard Distances](../../outputs/example/visualization/physical_distances.png)

### 4.3 Pixel to Physical Distance Relationship

![Pixel to Physical Distance Relationship](../../outputs/example/visualization/pixel_physical_relation.png)

### 4.4 Calibration Results

#### 4.4.1 RealSense D415 Calibration Results

| Parameter | Calibrated Value | Built-in Value | Difference |
|-----------|------------------|----------------|------------|
| Focal Length fx | 609.21 | 610.33 | -0.18% |
| Focal Length fy | 597.05 | 609.95 | -2.11% |
| Principal Point cx | 334.48 | 325.21 | +2.85% |
| Principal Point cy | 235.44 | 229.97 | +2.38% |
| Mean Reprojection Error | 0.139 pixels | - | - |

#### 4.4.2 Quest3 Calibration Results

| Parameter | Calibrated Value | Built-in Value | Difference |
|-----------|------------------|----------------|------------|
| Focal Length fx | 879.60 | 869.13 | +1.20% |
| Focal Length fy | 863.39 | 869.13 | -0.66% |
| Principal Point cx | 646.87 | 644.64 | +0.35% |
| Principal Point cy | 641.39 | 639.26 | +0.33% |
| Mean Reprojection Error | 0.017 pixels | - | - |

#### 4.4.3 Result Analysis

1. **Calibration Accuracy**:
   - Quest3 calibration accuracy is very high, with mean reprojection error of only 0.017 pixels
   - RealSense calibration accuracy is also good, with mean reprojection error of 0.139 pixels

2. **Difference from Built-in Parameters**:
   - Quest3 calibration results are very close to built-in parameters, with differences within 1.3%
   - RealSense calibration results have some differences from built-in parameters, especially for fy value (-2.11%)

3. **Recommendations**:
   - For high-precision applications, use the calibrated intrinsics
   - For general applications, built-in parameters can also meet requirements

## 5. Code Example

Use the `intr-visual.py` script to visualize the entire intrinsics calibration process:

```bash
python examples/intr-visual.py
```

This script will:
1. Detect chessboard corners
2. Visualize physical chessboard distances
3. Show the relationship between pixel and physical distances
4. Display calibration results

## 6. Common Issues and Solutions

### 6.1 Corner Detection Failure

**Reasons**:
- Blurry or overexposed images
- Partially occluded chessboard
- Excessively tilted angles

**Solutions**:
- Ensure images are clear with uniform lighting
- Ensure the entire chessboard is visible
- Capture images from different angles
- Use preprocessing methods to enhance contrast

### 6.2 Low Calibration Accuracy

**Reasons**:
- Insufficient number of images
- Inadequate angle coverage
- Inaccurate chessboard square size measurement

**Solutions**:
- Capture at least 15-20 images
- Ensure coverage of different angles and distances
- Accurately measure chessboard square size

### 6.3 Large Reprojection Error

**Reasons**:
- Severe lens distortion
- Non-flat calibration board
- Inaccurate detected corners

**Solutions**:
- Use higher-order distortion models
- Ensure the calibration board is flat
- Adjust corner detection parameters

## 7. Summary

Intrinsics calibration is the foundation of camera calibration, establishing the mapping relationship between pixel coordinates and 3D space. Through calibration, we can obtain the internal optical parameters of the camera, laying the foundation for subsequent extrinsic calibration and 3D reconstruction.

Actual calibration results show that both Quest3 and RealSense D415 have high calibration accuracy, with differences from built-in parameters within acceptable ranges. For high-precision applications, it is recommended to use the calibrated intrinsics to achieve the best results.