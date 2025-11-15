#!/bin/bash

# Скрипт для быстрого деплоя Facy
# Использует предоставленные токены

set -e

# Токены загружаются из переменных окружения или TOKENS.md
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
BOT_TOKEN="${BOT_TOKEN:-}"

echo "🚀 Настройка деплоя Facy"
echo "========================"
echo ""

# Цвета
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Проверка GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}GitHub CLI не установлен. Установите: brew install gh${NC}"
    exit 1
fi

# Авторизация в GitHub
echo -e "${BLUE}Авторизация в GitHub...${NC}"
echo "$GITHUB_TOKEN" | gh auth login --with-token 2>/dev/null || true
gh auth status

# Настройка GitHub Secrets
echo -e "${BLUE}Настройка GitHub Secrets...${NC}"
gh secret set BOT_TOKEN --body "$BOT_TOKEN" 2>&1 | grep -v "already exists" || true
echo -e "${GREEN}✓ BOT_TOKEN добавлен${NC}"

echo ""
echo -e "${GREEN}✅ GitHub Secrets настроены!${NC}"
echo ""
echo "Следующие шаги:"
echo ""
echo "1. Railway:"
echo "   - Откройте https://railway.app"
echo "   - Войдите через GitHub"
echo "   - New Project → Deploy from GitHub repo → выберите GrekEv/facy-app"
echo "   - В Variables добавьте:"
echo "     BOT_TOKEN=$BOT_TOKEN"
echo "     WEBAPP_URL=https://ваш-vercel-url.vercel.app (обновим после Vercel)"
echo "     ENVIRONMENT=production"
echo ""
echo "2. Vercel:"
echo "   - Откройте https://vercel.com"
echo "   - Войдите через GitHub"
echo "   - Add New Project → выберите GrekEv/facy-app"
echo "   - Обновите vercel.json: замените YOUR-RAILWAY-URL на Railway URL"
echo "   - Deploy"
echo ""
echo "3. Обновите Railway:"
echo "   - Обновите WEBAPP_URL в Railway на Vercel URL"
echo ""
echo "4. Настройте бота:"
echo "   - BotFather → Menu Button → укажите Vercel URL"
echo ""

