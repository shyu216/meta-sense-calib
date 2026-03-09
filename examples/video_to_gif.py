import cv2
import numpy as np
import os
from PIL import Image
import argparse

def video_to_gif(video_path, output_path, max_size=1024*1024, fps=10, width=320, duration=20):
    """
    Convert a video to a GIF with size control
    
    Args:
        video_path (str): Path to input video
        output_path (str): Path to output GIF
        max_size (int): Maximum size of GIF in bytes (default: 1MB)
        fps (int): Frames per second for GIF
        width (int): Width of output GIF
        duration (int): Duration of video to process in seconds (default: 20)
    """
    # Open video capture
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return False
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate frame skip to achieve desired FPS
    frame_skip = max(1, int(original_fps / fps))
    
    # Calculate maximum frames to process based on duration
    max_frames = int(duration * original_fps)
    
    # Read frames
    frames = []
    frame_count = 0
    
    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Skip frames to control FPS
        if frame_count % frame_skip == 0:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame
            h, w = frame_rgb.shape[:2]
            height = int(width * h / w)
            frame_resized = cv2.resize(frame_rgb, (width, height), interpolation=cv2.INTER_AREA)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame_resized)
            frames.append(pil_image)
        
        frame_count += 1
    
    print(f"Processed {len(frames)} frames from {frame_count} total frames")
    
    # If still too many frames, further reduce
    max_gif_frames = 100  # Maximum frames for GIF
    if len(frames) > max_gif_frames:
        frame_step = max(1, len(frames) // max_gif_frames)
        frames = frames[::frame_step]
        print(f"Reduced frames to {len(frames)} for GIF compatibility")
    
    cap.release()
    
    if not frames:
        print("Error: No frames read from video")
        return False
    
    # Save as GIF with size control
    current_width = width
    
    while current_width >= 160:  # Minimum width threshold
        # Resize frames if width changed
        if current_width != width:
            resized_frames = []
            for frame in frames:
                w, h = frame.size
                new_height = int(current_width * h / w)
                resized_frame = frame.resize((current_width, new_height), Image.LANCZOS)
                resized_frames.append(resized_frame)
            save_frames = resized_frames
        else:
            save_frames = frames
        
        # Save GIF
        save_frames[0].save(
            output_path,
            format='GIF',
            append_images=save_frames[1:],
            save_all=True,
            duration=int(1000/fps),
            loop=0,
            optimize=True
        )
        
        # Check file size
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size <= max_size:
                print(f"GIF saved successfully! Size: {file_size/1024:.2f} KB, Width: {current_width}")
                return True
            else:
                print(f"GIF too large ({file_size/1024:.2f} KB), reducing width from {current_width} to {int(current_width * 0.5)}")
                current_width = int(current_width * 0.5)
        else:
            print("Error: Failed to save GIF")
            return False
    
    print("Could not reduce size enough even with minimum width")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert video to GIF with size control")
    parser.add_argument("input", help="Input video path")
    parser.add_argument("output", help="Output GIF path")
    parser.add_argument("--max-size", type=int, default=1024*1024, help="Maximum GIF size in bytes")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second for GIF")
    parser.add_argument("--width", type=int, default=320, help="Width of output GIF")
    parser.add_argument("--duration", type=int, default=20, help="Duration of video to process in seconds")
    
    args = parser.parse_args()
    
    success = video_to_gif(args.input, args.output, args.max_size, args.fps, args.width, args.duration)
    if success:
        print(f"Successfully converted {args.input} to {args.output}")
    else:
        print("Conversion failed")
