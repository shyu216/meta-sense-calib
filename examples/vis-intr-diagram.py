import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# -------------------------- 1. Initialize 3D Canvas --------------------------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# -------------------------- 2. Set Coordinate System and Parameters --------------------------
# Unity coordinate system: X=right, Y=up, Z=forward
# Camera position (left side, facing right)
camera_center = np.array([-3, 0, 0])

# Image plane parameters (in front of camera, facing right)
image_plane_x = 0  # X position of image plane
image_width = 1.5   # Height (Y direction)
image_height = 1.0  # Width (Z direction)

# Pixel points (on the image plane)
pixels = np.array([
    [image_plane_x, 0.3, 0.2],   # Top-right pixel
    [image_plane_x, 0.3, -0.2],  # Top-left pixel
    [image_plane_x, -0.3, 0.2],  # Bottom-right pixel
    [image_plane_x, -0.3, -0.2], # Bottom-left pixel
    [image_plane_x, 0, 0]        # Center pixel
])

# -------------------------- 3. Draw Image Plane --------------------------
# Four corners of the image plane
plane_corners = np.array([
    [image_plane_x, -image_width/2, -image_height/2],
    [image_plane_x, image_width/2, -image_height/2],
    [image_plane_x, image_width/2, image_height/2],
    [image_plane_x, -image_width/2, image_height/2]
])

# Connect four corners to form the image plane
ax.plot([plane_corners[0,0], plane_corners[1,0]], 
        [plane_corners[0,1], plane_corners[1,1]], 
        [plane_corners[0,2], plane_corners[1,2]], 'b-', alpha=0.5)
ax.plot([plane_corners[1,0], plane_corners[2,0]], 
        [plane_corners[1,1], plane_corners[2,1]], 
        [plane_corners[1,2], plane_corners[2,2]], 'b-', alpha=0.5)
ax.plot([plane_corners[2,0], plane_corners[3,0]], 
        [plane_corners[2,1], plane_corners[3,1]], 
        [plane_corners[2,2], plane_corners[3,2]], 'b-', alpha=0.5)
ax.plot([plane_corners[3,0], plane_corners[0,0]], 
        [plane_corners[3,1], plane_corners[0,1]], 
        [plane_corners[3,2], plane_corners[0,2]], 'b-', alpha=0.5)

# -------------------------- 4. Draw Camera Optical Center --------------------------
ax.scatter(camera_center[0], camera_center[1], camera_center[2], 
           c='r', s=100, marker='o', label='Camera Optical Center')

# -------------------------- 5. Draw Pixel Points and Rays --------------------------
colors = ['g', 'y', 'm', 'c', 'b']
for i, pixel in enumerate(pixels):
    # Draw pixel point
    ax.scatter(pixel[0], pixel[1], pixel[2], 
               c=colors[i], s=50, marker='s', label=f'Pixel {i+1}')
    
    # Draw ray from optical center through pixel to scene
    # Extend the ray beyond the pixel towards the right (positive X direction)
    ray_end = camera_center + (pixel - camera_center) * 1.2
    ax.plot([camera_center[0], ray_end[0]], 
            [camera_center[1], ray_end[1]], 
            [camera_center[2], ray_end[2]], 
            f'{colors[i]}-', alpha=0.6)

# -------------------------- 6. Add Labels and Annotations --------------------------
ax.set_xlabel('X Axis (Right)')
ax.set_ylabel('Y Axis (Up)')
ax.set_zlabel('Z Axis (Forward)')
ax.set_title('Camera Intrinsic Calibration Diagram (Unity Coordinates)')
ax.legend()

# -------------------------- 7. Set View Angle and Axis Ranges --------------------------
# Set view angle to better see the camera facing right
ax.view_init(elev=30, azim=-60)
ax.set_xlim([-4, 2])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])

# -------------------------- 8. Save and Display Image --------------------------
plt.tight_layout()
# Save the figure to docs directory
plt.savefig('docs/images/intrinsics_calibration_diagram.png', dpi=300, bbox_inches='tight')
# plt.show()