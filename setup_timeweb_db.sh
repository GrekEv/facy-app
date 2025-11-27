#!/bin/bash
# Настройка базы данных на Timeweb

cd ~/facy-app 2>/dev/null || cd /home/ubuntu/facy-app 2>/dev/null || cd /root/facy-app 2>/dev/null || {
    echo "✗ Директория ~/facy-app не найдена!"
    exit 1
}

echo "=========================================="
echo "НАСТРОЙКА БАЗЫ ДАННЫХ НА TIMEWEB"
echo "=========================================="
echo ""

# Проверка существования .env
if [ ! -f .env ]; then
    echo "✗ .env файл не найден!"
    echo "Создайте .env файл сначала"
    exit 1
fi

echo "Варианты базы данных на Timeweb:"
echo ""
echo "1. SQLite (локальная, по умолчанию) - не требует настройки"
echo "2. PostgreSQL на Timeweb - нужно создать через панель"
echo "3. Внешняя PostgreSQL (если есть)"
echo ""

read -p "Выберите вариант (1/2/3) [1]: " DB_CHOICE
DB_CHOICE=${DB_CHOICE:-1}

case $DB_CHOICE in
    1)
        echo ""
        echo "Использование SQLite (локальная база данных)"
        
        # Удаляем старый DATABASE_URL если есть
        if grep -q "^DATABASE_URL=" .env; then
            sed -i '/^DATABASE_URL=/d' .env
        fi
        
        # Создаем директорию для базы данных
        mkdir -p data
        
        echo "✓ SQLite будет использоваться автоматически"
        echo "  База данных: data/app.db"
        ;;
        
    2)
        echo ""
        echo "Настройка PostgreSQL на Timeweb"
        echo ""
        echo "Создайте базу данных в панели Timeweb:"
        echo "  1. Откройте https://timeweb.cloud/"
        echo "  2. Перейдите в раздел 'Базы данных'"
        echo "  3. Создайте новую PostgreSQL базу данных"
        echo "  4. Скопируйте данные подключения"
        echo ""
        
        read -p "Хост базы данных: " DB_HOST
        read -p "Порт [5432]: " DB_PORT
        DB_PORT=${DB_PORT:-5432}
        read -p "Имя базы данных: " DB_NAME
        read -p "Пользователь: " DB_USER
        read -sp "Пароль: " DB_PASSWORD
        echo ""
        
        if [ -z "$DB_HOST" ] || [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
            echo "✗ Все поля обязательны!"
            exit 1
        fi
        
        # Формируем DATABASE_URL для asyncpg
        DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?ssl=require"
        
        # Обновляем .env
        if grep -q "^DATABASE_URL=" .env; then
            sed -i "s|^DATABASE_URL=.*|DATABASE_URL=${DATABASE_URL}|g" .env
        else
            echo "DATABASE_URL=${DATABASE_URL}" >> .env
        fi
        
        echo "✓ DATABASE_URL обновлен"
        ;;
        
    3)
        echo ""
        read -p "Введите DATABASE_URL (postgresql+asyncpg://...): " DATABASE_URL
        
        if [ -z "$DATABASE_URL" ]; then
            echo "✗ DATABASE_URL не может быть пустым!"
            exit 1
        fi
        
        # Обновляем .env
        if grep -q "^DATABASE_URL=" .env; then
            sed -i "s|^DATABASE_URL=.*|DATABASE_URL=${DATABASE_URL}|g" .env
        else
            echo "DATABASE_URL=${DATABASE_URL}" >> .env
        fi
        
        echo "✓ DATABASE_URL обновлен"
        ;;
        
    *)
        echo "✗ Неверный выбор!"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "ОБНОВЛЕНИЕ .env"
echo "=========================================="
echo ""

# Удаляем старый Yandex Cloud DATABASE_URL если есть
if grep -q "mdb.yandexcloud.net" .env; then
    echo "Удаление старого DATABASE_URL (Yandex Cloud)..."
    sed -i '/DATABASE_URL.*mdb.yandexcloud.net/d' .env
    echo "✓ Старый DATABASE_URL удален"
fi

echo ""
echo "Текущий DATABASE_URL в .env:"
if grep -q "^DATABASE_URL=" .env; then
    DB_URL=$(grep "^DATABASE_URL=" .env | cut -d'=' -f2-)
    # Скрываем пароль
    DB_URL_MASKED=$(echo "$DB_URL" | sed 's/:[^:@]*@/:***@/')
    echo "  $DB_URL_MASKED"
else
    echo "  (не установлен, будет использован SQLite)"
fi

echo ""
echo "=========================================="
echo "ПЕРЕЗАПУСК КОНТЕЙНЕРОВ"
echo "=========================================="
echo ""

# Определяем команду docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE="docker compose"
else
    echo "✗ Docker Compose не найден!"
    exit 1
fi

echo "Остановка контейнеров..."
$COMPOSE -f docker-compose.prod.yml down

echo ""
echo "Запуск контейнеров..."
$COMPOSE -f docker-compose.prod.yml up -d

echo ""
echo "Ожидание запуска (30 секунд)..."
sleep 30

echo ""
echo "Проверка статуса:"
$COMPOSE -f docker-compose.prod.yml ps

echo ""
echo "Проверка health:"
curl -s http://localhost:8000/health | head -5 || echo "API еще запускается..."

echo ""
echo "Проверка подключения к БД:"
curl -s http://localhost:8000/api/health | grep -o '"database"[^}]*}' || echo "Проверьте ответ выше"

echo ""
echo "=========================================="
echo "✓ ГОТОВО!"
echo "=========================================="
echo ""

