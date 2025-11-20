#!/usr/bin/env python3
"""
Convert logo.png to logo.ico for Windows icon
"""
from PIL import Image
import os

def create_icon():
    """Convert logo.png to logo.ico"""
    try:
        # Open the PNG file
        img = Image.open("logo.png")
        
        # Create icon sizes (Windows supports multiple sizes in one ico file)
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Resize and store images
        icons = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized)
        
        # Save as ICO file
        img.save("logo.ico", format='ICO', sizes=[(s.width, s.height) for s in icons])
        print(f"[SUCCESS] Created logo.ico with sizes: {[s for s in sizes]}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create icon: {e}")
        return False

if __name__ == "__main__":
    if os.path.exists("logo.png"):
        create_icon()
    else:
        print("[ERROR] logo.png not found!")
