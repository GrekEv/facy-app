#!/usr/bin/env python3
"""
Скрипт для обрезки белых полей с изображения и сохранения в demo-before-1.png
"""
from PIL import Image
import sys
import os

def remove_white_borders(image_path, output_path):
    """Обрезает белые поля с изображения"""
    img = Image.open(image_path)
    
    # Конвертируем в RGB если нужно
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Получаем данные изображения
    img_data = img.load()
    width, height = img.size
    
    # Находим границы контента (не белого)
    # Белый цвет: RGB близко к (255, 255, 255)
    threshold = 240  # Порог для определения "белого"
    
    left = width
    right = 0
    top = height
    bottom = 0
    
    for y in range(height):
        for x in range(width):
            r, g, b = img_data[x, y]
            # Если пиксель не белый
            if r < threshold or g < threshold or b < threshold:
                left = min(left, x)
                right = max(right, x)
                top = min(top, y)
                bottom = max(bottom, y)
    
    # Добавляем небольшой отступ (5% с каждой стороны)
    padding = int(min(width, height) * 0.05)
    left = max(0, left - padding)
    right = min(width - 1, right + padding)
    top = max(0, top - padding)
    bottom = min(height - 1, bottom + padding)
    
    # Обрезаем изображение
    cropped = img.crop((left, top, right + 1, bottom + 1))
    
    # Сохраняем
    cropped.save(output_path, 'PNG', optimize=True)
    print(f"✅ Изображение обрезано и сохранено: {output_path}")
    print(f"   Исходный размер: {width}x{height}")
    print(f"   Новый размер: {cropped.size[0]}x{cropped.size[1]}")
    print(f"   Обрезано: {width - cropped.size[0]}px по ширине, {height - cropped.size[1]}px по высоте")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 process_demo_image.py <путь_к_изображению> [before|after]")
        print("Пример: python3 process_demo_image.py ~/Downloads/image.png after")
        sys.exit(1)
    
    input_path = sys.argv[1]
    position = sys.argv[2] if len(sys.argv) > 2 else "before"
    output_path = f"static/images/demo-{position}-1.png"
    
    if not os.path.exists(input_path):
        print(f"❌ Файл не найден: {input_path}")
        sys.exit(1)
    
    # Создаем директорию если нужно
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    remove_white_borders(input_path, output_path)

