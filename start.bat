@echo off
chcp 65001 >nul
echo 🚀 Запуск DeepFace AI...
echo.

REM Проверка виртуального окружения
if not exist "venv\" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
)

REM Активация виртуального окружения
echo ✓ Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Установка зависимостей
echo 📥 Установка зависимостей...
pip install -r requirements.txt

REM Проверка .env файла
if not exist ".env" (
    echo ⚠️  Файл .env не найден!
    echo 📝 Создание .env из .env.example...
    copy .env.example .env
    echo.
    echo ❗ ВАЖНО: Отредактируйте файл .env и укажите ваш BOT_TOKEN!
    echo ❗ Получите токен у @BotFather в Telegram
    echo.
    pause
)

REM Запуск API сервера в новом окне
echo 🌐 Запуск API сервера...
start "DeepFace API" cmd /k python run_api.py

REM Пауза перед запуском бота
timeout /t 3 /nobreak >nul

REM Запуск бота в новом окне
echo 🤖 Запуск Telegram бота...
start "DeepFace Bot" cmd /k python main.py

echo.
echo ✅ Приложение запущено!
echo 📊 API сервер: http://localhost:8000
echo 🤖 Telegram бот: активен
echo.
echo Закройте окна для остановки приложения
echo.
pause

