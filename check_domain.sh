#!/bin/bash
# Проверка домена и DNS

DOMAIN="onlyface.art"
SERVER_IP="72.56.85.215"

echo "=== ПРОВЕРКА ДОМЕНА ==="
echo ""

echo "1. Проверка DNS:"
DOMAIN_IP=$(dig +short $DOMAIN @8.8.8.8 | tail -1)
if [ -n "$DOMAIN_IP" ]; then
    echo "  DNS: $DOMAIN -> $DOMAIN_IP"
    if [ "$DOMAIN_IP" = "$SERVER_IP" ]; then
        echo "  ✓ DNS указывает на правильный IP ($SERVER_IP)"
    else
        echo "  ✗ DNS указывает на $DOMAIN_IP, ожидается $SERVER_IP"
        echo "  Настройте A-запись в Timeweb или reg.ru"
    fi
else
    echo "  ✗ Домен не резолвится"
    echo "  DNS записи еще не настроены или не обновились"
fi

echo ""
echo "2. Проверка www поддомена:"
WWW_IP=$(dig +short www.$DOMAIN @8.8.8.8 | tail -1)
if [ -n "$WWW_IP" ]; then
    echo "  DNS: www.$DOMAIN -> $WWW_IP"
    if [ "$WWW_IP" = "$SERVER_IP" ]; then
        echo "  ✓ www DNS настроен правильно"
    else
        echo "  ✗ www указывает на $WWW_IP"
    fi
else
    echo "  ✗ www поддомен не резолвится"
fi

echo ""
echo "3. Проверка HTTP (порт 80):"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://$DOMAIN/ 2>/dev/null || echo "timeout")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "  ✓ HTTP работает (код: $HTTP_CODE)"
else
    echo "  ✗ HTTP не работает (код: $HTTP_CODE)"
    if [ "$HTTP_CODE" = "timeout" ]; then
        echo "    Возможные причины:"
        echo "    - DNS не настроен"
        echo "    - Nginx не запущен"
        echo "    - Firewall блокирует порт 80"
    fi
fi

echo ""
echo "4. Проверка HTTPS (порт 443):"
HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://$DOMAIN/ 2>/dev/null || echo "timeout")
if [ "$HTTPS_CODE" = "200" ] || [ "$HTTPS_CODE" = "301" ] || [ "$HTTPS_CODE" = "302" ]; then
    echo "  ✓ HTTPS работает (код: $HTTPS_CODE)"
elif [ "$HTTPS_CODE" = "timeout" ]; then
    echo "  ✗ HTTPS не работает (timeout)"
    echo "    Возможные причины:"
    echo "    - DNS не настроен"
    echo "    - SSL сертификат не получен"
    echo "    - Nginx не настроен для HTTPS"
    echo "    - Firewall блокирует порт 443"
else
    echo "  ✗ HTTPS не работает (код: $HTTPS_CODE)"
fi

echo ""
echo "5. Проверка на сервере (если доступен SSH):"
echo "  ssh root@$SERVER_IP 'curl -s http://localhost:8000/health'"
echo "  ssh root@$SERVER_IP 'sudo systemctl status nginx'"
echo "  ssh root@$SERVER_IP 'sudo ufw status | grep 443'"

echo ""
echo "=== РЕКОМЕНДАЦИИ ==="
if [ -z "$DOMAIN_IP" ] || [ "$DOMAIN_IP" != "$SERVER_IP" ]; then
    echo "1. Настройте DNS записи в Timeweb:"
    echo "   - A запись: @ -> $SERVER_IP"
    echo "   - A запись: www -> $SERVER_IP"
    echo "2. Подождите 5-15 минут для распространения DNS"
fi

if [ "$HTTPS_CODE" = "timeout" ] && [ "$HTTP_CODE" != "timeout" ]; then
    echo "3. Настройте SSL сертификат:"
    echo "   ssh root@$SERVER_IP"
    echo "   cd ~/facy-app"
    echo "   ./setup_domain_onlyface.sh"
fi

