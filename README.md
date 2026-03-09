# MetaSenseCalib

<div align="right">
  <a href="README.md">中文</a> | <a href="README.en.md">English</a>
</div>

<div align="center">
  <img src="docs/images/assembly.png" alt="MetaSenseCalib Assembly" style="max-width: 600px; height: auto;">
  
  <div style="margin-top: 20px;">
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
    <img src="https://img.shields.io/badge/OpenCV-4.x-orange.svg" alt="OpenCV">
  </div>
  
  <p style="margin-top: 20px; font-size: 18px;">
    Quest3 + RealSense 相机标定工具 | 让两个相机的像素能够互相转换
  </p>
</div>

## 📑 目录

- [标定的最终目的](#-标定的最终目的)
- [内参是什么](#-内参是什么)
- [外参是什么](#-外参是什么)
- [快速开始](#-快速开始)
- [示例数据](#-示例数据)
- [详细文档](#-详细文档)
- [贡献](#-贡献)
- [许可证](#-许可证)

## 🎯 标定的最终目的

相机标定的核心目标是**让两个相机的像素能够互相转换**。通过标定，我们可以：

- 将 RealSense 相机的像素坐标转换到 Quest3 相机的像素坐标
- 将 Quest3 相机的像素坐标转换到 RealSense 相机的像素坐标
- 实现两个相机之间的空间对齐，使它们能够"看到"同一个三维世界

## 📷 内参是什么

**内参**描述了相机的内部光学特性，定义了**像素与三维空间的映射关系**：

- **焦距 (focal length)**：控制相机的视角和放大倍数
- **主点 (principal point)**：相机光轴与成像平面的交点
- **畸变系数 (distortion coefficients)**：校正镜头畸变

内参标定的本质是建立像素坐标到空间射线的映射。每个像素对应空间中的一条射线，这条射线从相机光心出发，穿过像素点指向无穷远。

## 🌍 外参是什么

**外参**描述了**两个相机之间的相对位置和姿态**，假设两个相机处于不同的三维参考系中：

- **旋转矩阵 (rotation matrix)**：描述一个相机相对于另一个相机的旋转
- **平移向量 (translation vector)**：描述一个相机相对于另一个相机的位置偏移

外参标定的本质是找到一个刚体变换，将一个相机的三维坐标系转换到另一个相机的三维坐标系。

## 🚀 快速开始

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

##  示例数据

项目包含示例数据集，位于 `data/example/` 目录：

```
data/example/
├── rs_0000.png ~ rs_0019.png   # RealSense D415 图像 (20张)
├── q3_0000.png ~ q3_0019.png   # Quest3 图像 (20张)
├── rs_intrinsics.json          # RealSense 内参
└── q3_intrinsics.json           # Quest3 内参
```

### 运行示例

```bash
# 内参标定可视化
python examples/intr-visual.py

# 外参标定演示
python examples/extr-demo.py
```

## 📹 视频演示

以下视频展示了相机标定后的像素转换效果，实现了RealSense和Quest3相机之间的视图转换：

[视频](https://github.com/user-attachments/assets/6618a9a1-ad41-4f3e-8bfe-1c0d7b768931)

它放在docs\videos\warp_demo.mp4

## 📚 详细文档

更多详细的标定原理和结果分析，请参考：

- **中文文档**：[docs/zh/](docs/zh/)
- **英文文档**：[docs/en/](docs/en/)

详细文档包含：
- 内参标定的完整步骤和原理
- 外参刚体标定的数学原理
- 实际标定结果的详细分析
- 误差评估和优化建议

## 🤝 贡献

欢迎提交 Pull Request！我们非常感谢社区的贡献，无论是功能改进、Bug 修复还是文档完善。

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

<div align="center">
  <p>Made with ❤️ for XR Calibration</p>
</div>
