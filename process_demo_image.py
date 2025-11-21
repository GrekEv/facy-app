#!/usr/bin/env python3
"""
ÐÐºÑÐÐ¿Ñ Ð´Ð»Ñ Ð¾ÐÑÐµÐ·ÐºÐ ÐÐµÐ»ÑÑ Ð¿Ð¾Ð»ÐµÐ¹ Ñ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ Ð ÑÐ¾ÑÑÐ°Ð½ÐµÐ½ÐÑ Ð² demo-before-1.png
"""
from PIL import Image
import sys
import os

def remove_white_borders(image_path, output_path):
    """ÐÐÑÐµÐ·Ð°ÐµÑ ÐÐµÐ»ÑÐµ Ð¿Ð¾Ð»Ñ Ñ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ"""
    img = Image.open(image_path)
    
    # ÐÐ¾Ð½Ð²ÐµÑÑÐÑÑÐµÐ¼ Ð² RGB ÐµÑÐ»Ð Ð½ÑÐ¶Ð½Ð¾
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # ÐÐ¾Ð»ÑÑÐ°ÐµÐ¼ Ð´Ð°Ð½Ð½ÑÐµ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ
    img_data = img.load()
    width, height = img.size
    
    # ÐÐ°ÑÐ¾Ð´ÐÐ¼ ÐÑÐ°Ð½ÐÑÑ ÐºÐ¾Ð½ÑÐµÐ½ÑÐ° (Ð½Ðµ ÐÐµÐ»Ð¾ÐÐ¾)
    # ÐÐµÐ»ÑÐ¹ ÑÐ²ÐµÑ: RGB ÐÐ»ÐÐ·ÐºÐ¾ Ðº (255, 255, 255)
    threshold = 240  # ÐÐ¾ÑÐ¾Ð Ð´Ð»Ñ Ð¾Ð¿ÑÐµÐ´ÐµÐ»ÐµÐ½ÐÑ "ÐÐµÐ»Ð¾ÐÐ¾"
    
    left = width
    right = 0
    top = height
    bottom = 0
    
    for y in range(height):
        for x in range(width):
            r, g, b = img_data[x, y]
            # ÐÑÐ»Ð Ð¿ÐÐºÑÐµÐ»Ñ Ð½Ðµ ÐÐµÐ»ÑÐ¹
            if r < threshold or g < threshold or b < threshold:
                left = min(left, x)
                right = max(right, x)
                top = min(top, y)
                bottom = max(bottom, y)
    
    # ÐÐ¾ÐÐ°Ð²Ð»ÑÐµÐ¼ Ð½ÐµÐÐ¾Ð»ÑÑÐ¾Ð¹ Ð¾ÑÑÑÑÐ¿ (5% Ñ ÐºÐ°Ð¶Ð´Ð¾Ð¹ ÑÑÐ¾ÑÐ¾Ð½Ñ)
    padding = int(min(width, height) * 0.05)
    left = max(0, left - padding)
    right = min(width - 1, right + padding)
    top = max(0, top - padding)
    bottom = min(height - 1, bottom + padding)
    
    # ÐÐÑÐµÐ·Ð°ÐµÐ¼ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐµ
    cropped = img.crop((left, top, right + 1, bottom + 1))
    
    cropped.save(output_path, 'PNG', optimize=True)
    print(f"ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐµ Ð¾ÐÑÐµÐ·Ð°Ð½Ð¾ Ð ÑÐ¾ÑÑÐ°Ð½ÐµÐ½Ð¾: {output_path}")
    print(f"   ÐÑÑÐ¾Ð´Ð½ÑÐ¹ ÑÐ°Ð·Ð¼ÐµÑ: {width}x{height}")
    print(f"   ÐÐ¾Ð²ÑÐ¹ ÑÐ°Ð·Ð¼ÐµÑ: {cropped.size[0]}x{cropped.size[1]}")
    print(f"   ÐÐÑÐµÐ·Ð°Ð½Ð¾: {width - cropped.size[0]}px Ð¿Ð¾ ÑÐÑÐÐ½Ðµ, {height - cropped.size[1]}px Ð¿Ð¾ Ð²ÑÑÐ¾ÑÐµ")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ÐÑÐ¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°Ð½ÐÐµ: python3 process_demo_image.py <Ð¿ÑÑÑ_Ðº_ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ> [before|after]")
        print("ÐÑÐÐ¼ÐµÑ: python3 process_demo_image.py ~/Downloads/image.png after")
        sys.exit(1)
    
    input_path = sys.argv[1]
    position = sys.argv[2] if len(sys.argv) > 2 else "before"
    output_path = f"static/images/demo-{position}-1.png"
    
    if not os.path.exists(input_path):
        print(f"ÐÑÐÐÐºÐ°: Ð¤Ð°Ð¹Ð» Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½: {input_path}")
        sys.exit(1)
    
    # ÐÐ¾Ð·Ð´Ð°ÐµÐ¼ Ð´ÐÑÐµÐºÑÐ¾ÑÐÑ ÐµÑÐ»Ð Ð½ÑÐ¶Ð½Ð¾
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    remove_white_borders(input_path, output_path)

