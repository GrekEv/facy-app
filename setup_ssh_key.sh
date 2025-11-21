#!/bin/bash
# Скрипт для создания и настройки SSH ключа для Yandex Cloud

echo "=== Настройка SSH ключа для Yandex Cloud ==="
echo ""

# Проверка существующих ключей
if [ -f ~/.ssh/id_ed25519 ] || [ -f ~/.ssh/id_rsa ]; then
    echo "Найдены существующие SSH ключи:"
    ls -la ~/.ssh/id_* 2>/dev/null | grep -v ".pub"
    echo ""
    read -p "Использовать существующий ключ? (y/n): " use_existing
    if [ "$use_existing" = "y" ]; then
        if [ -f ~/.ssh/id_ed25519.pub ]; then
            KEY_FILE=~/.ssh/id_ed25519.pub
        elif [ -f ~/.ssh/id_rsa.pub ]; then
            KEY_FILE=~/.ssh/id_rsa.pub
        fi
    fi
fi

# Создание нового ключа если нужно
if [ -z "$KEY_FILE" ]; then
    echo "Создание нового SSH ключа..."
    ssh-keygen -t ed25519 -C "yandex-cloud-$(date +%Y%m%d)" -f ~/.ssh/yandex_cloud -N ""
    KEY_FILE=~/.ssh/yandex_cloud.pub
fi

echo ""
echo "=== ВАШ ПУБЛИЧНЫЙ SSH КЛЮЧ ==="
echo ""
cat "$KEY_FILE"
echo ""
echo "=========================================="
echo ""
echo "ИНСТРУКЦИЯ:"
echo "1. Скопируйте ключ выше"
echo "2. Откройте: https://console.cloud.yandex.ru"
echo "3. Compute Cloud → Виртуальные машины"
echo "4. Найдите сервер 158.160.96.182"
echo "5. Нажмите 'Редактировать'"
echo "6. В разделе 'SSH ключи' нажмите 'Добавить'"
echo "7. Вставьте скопированный ключ"
echo "8. Сохраните"
echo ""
echo "После этого подключитесь:"
if [ -f ~/.ssh/yandex_cloud ]; then
    echo "  ssh -i ~/.ssh/yandex_cloud ubuntu@158.160.96.182"
else
    echo "  ssh ubuntu@158.160.96.182"
fi

