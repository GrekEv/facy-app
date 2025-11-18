@echo off
chcp 65001 >nul
echo  Запу�к DeepFace AI...
echo.

REM ��ове�ка в��туал�но�о ок�ужен��
if not exist "venv\" (
    echo � �оздан�е в��туал�но�о ок�ужен��...
    python -m venv venv
)

REM �кт�вац�� в��туал�но�о ок�ужен��
echo  �кт�вац�� в��туал�но�о ок�ужен��...
call venv\Scripts\activate.bat

REM У�тановка зав���мо�тей
echo  У�тановка зав���мо�тей...
pip install -r requirements.txt

REM ��ове�ка .env файла
if not exist ".env" (
    echo   Файл .env не найден!
    echo  �оздан�е .env �з .env.example...
    copy .env.example .env
    echo.
    echo � ��Ж�О: От�едакт��уйте файл .env � укаж�те ваш BOT_TOKEN!
    echo � �олуч�те токен у @BotFather в Telegram
    echo.
    pause
)

REM Запу�к API �е�ве�а в новом окне
echo  Запу�к API �е�ве�а...
start "DeepFace API" cmd /k python run_api.py

REM �ауза пе�ед запу�ком �ота
timeout /t 3 /nobreak >nul

REM Запу�к �ота в новом окне
echo �� Запу�к Telegram �ота...
start "DeepFace Bot" cmd /k python main.py

echo.
echo  ���ложен�е запу�ено!
echo  API �е�ве�: http://localhost:8000
echo �� Telegram �от: акт�вен
echo.
echo Зак�ойте окна дл� о�тановк� п��ложен��
echo.
pause

