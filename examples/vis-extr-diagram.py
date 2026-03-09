import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# -------------------------- Helper Functions --------------------------
def ray_aabb_intersection(ray_origin, ray_direction, min_bound, max_bound):
    """
    检测射线与轴对齐包围盒(AABB)的交点
    
    参数:
        ray_origin: 射线起点
        ray_direction: 射线方向向量
        min_bound: AABB的最小边界点
        max_bound: AABB的最大边界点
    
    返回:
        (intersects, t_min, t_max): 是否相交，以及交点参数
    """
    # 计算射线与每个轴平面的交点参数
    t_x_min = (min_bound[0] - ray_origin[0]) / ray_direction[0] if ray_direction[0] != 0 else -np.inf
    t_x_max = (max_bound[0] - ray_origin[0]) / ray_direction[0] if ray_direction[0] != 0 else np.inf
    
    t_y_min = (min_bound[1] - ray_origin[1]) / ray_direction[1] if ray_direction[1] != 0 else -np.inf
    t_y_max = (max_bound[1] - ray_origin[1]) / ray_direction[1] if ray_direction[1] != 0 else np.inf
    
    t_z_min = (min_bound[2] - ray_origin[2]) / ray_direction[2] if ray_direction[2] != 0 else -np.inf
    t_z_max = (max_bound[2] - ray_origin[2]) / ray_direction[2] if ray_direction[2] != 0 else np.inf
    
    # 确保t_min < t_max
    if t_x_min > t_x_max:
        t_x_min, t_x_max = t_x_max, t_x_min
    if t_y_min > t_y_max:
        t_y_min, t_y_max = t_y_max, t_y_min
    if t_z_min > t_z_max:
        t_z_min, t_z_max = t_z_max, t_z_min
    
    # 计算全局的t_min和t_max
    t_min = max(t_x_min, t_y_min, t_z_min)
    t_max = min(t_x_max, t_y_max, t_z_max)
    
    # 检查是否相交
    if t_min <= t_max and t_max >= 0:
        return True, t_min, t_max
    else:
        return False, 0, 0

def is_ray_blocked(ray_origin, ray_target, object_vertices):
    """
    检查射线是否被物体遮挡
    
    参数:
        ray_origin: 射线起点
        ray_target: 射线目标点
        object_vertices: 物体的顶点
    
    返回:
        bool: 射线是否被遮挡
    """
    # 计算射线方向
    ray_direction = ray_target - ray_origin
    ray_length = np.linalg.norm(ray_direction)
    if ray_length == 0:
        return False
    ray_direction = ray_direction / ray_length
    
    # 计算物体的AABB
    min_bound = np.min(object_vertices, axis=0)
    max_bound = np.max(object_vertices, axis=0)
    
    # 检查射线是否与物体相交
    intersects, t_min, t_max = ray_aabb_intersection(ray_origin, ray_direction, min_bound, max_bound)
    
    if intersects:
        # 检查交点是否在射线的有效范围内
        intersection_point = ray_origin + ray_direction * t_min
        distance_to_intersection = np.linalg.norm(intersection_point - ray_origin)
        distance_to_target = np.linalg.norm(ray_target - ray_origin)
        
        # 如果交点在起点和目标点之间，则射线被遮挡
        if distance_to_intersection < distance_to_target - 1e-6:  # 减去一个小的epsilon以避免浮点误差
            return True
    
    return False

# -------------------------- 1. Initialize 3D Canvas --------------------------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# -------------------------- 2. Define Object (Cube) --------------------------
# 3D cube vertices
cube_size = 0.5
cube_center = np.array([0, 0, 0])
cube_vertices = np.array([
    cube_center + np.array([-cube_size/2, -cube_size/2, -cube_size/2]),
    cube_center + np.array([cube_size/2, -cube_size/2, -cube_size/2]),
    cube_center + np.array([cube_size/2, cube_size/2, -cube_size/2]),
    cube_center + np.array([-cube_size/2, cube_size/2, -cube_size/2]),
    cube_center + np.array([-cube_size/2, -cube_size/2, cube_size/2]),
    cube_center + np.array([cube_size/2, -cube_size/2, cube_size/2]),
    cube_center + np.array([cube_size/2, cube_size/2, cube_size/2]),
    cube_center + np.array([-cube_size/2, cube_size/2, cube_size/2])
])

# Cube edges
cube_edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # Front face
    (4, 5), (5, 6), (6, 7), (7, 4),  # Back face
    (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
]

# -------------------------- 3. Define Cameras --------------------------
# Camera 1: Reference camera (left side, facing right)
camera1_position = np.array([-4, -1, 0])
camera1_x = np.array([1, 0, 0])    # Right (forward direction)
camera1_y = np.array([0, 1, 0])    # Up
camera1_z = np.array([0, 0, 1])    # Forward (out of screen)

# Camera 2: Second camera (different position and orientation)
camera2_position = np.array([-4, 1, 0])
camera2_x = np.array([1, 0, 0])   # Left (forward direction)
camera2_y = np.array([0, 1, 0])    # Up
camera2_z = np.array([0, 0, 1])   # Backward (into screen)

# -------------------------- 4. Draw Object (Cube) --------------------------
for edge in cube_edges:
    ax.plot(
        [cube_vertices[edge[0], 0], cube_vertices[edge[1], 0]],
        [cube_vertices[edge[0], 1], cube_vertices[edge[1], 1]],
        [cube_vertices[edge[0], 2], cube_vertices[edge[1], 2]],
        'b-', linewidth=2, label='Object' if edge == (0, 1) else ""
    )

# -------------------------- 5. Draw Camera 1 --------------------------
# Camera 1 optical center
ax.scatter(camera1_position[0], camera1_position[1], camera1_position[2], 
           c='r', s=100, marker='o', label='Camera 1 (Reference)')

# Camera 1 coordinate system
ax.plot([camera1_position[0], camera1_position[0] + camera1_x[0]], 
        [camera1_position[1], camera1_position[1] + camera1_x[1]], 
        [camera1_position[2], camera1_position[2] + camera1_x[2]], 'c-', linewidth=2, label='Camera 1 X')
ax.plot([camera1_position[0], camera1_position[0] + camera1_y[0]], 
        [camera1_position[1], camera1_position[1] + camera1_y[1]], 
        [camera1_position[2], camera1_position[2] + camera1_y[2]], 'm-', linewidth=2, label='Camera 1 Y')
ax.plot([camera1_position[0], camera1_position[0] + camera1_z[0]], 
        [camera1_position[1], camera1_position[1] + camera1_z[1]], 
        [camera1_position[2], camera1_position[2] + camera1_z[2]], 'y-', linewidth=2, label='Camera 1 Z')

# Camera 1 frustum
frustum_size = 0.3
frustum_depth = 1.0
frustum1_points = np.array([
    camera1_position,
    camera1_position + camera1_x * frustum_depth + camera1_y * frustum_size + camera1_z * frustum_size,
    camera1_position + camera1_x * frustum_depth + camera1_y * frustum_size - camera1_z * frustum_size,
    camera1_position + camera1_x * frustum_depth - camera1_y * frustum_size - camera1_z * frustum_size,
    camera1_position + camera1_x * frustum_depth - camera1_y * frustum_size + camera1_z * frustum_size
])

# Connect frustum 1 points
for i in range(1, 5):
    ax.plot([frustum1_points[0,0], frustum1_points[i,0]], 
            [frustum1_points[0,1], frustum1_points[i,1]], 
            [frustum1_points[0,2], frustum1_points[i,2]], 'k-', alpha=0.5)

# Connect frustum 1 base
ax.plot([frustum1_points[1,0], frustum1_points[2,0]], 
        [frustum1_points[1,1], frustum1_points[2,1]], 
        [frustum1_points[1,2], frustum1_points[2,2]], 'k-', alpha=0.5)
ax.plot([frustum1_points[2,0], frustum1_points[3,0]], 
        [frustum1_points[2,1], frustum1_points[3,1]], 
        [frustum1_points[2,2], frustum1_points[3,2]], 'k-', alpha=0.5)
ax.plot([frustum1_points[3,0], frustum1_points[4,0]], 
        [frustum1_points[3,1], frustum1_points[4,1]], 
        [frustum1_points[3,2], frustum1_points[4,2]], 'k-', alpha=0.5)
ax.plot([frustum1_points[4,0], frustum1_points[1,0]], 
        [frustum1_points[4,1], frustum1_points[1,1]], 
        [frustum1_points[4,2], frustum1_points[1,2]], 'k-', alpha=0.5)

# -------------------------- 6. Draw Camera 2 --------------------------
# Camera 2 optical center
ax.scatter(camera2_position[0], camera2_position[1], camera2_position[2], 
           c='g', s=100, marker='o', label='Camera 2 (Simulated)')

# Camera 2 coordinate system
ax.plot([camera2_position[0], camera2_position[0] + camera2_x[0]], 
        [camera2_position[1], camera2_position[1] + camera2_x[1]], 
        [camera2_position[2], camera2_position[2] + camera2_x[2]], 'c--', linewidth=2, label='Camera 2 X')
ax.plot([camera2_position[0], camera2_position[0] + camera2_y[0]], 
        [camera2_position[1], camera2_position[1] + camera2_y[1]], 
        [camera2_position[2], camera2_position[2] + camera2_y[2]], 'm--', linewidth=2, label='Camera 2 Y')
ax.plot([camera2_position[0], camera2_position[0] + camera2_z[0]], 
        [camera2_position[1], camera2_position[1] + camera2_z[1]], 
        [camera2_position[2], camera2_position[2] + camera2_z[2]], 'y--', linewidth=2, label='Camera 2 Z')

# Camera 2 frustum
frustum2_points = np.array([
    camera2_position,
    camera2_position + camera2_x * frustum_depth + camera2_y * frustum_size + camera2_z * frustum_size,
    camera2_position + camera2_x * frustum_depth + camera2_y * frustum_size - camera2_z * frustum_size,
    camera2_position + camera2_x * frustum_depth - camera2_y * frustum_size - camera2_z * frustum_size,
    camera2_position + camera2_x * frustum_depth - camera2_y * frustum_size + camera2_z * frustum_size
])

# Connect frustum 2 points
for i in range(1, 5):
    ax.plot([frustum2_points[0,0], frustum2_points[i,0]], 
            [frustum2_points[0,1], frustum2_points[i,1]], 
            [frustum2_points[0,2], frustum2_points[i,2]], 'k--', alpha=0.5)

# Connect frustum 2 base
ax.plot([frustum2_points[1,0], frustum2_points[2,0]], 
        [frustum2_points[1,1], frustum2_points[2,1]], 
        [frustum2_points[1,2], frustum2_points[2,2]], 'k--', alpha=0.5)
ax.plot([frustum2_points[2,0], frustum2_points[3,0]], 
        [frustum2_points[2,1], frustum2_points[3,1]], 
        [frustum2_points[2,2], frustum2_points[3,2]], 'k--', alpha=0.5)
ax.plot([frustum2_points[3,0], frustum2_points[4,0]], 
        [frustum2_points[3,1], frustum2_points[4,1]], 
        [frustum2_points[3,2], frustum2_points[4,2]], 'k--', alpha=0.5)
ax.plot([frustum2_points[4,0], frustum2_points[1,0]], 
        [frustum2_points[4,1], frustum2_points[1,1]], 
        [frustum2_points[4,2], frustum2_points[1,2]], 'k--', alpha=0.5)

# -------------------------- 7. Draw View Transformation --------------------------
# Draw rays from both cameras to the object
for vertex in cube_vertices:
    # Ray from camera 1 to object
    if not is_ray_blocked(camera1_position, vertex, cube_vertices):
        ax.plot([camera1_position[0], vertex[0]], 
                [camera1_position[1], vertex[1]], 
                [camera1_position[2], vertex[2]], 'r-', alpha=0.3)
    # Ray from camera 2 to object
    if not is_ray_blocked(camera2_position, vertex, cube_vertices):
        ax.plot([camera2_position[0], vertex[0]], 
                [camera2_position[1], vertex[1]], 
                [camera2_position[2], vertex[2]], 'g-', alpha=0.3)

# -------------------------- 8. Add Labels and Annotations --------------------------
ax.set_xlabel('Z Axis (Forward)')
ax.set_ylabel('X Axis (Right)')
ax.set_zlabel('Y Axis (Up)')
ax.set_title('Camera View Transformation Diagram')
ax.legend()

# -------------------------- 9. Set View Angle and Axis Ranges --------------------------
# Set view angle to better show both cameras and the object
ax.view_init(elev=30, azim=45)
ax.set_xlim([-3, 2])
ax.set_ylim([-1, 2])
ax.set_zlim([-1, 2])

# -------------------------- 10. Save and Display Image --------------------------
plt.tight_layout()
# Save the figure to docs directory
plt.savefig('docs/images/camera_view_transformation.png', dpi=300, bbox_inches='tight')
plt.show()