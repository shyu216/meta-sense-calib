# MetaSenseCalib

<div align="right">
  <a href="README.cn.md">中文</a> | <a href="README.md">English</a>
</div>

![MetaSenseCalib Assembly](docs/images/assembly.png)

一个用于标定 Quest3 和 RealSense 相机系统的基础流程，旨在建立异构成像设备之间精确的像素到像素坐标转换。该实现提供了多相机标定的基础方法，应该能帮助初学者理解相机坐标系对齐的核心原理。

欢迎提出您的意见和建议！随时分享您对如何改进这个标定流程的想法。

---

## 🎬 效果演示

观看 MetaSenseCalib 如何实现 RealSense 和 Quest3 相机之间的像素级转换：

<div align="center">
  <img src="docs/videos/warp_demo.gif" alt="Warp Demo" style="max-width: 700px; width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
  <p><i>RealSense D415 与 Quest3 相机之间的实时视图转换</i></p>
</div>

📹 <a href="docs/videos/warp_demo.mp4">下载完整视频 (MP4)</a>

---

## ✨ 核心特性

- 🎯 **像素级对齐** - 亚像素精度的相机坐标转换
- 🔧 **完整标定流程** - 内参 + 外参一体化标定工具
- 📊 **丰富可视化** - 交互式图表和详细误差分析
- 🚀 **简单易用** - 简洁的 API 和命令行界面
- 📁 **包含示例数据** - 20对图像的即用型示例
- 🎮 **XR 优化** - 专为 Quest3 和 RealSense D415 优化

---

## 📑 目录

- [快速开始](#-快速开始)
- [什么是相机标定](#-什么是相机标定)
- [安装说明](#-安装说明)
- [示例数据](#-示例数据)
- [详细文档](#-详细文档)
- [核心 OpenCV 函数](#-核心-opencv-函数)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/shyu216/meta-sense-calib.git
cd meta-sense-calib

# 安装依赖
pip install -r requirements.txt
```

### 基本用法

```python
from calibration import Calibrator

# 创建标定器
calibrator = Calibrator(
    intrinsics_rs="data/example/rs_intrinsics.json",
    intrinsics_q3="data/example/q3_intrinsics.json"
)

# 运行标定
result = calibrator.calibrate(
    image_folder="data/example",
    output_dir="outputs/example/extrinsics"
)

# 查看结果
print(f"变换矩阵:\n{result.transformation_matrix}")
print(f"旋转矩阵:\n{result.rotation_matrix}")
print(f"平移向量: {result.translation_vector}")
print(f"旋转角度 (度): X={result.euler_angles[0]:.2f}, Y={result.euler_angles[1]:.2f}, Z={result.euler_angles[2]:.2f}")
print(f"平均误差: {result.mean_error:.3f} mm")
```

### 运行示例

```bash
# 内参标定可视化
python examples/intr-visual.py

# 外参标定演示
python examples/extr-demo.py
```

---

## 📖 什么是相机标定

### 🎯 标定的最终目的

相机标定的核心目标是**让两个相机的像素能够互相转换**。通过标定，我们可以：

- 将 RealSense 相机的像素坐标转换到 Quest3 相机的像素坐标
- 将 Quest3 相机的像素坐标转换到 RealSense 相机的像素坐标
- 实现两个相机之间的空间对齐，使它们能够"看到"同一个三维世界

### 📷 内参

**内参**描述了相机的内部光学特性，定义了**像素与三维空间的映射关系**：

- **焦距 (focal length)**：控制相机的视角和放大倍数
- **主点 (principal point)**：相机光轴与成像平面的交点
- **畸变系数 (distortion coefficients)**：校正镜头畸变

内参标定的本质是建立像素坐标到空间射线的映射。每个像素对应空间中的一条射线，这条射线从相机光心出发，穿过像素点指向无穷远。

### 🌍 外参

**外参**描述了**两个相机之间的相对位置和姿态**，假设两个相机处于不同的三维参考系中：

- **旋转矩阵 (rotation matrix)**：描述一个相机相对于另一个相机的旋转
- **平移向量 (translation vector)**：描述一个相机相对于另一个相机的位置偏移

外参标定的本质是找到一个刚体变换，将一个相机的三维坐标系转换到另一个相机的三维坐标系。

---

## 📦 示例数据

项目包含示例数据集，位于 `data/example/` 目录：

```
data/example/
├── rs_0000.png ~ rs_0019.png   # RealSense D415 图像 (20张)
├── q3_0000.png ~ q3_0019.png   # Quest3 图像 (20张)
├── rs_intrinsics.json          # RealSense 内参
└── q3_intrinsics.json          # Quest3 内参
```

---

## 📚 详细文档

更多详细的标定原理和结果分析，请参考：

- **中文文档**：[docs/zh/](docs/zh/)
- **英文文档**：[docs/en/](docs/en/)

详细文档包含：
- 内参标定的完整步骤和原理
- 外参刚体标定的数学原理
- 实际标定结果的详细分析
- 误差评估和优化建议

### 📚 相关资源

- [MIT Vision Book - Imaging Geometry](https://visionbook.mit.edu/imaging_geometry.html)

---

## 🛠️ 核心 OpenCV 函数

本项目使用的关键 OpenCV 函数：

### 棋盘格检测与角点定位
- `cv2.findChessboardCorners` - 检测棋盘格角点
- `cv2.cornerSubPix` - 亚像素级角点精确定位
- `cv2.drawChessboardCorners` - 可视化棋盘格角点

### 相机位姿估计
- `cv2.solvePnP` - 求解相机位姿
- `cv2.Rodrigues` - 旋转向量和旋转矩阵之间的转换
- `cv2.projectPoints` - 将3D点投影到2D图像平面

### 图像处理
- `cv2.cvtColor` - 图像颜色空间转换
- `cv2.imread` - 读取图像
- `cv2.imwrite` - 保存图像
- `cv2.resize` - 调整图像大小

### 优化参数
- `cv2.TERM_CRITERIA_EPS` - 角点精确定位的终止条件（精度）
- `cv2.TERM_CRITERIA_MAX_ITER` - 角点精确定位的终止条件（最大迭代次数）
- `cv2.SOLVEPNP_ITERATIVE` - solvePnP的迭代求解方法

---

## 🤝 贡献指南

我们欢迎社区贡献！您可以通过以下方式参与：

- 🐛 **Bug 报告** - 发现问题？请提交 issue 并描述详情
- 💡 **功能建议** - 有好想法？我们期待您的建议
- 🔧 **Pull Request** - 提交代码修复或新功能
- 📖 **文档改进** - 帮助完善文档和翻译

请阅读我们的[贡献指南](CONTRIBUTING.md)了解代码规范和开发流程。

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---
