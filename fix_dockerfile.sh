#!/bin/bash
# Скрипт для быстрого исправления Dockerfile на сервере

# Переход в директорию проекта
cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

# Создание резервной копии
cp Dockerfile Dockerfile.backup

# Замена libgl1-mesa-glx на libgl1
sed -i 's/libgl1-mesa-glx/libgl1/g' Dockerfile

echo "✅ Dockerfile исправлен!"
echo "Теперь запустите: docker compose build"

