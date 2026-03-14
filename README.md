# MetaSenseCalib

<div align="right">
  <a href="README.cn.md">中文</a> | <a href="README.md">English</a>
</div>

![MetaSenseCalib Assembly](docs/images/assembly.png)

A basic pipeline for calibrating Quest3 and RealSense camera systems, aiming to establish precise pixel-to-pixel coordinate transformation between heterogeneous imaging devices. This implementation provides a foundational approach to multi-camera calibration that should help beginners understand the core principles of camera coordinate system alignment.

Your feedback and suggestions are welcome! Feel free to share your thoughts on how we can improve this calibration pipeline.



---

## 🎬 See It In Action

Watch how MetaSenseCalib enables seamless pixel-to-pixel conversion between RealSense and Quest3 cameras:

<div align="center">
  <img src="docs/videos/warp_demo.gif" alt="Warp Demo" style="max-width: 700px; width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
  <p><i>Real-time view transformation between RealSense D415 and Quest3 cameras</i></p>
</div>

📹 <a href="docs/videos/warp_demo.mp4">Download Full Video (MP4)</a>

---

## ✨ Key Features

- 🎯 **Pixel-Perfect Alignment** - Convert coordinates between cameras with sub-pixel accuracy
- 🔧 **Complete Calibration Pipeline** - Intrinsics + extrinsics calibration in one tool
- 📊 **Rich Visualization** - Interactive plots and detailed error analysis
- 🚀 **Easy to Use** - Simple API and command-line interface
- 📁 **Sample Data Included** - Ready-to-run examples with 20 image pairs
- 🎮 **XR-Ready** - Optimized for Quest3 and RealSense D415

---

## 📑 Table of Contents

- [Quick Start](#-quick-start)
- [What is Calibration](#-what-is-calibration)
- [Installation](#-installation)
- [Sample Data](#-sample-data)
- [Detailed Documentation](#-detailed-documentation)
- [Core OpenCV Functions](#-core-opencv-functions)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/shyu216/meta-sense-calib.git
cd meta-sense-calib

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from calibration import Calibrator

# Create calibrator
calibrator = Calibrator(
    intrinsics_rs="data/example/rs_intrinsics.json",
    intrinsics_q3="data/example/q3_intrinsics.json"
)

# Run calibration
result = calibrator.calibrate(
    image_folder="data/example",
    output_dir="outputs/example/extrinsics"
)

# View results
print(f"Transformation matrix:\n{result.transformation_matrix}")
print(f"Rotation matrix:\n{result.rotation_matrix}")
print(f"Translation vector: {result.translation_vector}")
print(f"Euler angles (degrees): X={result.euler_angles[0]:.2f}, Y={result.euler_angles[1]:.2f}, Z={result.euler_angles[2]:.2f}")
print(f"Mean error: {result.mean_error:.3f} mm")
```

### Run Examples

```bash
# Intrinsics calibration visualization
python examples/intr-visual.py

# Extrinsics calibration demo
python examples/extr-demo.py
```

---

## 📖 What is Calibration

### 🎯 Final Goal

The core goal of camera calibration is **to enable pixel-to-pixel conversion between two cameras**. Through calibration, we can:

- Convert pixel coordinates from RealSense camera to Quest3 camera
- Convert pixel coordinates from Quest3 camera to RealSense camera
- Achieve spatial alignment between the two cameras, allowing them to "see" the same 3D world

### 📷 Intrinsics

**Intrinsics** describe the internal optical characteristics of a camera, defining the **mapping relationship between pixels and 3D space**:

- **Focal Length**: Controls the camera's field of view and magnification
- **Principal Point**: The intersection of the camera's optical axis with the imaging plane
- **Distortion Coefficients**: Correct lens distortion

The essence of intrinsics calibration is to establish a mapping from pixel coordinates to spatial rays. Each pixel corresponds to a ray in space that starts from the camera's optical center, passes through the pixel, and extends to infinity.

### 🌍 Extrinsics

**Extrinsics** describe the **relative position and orientation between two cameras**, assuming they are in different 3D reference frames:

- **Rotation Matrix**: Describes the rotation of one camera relative to another
- **Translation Vector**: Describes the position offset of one camera relative to another

The essence of extrinsics calibration is to find a rigid body transformation that converts one camera's 3D coordinate system to another camera's 3D coordinate system.

---

## 📦 Sample Data

The project includes sample datasets located in the `data/example/` directory:

```
data/example/
├── rs_0000.png ~ rs_0019.png   # RealSense D415 images (20 images)
├── q3_0000.png ~ q3_0019.png   # Quest3 images (20 images)
├── rs_intrinsics.json          # RealSense intrinsics
└── q3_intrinsics.json          # Quest3 intrinsics
```

---

## 📚 Detailed Documentation

For more detailed calibration principles and result analysis, please refer to:

- **Chinese Documentation**: [docs/zh/](docs/zh/)
- **English Documentation**: [docs/en/](docs/en/)

Detailed documentation includes:
- Complete steps and principles of intrinsics calibration
- Mathematical principles of extrinsic rigid body calibration
- Detailed analysis of actual calibration results
- Error evaluation and optimization suggestions

### 📚 Related Resources

- [MIT Vision Book - Imaging Geometry](https://visionbook.mit.edu/imaging_geometry.html)

---

## 🛠️ Core OpenCV Functions

Key OpenCV functions used in this project:

### Chessboard Detection and Corner Localization
- `cv2.findChessboardCorners` - Detect chessboard corners
- `cv2.cornerSubPix` - Sub-pixel corner localization
- `cv2.drawChessboardCorners` - Visualize chessboard corners

### Camera Pose Estimation
- `cv2.solvePnP` - Solve camera pose
- `cv2.Rodrigues` - Convert between rotation vector and rotation matrix
- `cv2.projectPoints` - Project 3D points to 2D image plane

### Image Processing
- `cv2.cvtColor` - Convert image color space
- `cv2.imread` - Read image
- `cv2.imwrite` - Save image
- `cv2.resize` - Resize image

### Optimization Parameters
- `cv2.TERM_CRITERIA_EPS` - Termination criteria for corner localization (precision)
- `cv2.TERM_CRITERIA_MAX_ITER` - Termination criteria for corner localization (maximum iterations)
- `cv2.SOLVEPNP_ITERATIVE` - Iterative method for solvePnP

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

- 🐛 **Bug Reports** - Found an issue? Please open an issue with details
- 💡 **Feature Requests** - Have an idea? We'd love to hear it
- 🔧 **Pull Requests** - Submit PRs for bug fixes or new features
- 📖 **Documentation** - Help improve our docs and translations

Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and development process.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
