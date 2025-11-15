#!/bin/bash

# Скрипт для автоматической настройки деплоя Facy

set -e

echo "🚀 Настройка деплоя Facy"
echo "=========================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка наличия необходимых инструментов
check_requirements() {
    echo -e "${BLUE}Проверка требований...${NC}"
    
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}GitHub CLI не установлен. Установите: brew install gh${NC}"
    else
        echo -e "${GREEN}✓ GitHub CLI установлен${NC}"
    fi
    
    if ! command -v railway &> /dev/null; then
        echo -e "${YELLOW}Railway CLI не установлен. Установите: npm i -g @railway/cli${NC}"
    else
        echo -e "${GREEN}✓ Railway CLI установлен${NC}"
    fi
    
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}Vercel CLI не установлен. Установите: npm i -g vercel${NC}"
    else
        echo -e "${GREEN}✓ Vercel CLI установлен${NC}"
    fi
    
    echo ""
}

# Настройка Railway
setup_railway() {
    echo -e "${BLUE}Настройка Railway...${NC}"
    
    if command -v railway &> /dev/null; then
        echo "Войдите в Railway (откроется браузер)..."
        railway login
        
        echo "Создание проекта Railway..."
        railway init
        
        echo "Настройка переменных окружения..."
        echo "Введите BOT_TOKEN:"
        read -s BOT_TOKEN
        railway variables set BOT_TOKEN="$BOT_TOKEN"
        
        echo "Введите WEBAPP_URL (пока можно временный, обновим после Vercel):"
        read WEBAPP_URL
        railway variables set WEBAPP_URL="$WEBAPP_URL"
        
        railway variables set ENVIRONMENT=production
        
        echo -e "${GREEN}✓ Railway настроен${NC}"
        echo "Скопируйте Railway URL из дашборда и используйте его в vercel.json"
    else
        echo -e "${YELLOW}Railway CLI не установлен. Пропускаем...${NC}"
    fi
    
    echo ""
}

# Настройка Vercel
setup_vercel() {
    echo -e "${BLUE}Настройка Vercel...${NC}"
    
    if command -v vercel &> /dev/null; then
        echo "Войдите в Vercel..."
        vercel login
        
        echo "Создание проекта Vercel..."
        vercel --yes
        
        echo -e "${GREEN}✓ Vercel настроен${NC}"
        echo "Скопируйте Vercel URL и обновите WEBAPP_URL в Railway"
    else
        echo -e "${YELLOW}Vercel CLI не установлен. Пропускаем...${NC}"
    fi
    
    echo ""
}

# Настройка GitHub Secrets
setup_github_secrets() {
    echo -e "${BLUE}Настройка GitHub Secrets...${NC}"
    
    if command -v gh &> /dev/null; then
        echo "Для автоматического деплоя через GitHub Actions нужны секреты:"
        echo ""
        echo "1. RAILWAY_TOKEN - получите на https://railway.app/account"
        echo "2. VERCEL_TOKEN - получите на https://vercel.com/account/tokens"
        echo "3. VERCEL_ORG_ID и VERCEL_PROJECT_ID - после создания проекта в Vercel"
        echo ""
        echo "Хотите настроить секреты сейчас? (y/n)"
        read -r answer
        
        if [ "$answer" = "y" ]; then
            echo "Введите RAILWAY_TOKEN:"
            read -s RAILWAY_TOKEN
            gh secret set RAILWAY_TOKEN --body "$RAILWAY_TOKEN"
            
            echo "Введите VERCEL_TOKEN:"
            read -s VERCEL_TOKEN
            gh secret set VERCEL_TOKEN --body "$VERCEL_TOKEN"
            
            echo "Введите VERCEL_ORG_ID:"
            read VERCEL_ORG_ID
            gh secret set VERCEL_ORG_ID --body "$VERCEL_ORG_ID"
            
            echo "Введите VERCEL_PROJECT_ID:"
            read VERCEL_PROJECT_ID
            gh secret set VERCEL_PROJECT_ID --body "$VERCEL_PROJECT_ID"
            
            echo -e "${GREEN}✓ GitHub Secrets настроены${NC}"
        fi
    else
        echo -e "${YELLOW}GitHub CLI не установлен. Настройте секреты вручную в GitHub${NC}"
    fi
    
    echo ""
}

# Обновление vercel.json с Railway URL
update_vercel_config() {
    echo -e "${BLUE}Обновление vercel.json...${NC}"
    
    echo "Введите Railway URL (например: https://facy-app.up.railway.app):"
    read RAILWAY_URL
    
    # Удаляем протокол если есть
    RAILWAY_URL=${RAILWAY_URL#https://}
    RAILWAY_URL=${RAILWAY_URL#http://}
    
    # Обновляем vercel.json
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/YOUR-RAILWAY-URL/$RAILWAY_URL/g" vercel.json
    else
        # Linux
        sed -i "s/YOUR-RAILWAY-URL/$RAILWAY_URL/g" vercel.json
    fi
    
    echo -e "${GREEN}✓ vercel.json обновлен${NC}"
    echo ""
}

# Главная функция
main() {
    check_requirements
    
    echo "Выберите действие:"
    echo "1) Настроить Railway"
    echo "2) Настроить Vercel"
    echo "3) Настроить GitHub Secrets"
    echo "4) Обновить vercel.json с Railway URL"
    echo "5) Все вышеперечисленное"
    echo ""
    read -r choice
    
    case $choice in
        1) setup_railway ;;
        2) setup_vercel ;;
        3) setup_github_secrets ;;
        4) update_vercel_config ;;
        5)
            setup_railway
            setup_vercel
            update_vercel_config
            setup_github_secrets
            ;;
        *)
            echo "Неверный выбор"
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}✅ Настройка завершена!${NC}"
    echo ""
    echo "Следующие шаги:"
    echo "1. Убедитесь, что WEBAPP_URL в Railway указывает на Vercel URL"
    echo "2. Настройте Menu Button в BotFather на Vercel URL"
    echo "3. Запушьте изменения: git add . && git commit -m 'Update config' && git push"
}

main

