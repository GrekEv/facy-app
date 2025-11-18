#!/bin/bash
# �к��пт дл� о�новлен�� �зо��ажен�й "�о" � "�о�ле" �з 1.jpg � 2.jpg

echo "О�новлен�е �зо��ажен�й '�о' � '�о�ле'..."

# И�ем файл� в �азн�� ме�та�
find_file() {
    local filename=$1
    # ��ове��ем в �азн�� ме�та�
    if [ -f "images/$filename" ]; then
        echo "images/$filename"
    elif [ -f "$filename" ]; then
        echo "$filename"
    elif [ -f "$HOME/Downloads/$filename" ]; then
        echo "$HOME/Downloads/$filename"
    elif [ -f "$HOME/Desktop/$filename" ]; then
        echo "$HOME/Desktop/$filename"
    else
        # И�ем файл в п�оекте
        local found=$(find . -maxdepth 3 -name "$filename" -type f 2>/dev/null | head -1)
        if [ -n "$found" ]; then
            echo "$found"
        else
            echo ""
        fi
    fi
}

# И�ем файл�
SOURCE_1=$(find_file "1.jpg")
SOURCE_2=$(find_file "2.jpg")

# ��ове��ем нал�ч�е файлов
if [ -z "$SOURCE_1" ]; then
    echo "Ош��ка: Файл 1.jpg не найден!"
    echo "   И�кал в: images/1.jpg, ./1.jpg, ~/Downloads/1.jpg, ~/Desktop/1.jpg"
    echo ""
    echo "�оме�т�те файл 1.jpg в одну �з �т�� папок �л� укаж�те полн�й пут�:"
    echo "   python3 process_demo_image.py <пут�_к_1.jpg> before"
    exit 1
fi

if [ -z "$SOURCE_2" ]; then
    echo "Ош��ка: Файл 2.jpg не найден!"
    echo "   И�кал в: images/2.jpg, ./2.jpg, ~/Downloads/2.jpg, ~/Desktop/2.jpg"
    echo ""
    echo "�оме�т�те файл 2.jpg в одну �з �т�� папок �л� укаж�те полн�й пут�:"
    echo "   python3 process_demo_image.py <пут�_к_2.jpg> after"
    exit 1
fi

echo "�айден� файл�:"
echo "   �О: $SOURCE_1"
echo "   �О�ЛЕ: $SOURCE_2"

echo ""
echo "О��а�отка �зо��ажен�й (удален�е �ел�� полей)..."

python3 process_demo_image.py "$SOURCE_1" before
if [ $? -ne 0 ]; then
    echo "Ош��ка о��а�отк� 1.jpg (�О)"
    exit 1
fi

python3 process_demo_image.py "$SOURCE_2" after
if [ $? -ne 0 ]; then
    echo "Ош��ка о��а�отк� 2.jpg (�О�ЛЕ)"
    exit 1
fi

echo ""
echo "Изо��ажен�� у�пешно о�новлен�!"
echo "   �О: static/images/demo-before-1.png"
echo "   �О�ЛЕ: static/images/demo-after-1.png"

