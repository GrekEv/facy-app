#!/usr/bin/env python3
"""
�к��пт дл� о��езк� �ел�� полей � �зо��ажен�� � �о��анен�� в demo-before-1.png
"""
from PIL import Image
import sys
import os

def remove_white_borders(image_path, output_path):
    """О��езает �ел�е пол� � �зо��ажен��"""
    img = Image.open(image_path)
    
    # �онве�т��уем в RGB е�л� нужно
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # �олучаем данн�е �зо��ажен��
    img_data = img.load()
    width, height = img.size
    
    # �а�од�м ��ан�ц� контента (не �ело�о)
    # Бел�й цвет: RGB �л�зко к (255, 255, 255)
    threshold = 240  # �о�о� дл� оп�еделен�� "�ело�о"
    
    left = width
    right = 0
    top = height
    bottom = 0
    
    for y in range(height):
        for x in range(width):
            r, g, b = img_data[x, y]
            # Е�л� п�к�ел� не �ел�й
            if r < threshold or g < threshold or b < threshold:
                left = min(left, x)
                right = max(right, x)
                top = min(top, y)
                bottom = max(bottom, y)
    
    # �о�авл�ем не�ол�шой от�туп (5% � каждой �то�он�)
    padding = int(min(width, height) * 0.05)
    left = max(0, left - padding)
    right = min(width - 1, right + padding)
    top = max(0, top - padding)
    bottom = min(height - 1, bottom + padding)
    
    # О��езаем �зо��ажен�е
    cropped = img.crop((left, top, right + 1, bottom + 1))
    
    cropped.save(output_path, 'PNG', optimize=True)
    print(f"Изо��ажен�е о��езано � �о��анено: {output_path}")
    print(f"   И��одн�й �азме�: {width}x{height}")
    print(f"   �ов�й �азме�: {cropped.size[0]}x{cropped.size[1]}")
    print(f"   О��езано: {width - cropped.size[0]}px по ш���не, {height - cropped.size[1]}px по в��оте")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("И�пол�зован�е: python3 process_demo_image.py <пут�_к_�зо��ажен��> [before|after]")
        print("���ме�: python3 process_demo_image.py ~/Downloads/image.png after")
        sys.exit(1)
    
    input_path = sys.argv[1]
    position = sys.argv[2] if len(sys.argv) > 2 else "before"
    output_path = f"static/images/demo-{position}-1.png"
    
    if not os.path.exists(input_path):
        print(f"Ош��ка: Файл не найден: {input_path}")
        sys.exit(1)
    
    # �оздаем д��екто��� е�л� нужно
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    remove_white_borders(input_path, output_path)

