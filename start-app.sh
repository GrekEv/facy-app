#!/bin/bash
# �втомат�че�к�й запу�к п��ложен�� Facy

set -e

cd ~/facy-app

echo " ��ове�ка .env файла..."
if [ ! -f .env ]; then
    echo " Файл .env не найден! �озда�..."
    cat > .env << 'ENVEOF'
# ОБ�З�ТЕЛ��ЫЕ �Е�Е�Е��ЫЕ
BOT_TOKEN=your_bot_token_here
WEBAPP_URL=http://158.160.96.182:8000
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
HOST=0.0.0.0
PORT=8000

# ============================================
# API �ЛЮ�И �Л� �Е�Е��ЦИИ ИЗОБ��ЖЕ�ИЙ
# ============================================

# Replicate (�екомендует�� дл� �зо��ажен�й)
REPLICATE_API_KEY=your_replicate_api_key_here
REPLICATE_API_URL=https://api.replicate.com/v1

# ============================================
# API �ЛЮ�И �Л� �Е�Е��ЦИИ �И�ЕО
# ============================================

# OpenAI Sora (дл� �ене�ац�� в�део)
OPENAI_API_KEY=your_openai_api_key_here
SORA_MODEL=sora-1.0-pro

# Higgsfield.ai (опц�онал�но)
HIGGSFIELD_API_KEY=
HIGGSFIELD_API_URL=https://api.higgsfield.ai

# ============================================
# �ЫБО� ��О��Й�Е�О�
# ============================================

# �л� �ене�ац�� �зо��ажен�й
IMAGE_GENERATION_PROVIDER=replicate

# �л� �ене�ац�� в�део
VIDEO_GENERATION_PROVIDER=sora
ENVEOF
    echo " Файл .env �оздан!"
fi

echo ""
echo " ��о�ка Docker о��азов..."
docker-compose -f docker-compose.prod.yml build

echo ""
echo " Запу�к п��ложен��..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo " Ож�дан�е запу�ка (15 �екунд)..."
sleep 15

echo ""
echo " �тату� контейне�ов:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo " ��ове�ка API..."
sleep 5
curl -f http://localhost:8000/health && echo " API �а�отает!" || echo " API е�е запу�кает��..."

echo ""
echo " �отово! ���ложен�е запу�ено."
echo ""
echo "��ове�ка:"
echo "  - API: http://158.160.96.182:8000/health"
echo "  - Web App: http://158.160.96.182:8000"
echo ""
echo "Ло��:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"

