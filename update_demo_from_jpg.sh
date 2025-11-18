#!/bin/bash
# Скрипт для обновления изображений "До" и "После" из 1.jpg и 2.jpg

echo "Обновление изображений 'До' и 'После'..."

# Ищем файлы в разных местах
find_file() {
    local filename=$1
    # Проверяем в разных местах
    if [ -f "images/$filename" ]; then
        echo "images/$filename"
    elif [ -f "$filename" ]; then
        echo "$filename"
    elif [ -f "$HOME/Downloads/$filename" ]; then
        echo "$HOME/Downloads/$filename"
    elif [ -f "$HOME/Desktop/$filename" ]; then
        echo "$HOME/Desktop/$filename"
    else
        # Ищем файл в проекте
        local found=$(find . -maxdepth 3 -name "$filename" -type f 2>/dev/null | head -1)
        if [ -n "$found" ]; then
            echo "$found"
        else
            echo ""
        fi
    fi
}

# Ищем файлы
SOURCE_1=$(find_file "1.jpg")
SOURCE_2=$(find_file "2.jpg")

# Проверяем наличие файлов
if [ -z "$SOURCE_1" ]; then
    echo "Ошибка: Файл 1.jpg не найден!"
    echo "   Искал в: images/1.jpg, ./1.jpg, ~/Downloads/1.jpg, ~/Desktop/1.jpg"
    echo ""
    echo "Поместите файл 1.jpg в одну из этих папок или укажите полный путь:"
    echo "   python3 process_demo_image.py <путь_к_1.jpg> before"
    exit 1
fi

if [ -z "$SOURCE_2" ]; then
    echo "Ошибка: Файл 2.jpg не найден!"
    echo "   Искал в: images/2.jpg, ./2.jpg, ~/Downloads/2.jpg, ~/Desktop/2.jpg"
    echo ""
    echo "Поместите файл 2.jpg в одну из этих папок или укажите полный путь:"
    echo "   python3 process_demo_image.py <путь_к_2.jpg> after"
    exit 1
fi

echo "Найдены файлы:"
echo "   ДО: $SOURCE_1"
echo "   ПОСЛЕ: $SOURCE_2"

echo ""
echo "Обработка изображений (удаление белых полей)..."

python3 process_demo_image.py "$SOURCE_1" before
if [ $? -ne 0 ]; then
    echo "Ошибка обработки 1.jpg (ДО)"
    exit 1
fi

python3 process_demo_image.py "$SOURCE_2" after
if [ $? -ne 0 ]; then
    echo "Ошибка обработки 2.jpg (ПОСЛЕ)"
    exit 1
fi

echo ""
echo "Изображения успешно обновлены!"
echo "   ДО: static/images/demo-before-1.png"
echo "   ПОСЛЕ: static/images/demo-after-1.png"

