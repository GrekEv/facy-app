#!/bin/bash
# Установка сертификата ca.crt из папки проекта на сервер

SERVER="root@72.56.85.215"
CERT_FILE="ca.crt"

echo "=========================================="
echo "УСТАНОВКА СЕРТИФИКАТА НА СЕРВЕР"
echo "=========================================="
echo ""

# Проверка наличия файла
if [ ! -f "$CERT_FILE" ]; then
    echo "✗ Файл $CERT_FILE не найден в текущей директории!"
    echo ""
    echo "Убедитесь, что файл ca.crt находится в:"
    echo "  $(pwd)"
    exit 1
fi

echo "✓ Файл найден: $CERT_FILE"
echo ""

# Загрузка на сервер
echo "1. Загрузка сертификата на сервер..."
scp "$CERT_FILE" "$SERVER:~/.cloud-certs/root.crt"

if [ $? -eq 0 ]; then
    echo "  ✓ Файл загружен"
else
    echo "  ✗ Ошибка загрузки"
    echo ""
    echo "Проверьте:"
    echo "  - SSH доступ к серверу"
    echo "  - Правильность адреса: $SERVER"
    exit 1
fi

echo ""
echo "2. Установка прав и настройка на сервере..."
ssh "$SERVER" << 'EOF'
    # Создаем директорию если нет
    mkdir -p ~/.cloud-certs
    
    # Устанавливаем права
    chmod 0600 ~/.cloud-certs/root.crt
    
    # Добавляем в .bashrc если еще нет
    if ! grep -q "PGSSLROOTCERT" ~/.bashrc 2>/dev/null; then
        echo "" >> ~/.bashrc
        echo "# Timeweb PostgreSQL SSL Certificate" >> ~/.bashrc
        echo "export PGSSLROOTCERT=\$HOME/.cloud-certs/root.crt" >> ~/.bashrc
    fi
    
    # Устанавливаем для текущей сессии
    export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt
    
    echo "  ✓ Сертификат установлен"
    echo "  ✓ Расположение: ~/.cloud-certs/root.crt"
    echo "  ✓ Права: 0600"
    echo ""
    echo "Проверка:"
    ls -la ~/.cloud-certs/root.crt
EOF

echo ""
echo "=========================================="
echo "✓ СЕРТИФИКАТ УСТАНОВЛЕН!"
echo "=========================================="
echo ""
echo "Следующие шаги:"
echo ""
echo "1. Обновите DATABASE_URL в .env на сервере:"
echo "   ssh $SERVER"
echo "   cd ~/facy-app"
echo "   nano .env"
echo ""
echo "2. Добавьте строку (замените на ваши данные):"
echo "   DATABASE_URL=postgresql+asyncpg://gen_user:пароль@ad9d6b1abc9d6aa538e0dea5.twc1.net:5432/default_db?ssl=require"
echo ""
echo "3. Перезапустите контейнеры:"
echo "   docker compose -f docker-compose.prod.yml down"
echo "   docker compose -f docker-compose.prod.yml up -d"
echo ""

