#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_URL="${1:-http://localhost:8000}"

echo "Проверка API: $API_URL"
echo ""

check_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=${3:-200}
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" 2>/dev/null)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ] || [ "$http_code" = "200" ] || [ "$http_code" = "404" ]; then
        echo -e "${GREEN}✓${NC} $method $endpoint - HTTP $http_code"
        if [ -n "$body" ] && [ ${#body} -lt 200 ]; then
            echo "  Ответ: $(echo "$body" | head -c 100)"
        fi
    else
        echo -e "${RED}✗${NC} $method $endpoint - HTTP $http_code"
    fi
}

echo "Health checks:"
check_endpoint "GET" "/health"
check_endpoint "GET" "/api/health"
echo ""

echo "Публичные эндпоинты:"
check_endpoint "GET" "/api/models"
check_endpoint "GET" "/api/styles"
check_endpoint "GET" "/api/video/models"
check_endpoint "GET" "/api/video/styles"
check_endpoint "GET" "/api/stats"
echo ""

echo "Платежи:"
check_endpoint "GET" "/api/payments/status/1"
echo ""

echo "Проверка завершена"
echo ""
echo "Для проверки с доменом:"
echo "  ./check_api.sh https://onlyface.art"

