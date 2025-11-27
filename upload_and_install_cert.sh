#!/bin/bash
# Загрузка и установка сертификата с локального компьютера на сервер

SERVER="root@72.56.85.215"
CERT_FILE="ca.crt"

echo "=========================================="
echo "ЗАГРУЗКА И УСТАНОВКА СЕРТИФИКАТА"
echo "=========================================="
echo ""

# Проверка наличия файла локально
if [ ! -f "$CERT_FILE" ]; then
    echo "✗ Файл $CERT_FILE не найден в текущей директории!"
    echo ""
    echo "Скачайте сертификат:"
    echo "  1. Откройте https://timeweb.cloud/my/database/4109791/connect"
    echo "  2. Нажмите 'Скачать сертификат'"
    echo "  3. Сохраните файл как 'ca.crt' в текущей директории"
    echo ""
    echo "Или скачайте напрямую:"
    echo "  curl -o ca.crt https://st.timeweb.com/cloud-static/ca.crt"
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
    exit 1
fi

echo ""
echo "2. Установка прав и настройка на сервере..."
ssh "$SERVER" << 'EOF'
    # Создаем директорию если нет
    mkdir -p ~/.cloud-certs
    
    # Устанавливаем права
    chmod 0600 ~/.cloud-certs/root.crt
    
    # Добавляем в .bashrc
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
EOF

echo ""
echo "=========================================="
echo "✓ ГОТОВО!"
echo "=========================================="
echo ""
echo "Сертификат установлен на сервере."
echo "Для применения выполните на сервере:"
echo "  export PGSSLROOTCERT=\$HOME/.cloud-certs/root.crt"
echo ""

