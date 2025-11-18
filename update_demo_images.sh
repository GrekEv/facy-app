#!/bin/bash
# Скрипт для обновления демо-изображений "До и После"

echo "🔄 Обновление демо-изображений..."

# Проверяем папку images в корне проекта
IMAGES_DIR="./images"
STATIC_IMAGES_DIR="./static/images"

if [ ! -d "$IMAGES_DIR" ]; then
    echo "❌ Папка images не найдена в корне проекта"
    echo "💡 Создайте папку images и загрузите туда новые изображения"
    exit 1
fi

# Ищем изображения "до" и "после"
BEFORE_IMG=$(find "$IMAGES_DIR" -maxdepth 1 -type f \( -iname "*до*.png" -o -iname "*before*.png" -o -iname "1.png" -o -iname "before.png" \) | head -1)
AFTER_IMG=$(find "$IMAGES_DIR" -maxdepth 1 -type f \( -iname "*после*.png" -o -iname "*after*.png" -o -iname "2.png" -o -iname "after.png" \) | head -1)

# Если не найдены по именам, берем первые два PNG файла
if [ -z "$BEFORE_IMG" ] || [ -z "$AFTER_IMG" ]; then
    PNG_FILES=($(find "$IMAGES_DIR" -maxdepth 1 -type f -iname "*.png" | sort))
    if [ ${#PNG_FILES[@]} -ge 2 ]; then
        BEFORE_IMG="${PNG_FILES[0]}"
        AFTER_IMG="${PNG_FILES[1]}"
        echo "📋 Найдены файлы:"
        echo "   До: $(basename "$BEFORE_IMG")"
        echo "   После: $(basename "$AFTER_IMG")"
    fi
fi

if [ -z "$BEFORE_IMG" ] || [ -z "$AFTER_IMG" ]; then
    echo "❌ Не найдены изображения 'до' и 'после' в папке images"
    echo "💡 Загрузите два PNG файла в папку images/"
    exit 1
fi

# Копируем изображения
echo "📋 Копирую изображения..."
cp "$BEFORE_IMG" "$STATIC_IMAGES_DIR/demo-before-1.png"
cp "$AFTER_IMG" "$STATIC_IMAGES_DIR/demo-after-1.png"

echo "✅ Изображения обновлены!"
echo "   До: static/images/demo-before-1.png"
echo "   После: static/images/demo-after-1.png"
echo ""
echo "🔄 Перезапустите сервер для применения изменений"

