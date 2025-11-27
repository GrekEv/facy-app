#!/bin/bash
# Установка SSL сертификата Timeweb для PostgreSQL

echo "=========================================="
echo "УСТАНОВКА SSL СЕРТИФИКАТА TIMEWEB"
echo "=========================================="
echo ""

# Создаем директорию для сертификатов
CERT_DIR="$HOME/.cloud-certs"
mkdir -p "$CERT_DIR"

echo "1. Создание директории для сертификатов..."
echo "   Директория: $CERT_DIR"
echo ""

# Вариант 1: Скачать с сервера Timeweb
echo "2. Скачивание сертификата с сервера Timeweb..."
if curl -o "$CERT_DIR/root.crt" "https://st.timeweb.com/cloud-static/ca.crt" 2>/dev/null; then
    chmod 0600 "$CERT_DIR/root.crt"
    echo "   ✓ Сертификат скачан и установлен"
    echo "   Файл: $CERT_DIR/root.crt"
else
    echo "   ✗ Не удалось скачать сертификат автоматически"
    echo ""
    echo "   Альтернатива: загрузите файл ca.crt вручную"
    echo "   scp ca.crt root@72.56.85.215:$CERT_DIR/root.crt"
    exit 1
fi

echo ""
echo "3. Проверка сертификата..."
if [ -f "$CERT_DIR/root.crt" ]; then
    CERT_SIZE=$(stat -c%s "$CERT_DIR/root.crt" 2>/dev/null || stat -f%z "$CERT_DIR/root.crt" 2>/dev/null)
    echo "   ✓ Сертификат установлен"
    echo "   Размер: $CERT_SIZE байт"
    echo "   Права доступа: $(ls -l "$CERT_DIR/root.crt" | awk '{print $1}')"
else
    echo "   ✗ Сертификат не найден"
    exit 1
fi

echo ""
echo "4. Настройка переменной окружения..."
echo "   Добавьте в ~/.bashrc или ~/.profile:"
echo "   export PGSSLROOTCERT=\$HOME/.cloud-certs/root.crt"
echo ""

# Добавляем в .bashrc если его нет
if ! grep -q "PGSSLROOTCERT" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# Timeweb PostgreSQL SSL Certificate" >> ~/.bashrc
    echo "export PGSSLROOTCERT=\$HOME/.cloud-certs/root.crt" >> ~/.bashrc
    echo "   ✓ Добавлено в ~/.bashrc"
else
    echo "   ✓ Уже настроено в ~/.bashrc"
fi

# Экспортируем для текущей сессии
export PGSSLROOTCERT="$CERT_DIR/root.crt"

echo ""
echo "=========================================="
echo "✓ СЕРТИФИКАТ УСТАНОВЛЕН"
echo "=========================================="
echo ""
echo "Для применения в текущей сессии выполните:"
echo "  export PGSSLROOTCERT=\$HOME/.cloud-certs/root.crt"
echo ""
echo "Или перезайдите в SSH сессию."
echo ""
echo "Примечание: Для Python приложений с asyncpg и параметром"
echo "?ssl=require сертификат устанавливать не обязательно -"
echo "библиотека сама обработает SSL."
echo ""

