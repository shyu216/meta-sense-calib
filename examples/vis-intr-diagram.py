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
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# -------------------------- 2. Set Coordinate System and Parameters --------------------------
# Unity coordinate system: X=right, Y=up, Z=forward

# Camera parameters
camera_center = np.array([0, 0, 0])  # Optical center
focal_length = 1.5  # Focal length

# First image plane (behind camera)
image_plane1_x = camera_center[0] - focal_length  # Image plane position (behind camera, on the opposite side of object)

# Second image plane (in front of camera)
image_plane2_x = camera_center[0] + focal_length  # Image plane position (in front of camera)

image_width = 1.5   # Image plane height (Y direction)
image_height = 1.0  # Image plane width (Z direction)

# -------------------------- 3. Define Object (Cube) --------------------------
# 3D cube vertices (on the right side of camera)
cube_size = 0.5
cube_center = np.array([3, 0, 0])  # Object position (on the right side of camera)
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

# -------------------------- 4. Draw Image Planes --------------------------
# First image plane (behind camera)
plane1_corners = np.array([
    [image_plane1_x, -image_width/2, -image_height/2],
    [image_plane1_x, image_width/2, -image_height/2],
    [image_plane1_x, image_width/2, image_height/2],
    [image_plane1_x, -image_width/2, image_height/2]
])

# Connect four corners to form the first image plane
ax.plot([plane1_corners[0,0], plane1_corners[1,0]], 
        [plane1_corners[0,1], plane1_corners[1,1]], 
        [plane1_corners[0,2], plane1_corners[1,2]], 'b-', alpha=0.5, label='Image Plane')
ax.plot([plane1_corners[1,0], plane1_corners[2,0]], 
        [plane1_corners[1,1], plane1_corners[2,1]], 
        [plane1_corners[1,2], plane1_corners[2,2]], 'b-', alpha=0.5)
ax.plot([plane1_corners[2,0], plane1_corners[3,0]], 
        [plane1_corners[2,1], plane1_corners[3,1]], 
        [plane1_corners[2,2], plane1_corners[3,2]], 'b-', alpha=0.5)
ax.plot([plane1_corners[3,0], plane1_corners[0,0]], 
        [plane1_corners[3,1], plane1_corners[0,1]], 
        [plane1_corners[3,2], plane1_corners[0,2]], 'b-', alpha=0.5)

# Second image plane (in front of camera)
plane2_corners = np.array([
    [image_plane2_x, -image_width/2, -image_height/2],
    [image_plane2_x, image_width/2, -image_height/2],
    [image_plane2_x, image_width/2, image_height/2],
    [image_plane2_x, -image_width/2, image_height/2]
])

# Connect four corners to form the second image plane
ax.plot([plane2_corners[0,0], plane2_corners[1,0]], 
        [plane2_corners[0,1], plane2_corners[1,1]], 
        [plane2_corners[0,2], plane2_corners[1,2]], 'g-', alpha=0.5, label='Image Plane (Inverted)')
ax.plot([plane2_corners[1,0], plane2_corners[2,0]], 
        [plane2_corners[1,1], plane2_corners[2,1]], 
        [plane2_corners[1,2], plane2_corners[2,2]], 'g-', alpha=0.5)
ax.plot([plane2_corners[2,0], plane2_corners[3,0]], 
        [plane2_corners[2,1], plane2_corners[3,1]], 
        [plane2_corners[2,2], plane2_corners[3,2]], 'g-', alpha=0.5)
ax.plot([plane2_corners[3,0], plane2_corners[0,0]], 
        [plane2_corners[3,1], plane2_corners[0,1]], 
        [plane2_corners[3,2], plane2_corners[0,2]], 'g-', alpha=0.5)

# -------------------------- 5. Draw Camera Optical Center --------------------------
ax.scatter(camera_center[0], camera_center[1], camera_center[2], 
           c='r', s=100, marker='o', label='Optical Center (O)')

# -------------------------- 6. Draw Object (Cube) --------------------------
for edge in cube_edges:
    ax.plot(
        [cube_vertices[edge[0], 0], cube_vertices[edge[1], 0]],
        [cube_vertices[edge[0], 1], cube_vertices[edge[1], 1]],
        [cube_vertices[edge[0], 2], cube_vertices[edge[1], 2]],
        'g-', linewidth=2, label='3D Object' if edge == (0, 1) else ""
    )

# -------------------------- 7. Calculate Image Plane Points (Pojection) --------------------------
# Calculate projected points on first image plane (behind camera)
projected_points1 = []
for vertex in cube_vertices:
    # Calculate direction vector from optical center to object vertex
    direction = vertex - camera_center
    # Calculate scaling factor to reach first image plane
    t1 = (image_plane1_x - camera_center[0]) / direction[0] if direction[0] != 0 else 0
    # Calculate projected point (inverted)
    projected_point1 = camera_center + direction * t1
    projected_points1.append(projected_point1)

projected_points1 = np.array(projected_points1)

# Calculate projected points on second image plane (in front of camera)
projected_points2 = []
for vertex in cube_vertices:
    # Calculate direction vector from optical center to object vertex
    direction = vertex - camera_center
    # Calculate scaling factor to reach second image plane
    t2 = (image_plane2_x - camera_center[0]) / direction[0] if direction[0] != 0 else 0
    # Calculate projected point (inverted)
    projected_point2 = camera_center + direction * t2
    projected_points2.append(projected_point2)

projected_points2 = np.array(projected_points2)

# -------------------------- 8. Draw Rays from Object through Optical Center to Image Planes --------------------------
colors = ['r', 'g', 'b', 'y', 'm', 'c', 'k', 'r']
for i, (vertex, projected1, projected2) in enumerate(zip(cube_vertices, projected_points1, projected_points2)):
    # 检查从物体顶点到光学中心的射线是否被遮挡
    # 注意：这里我们只检查从光学中心到物体顶点的射线，因为光线是从物体反射到相机
    if not is_ray_blocked(camera_center, vertex, cube_vertices):
        # Draw ray from object vertex through optical center to first image plane
        ax.plot([vertex[0], camera_center[0], projected1[0]], 
                [vertex[1], camera_center[1], projected1[1]], 
                [vertex[2], camera_center[2], projected1[2]], 
                f'{colors[i % len(colors)]}-', alpha=0.6, label='Ray' if i == 0 else "")
        
        # Draw projected point on first image plane
        ax.scatter(projected1[0], projected1[1], projected1[2], 
                   c=colors[i % len(colors)], s=50, marker='s', label='Projected Point' if i == 0 else "")
        
        # # Draw ray from object vertex through optical center to second image plane (Inverted)
        # ax.plot([vertex[0], camera_center[0], projected2[0]], 
        #         [vertex[1], camera_center[1], projected2[1]], 
        #         [vertex[2], camera_center[2], projected2[2]], 
        #         f'{colors[i % len(colors)]}--', alpha=0.6, label='Ray (Inverted)' if i == 0 else "")
        
        # Draw projected point on second image plane
        ax.scatter(projected2[0], projected2[1], projected2[2], 
                   c=colors[i % len(colors)], s=50, marker='^', label='Projected Point (Inverted)' if i == 0 else "")

# -------------------------- 9. Draw Pojection on Image Planes --------------------------
# Connect projected points to form inverted cube on first image plane
for edge in cube_edges:
    # 检查边的两个顶点是否都能被相机看到
    vertex1 = cube_vertices[edge[0]]
    vertex2 = cube_vertices[edge[1]]
    if not is_ray_blocked(camera_center, vertex1, cube_vertices) and not is_ray_blocked(camera_center, vertex2, cube_vertices):
        ax.plot(
            [projected_points1[edge[0], 0], projected_points1[edge[1], 0]],
            [projected_points1[edge[0], 1], projected_points1[edge[1], 1]],
            [projected_points1[edge[0], 2], projected_points1[edge[1], 2]],
            'm--', linewidth=2, label='Pojection' if edge == (0, 1) else ""
        )


# Connect projected points to form inverted cube on second image plane
for edge in cube_edges:
    # 检查边的两个顶点是否都能被相机看到
    vertex1 = cube_vertices[edge[0]]
    vertex2 = cube_vertices[edge[1]]
    if not is_ray_blocked(camera_center, vertex1, cube_vertices) and not is_ray_blocked(camera_center, vertex2, cube_vertices):
        ax.plot(
            [projected_points2[edge[0], 0], projected_points2[edge[1], 0]],
            [projected_points2[edge[0], 1], projected_points2[edge[1], 1]],
            [projected_points2[edge[0], 2], projected_points2[edge[1], 2]],
            'c--', linewidth=2, label='Pojection (Inverted)' if edge == (0, 1) else ""
        )

# -------------------------- 10. Add Labels and Annotations --------------------------
ax.set_xlabel('Z Axis (Forward)')
ax.set_ylabel('X Axis (Right)')
ax.set_zlabel('Y Axis (Up)')
ax.set_title('Camera Pinhole Model - Intrinsic Calibration Diagram')
ax.legend()

# -------------------------- 11. Set View Angle and Axis Ranges --------------------------
# Set view angle to better see the camera, object, and image plane
ax.view_init(elev=30, azim=-60)
ax.set_xlim([-3, 4])
ax.set_ylim([-1.5, 1.5])
ax.set_zlim([-1.5, 1.5])

# -------------------------- 12. Save and Display Image --------------------------
plt.tight_layout()
# Save the figure to docs directory
plt.savefig('docs/images/intrinsics_calibration_diagram.png', dpi=300, bbox_inches='tight')
plt.show()