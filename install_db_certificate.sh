#!/bin/bash
# Установка SSL сертификата для PostgreSQL на Timeweb

echo "=========================================="
echo "УСТАНОВКА SSL СЕРТИФИКАТА ДЛЯ БД"
echo "=========================================="
echo ""

# Создаем директорию для сертификатов
CERT_DIR="$HOME/.cloud-certs"
mkdir -p "$CERT_DIR"

echo "1. Скачивание сертификата..."
CERT_URL="https://st.timeweb.com/cloud-static/ca.crt"
CERT_FILE="$CERT_DIR/root.crt"

# Скачиваем сертификат
if curl -o "$CERT_FILE" "$CERT_URL" 2>/dev/null; then
    echo "  ✓ Сертификат скачан: $CERT_FILE"
else
    echo "  ✗ Ошибка скачивания сертификата"
    echo "  Попробуйте скачать вручную:"
    echo "    curl -o $CERT_FILE $CERT_URL"
    exit 1
fi

# Устанавливаем правильные права
chmod 0600 "$CERT_FILE"
echo "  ✓ Права установлены (0600)"

echo ""
echo "2. Проверка сертификата..."
if [ -f "$CERT_FILE" ]; then
    CERT_SIZE=$(stat -f%z "$CERT_FILE" 2>/dev/null || stat -c%s "$CERT_FILE" 2>/dev/null)
    echo "  ✓ Файл существует: $CERT_FILE"
    echo "  ✓ Размер: $CERT_SIZE байт"
    
    # Показываем первые строки сертификата
    echo ""
    echo "  Содержимое (первые 3 строки):"
    head -3 "$CERT_FILE" | sed 's/^/    /'
else
    echo "  ✗ Файл сертификата не найден!"
    exit 1
fi

echo ""
echo "3. Настройка переменной окружения..."
# Добавляем в .bashrc если еще нет
if ! grep -q "PGSSLROOTCERT" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# Timeweb PostgreSQL SSL Certificate" >> ~/.bashrc
    echo "export PGSSLROOTCERT=\$HOME/.cloud-certs/root.crt" >> ~/.bashrc
    echo "  ✓ Добавлено в ~/.bashrc"
else
    echo "  ✓ Уже настроено в ~/.bashrc"
fi

# Устанавливаем для текущей сессии
export PGSSLROOTCERT="$CERT_FILE"
echo "  ✓ Установлено для текущей сессии"

echo ""
echo "=========================================="
echo "✓ СЕРТИФИКАТ УСТАНОВЛЕН"
echo "=========================================="
echo ""
echo "Расположение: $CERT_FILE"
echo "Переменная: PGSSLROOTCERT=$PGSSLROOTCERT"
echo ""
echo "Для применения в текущей сессии выполните:"
echo "  export PGSSLROOTCERT=\$HOME/.cloud-certs/root.crt"
echo ""
echo "Или перезайдите в SSH сессию."
echo ""

