#!/bin/bash
# �к��пт дл� о�новлен�� демо-�зо��ажен�й "�о � �о�ле"

echo "� О�новлен�е демо-�зо��ажен�й..."

# ��ове��ем папку images в ко�не п�оекта
IMAGES_DIR="./images"
STATIC_IMAGES_DIR="./static/images"

if [ ! -d "$IMAGES_DIR" ]; then
    echo " �апка images не найдена в ко�не п�оекта"
    echo " �оздайте папку images � за��уз�те туда нов�е �зо��ажен��"
    exit 1
fi

# И�ем �зо��ажен�� "до" � "по�ле"
BEFORE_IMG=$(find "$IMAGES_DIR" -maxdepth 1 -type f \( -iname "*до*.png" -o -iname "*before*.png" -o -iname "1.png" -o -iname "before.png" \) | head -1)
AFTER_IMG=$(find "$IMAGES_DIR" -maxdepth 1 -type f \( -iname "*по�ле*.png" -o -iname "*after*.png" -o -iname "2.png" -o -iname "after.png" \) | head -1)

# Е�л� не найден� по �менам, �е�ем пе�в�е два PNG файла
if [ -z "$BEFORE_IMG" ] || [ -z "$AFTER_IMG" ]; then
    PNG_FILES=($(find "$IMAGES_DIR" -maxdepth 1 -type f -iname "*.png" | sort))
    if [ ${#PNG_FILES[@]} -ge 2 ]; then
        BEFORE_IMG="${PNG_FILES[0]}"
        AFTER_IMG="${PNG_FILES[1]}"
        echo " �айден� файл�:"
        echo "   �о: $(basename "$BEFORE_IMG")"
        echo "   �о�ле: $(basename "$AFTER_IMG")"
    fi
fi

if [ -z "$BEFORE_IMG" ] || [ -z "$AFTER_IMG" ]; then
    echo " �е найден� �зо��ажен�� 'до' � 'по�ле' в папке images"
    echo " За��уз�те два PNG файла в папку images/"
    exit 1
fi

# �оп��уем �зо��ажен��
echo " �оп��у� �зо��ажен��..."
cp "$BEFORE_IMG" "$STATIC_IMAGES_DIR/demo-before-1.png"
cp "$AFTER_IMG" "$STATIC_IMAGES_DIR/demo-after-1.png"

echo " Изо��ажен�� о�новлен�!"
echo "   �о: static/images/demo-before-1.png"
echo "   �о�ле: static/images/demo-after-1.png"
echo ""
echo "� �е�езапу�т�те �е�ве� дл� п��менен�� �зменен�й"

