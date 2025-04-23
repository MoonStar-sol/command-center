#!/usr/bin/env python3
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
import numpy as np
from PIL import Image
import os

def custom_resize(clip, newsize):
    """Custom resize function to avoid PIL.Image.ANTIALIAS deprecation"""
    w, h = newsize
    
    def resize_frame(frame):
        img = Image.fromarray(frame)
        # Use LANCZOS instead of deprecated ANTIALIAS
        resized_img = img.resize((w, h), Image.LANCZOS)
        return np.array(resized_img)
    
    resized_clip = clip.fl_image(resize_frame)
    return resized_clip

def crop_for_social_media(input_file, output_file=None):
    """
    Crop the video to keep only the right third and format it for social media (9:16 aspect ratio).
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
        
    if output_file is None:
        filename, ext = os.path.splitext(input_file)
        output_file = f"{filename}_social_media{ext}"
    
    # Load the video
    clip = VideoFileClip(input_file)
    
    # Calculate dimensions for right third
    original_width = clip.w
    original_height = clip.h
    crop_width = original_width // 3
    
    # Crop to keep only the right third
    right_third = clip.crop(x1=original_width - crop_width, 
                            y1=0,
                            x2=original_width, 
                            y2=original_height)
    
    # Calculate dimensions to match 9:16 aspect ratio
    target_ratio = 9/16  # For vertical videos (width:height)
    current_ratio = right_third.w / right_third.h
    
    final_clip = None
    
    if current_ratio > target_ratio:  # Too wide
        # Need to crop width
        new_width = int(right_third.h * target_ratio)
        x_center = right_third.w / 2
        final_clip = right_third.crop(x1=x_center - new_width/2,
                                     y1=0,
                                     x2=x_center + new_width/2,
                                     y2=right_third.h)
    elif current_ratio < target_ratio:  # Too tall
        # Add black padding on sides
        new_width = int(right_third.h * target_ratio)
        padding_width = (new_width - right_third.w) / 2
        
        # Create a black background with the target aspect ratio
        bg = ColorClip((new_width, right_third.h), color=(0, 0, 0))
        bg = bg.set_duration(right_third.duration)
        
        # Position the original clip at the center
        positioned_clip = right_third.set_position(("center", "center"))
        
        # Composite the clips
        final_clip = CompositeVideoClip([bg, positioned_clip])
    else:
        # Already correct ratio
        final_clip = right_third
    
    # Resize to recommended dimensions for social media (1080x1920)
    width = 1080
    height = 1920
    final_clip = custom_resize(final_clip, (width, height))
    
    # Write the result
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
    
    print(f"Video formatted for social media saved to: {output_file}")
    print(f"Final dimensions: {width}x{height} (9:16 aspect ratio)")

if __name__ == "__main__":
    input_file = "raw_footage/2025-04-22 13-17-18.mov"
    output_file = "raw_footage/2025-04-22_social_media.mp4"
    crop_for_social_media(input_file, output_file) 