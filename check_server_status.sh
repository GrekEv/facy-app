#!/bin/bash
# Полная проверка состояния сервера onlyface.art

DOMAIN="onlyface.art"
SERVER_IP="72.56.85.215"

echo "=========================================="
echo "ПРОВЕРКА СЕРВЕРА onlyface.art"
echo "=========================================="
echo ""

echo "1. DNS ПРОВЕРКА:"
DOMAIN_IP=$(dig +short $DOMAIN | tail -1)
if [ "$DOMAIN_IP" = "$SERVER_IP" ]; then
    echo "  ✓ DNS: $DOMAIN -> $DOMAIN_IP (правильно)"
else
    echo "  ✗ DNS: $DOMAIN -> $DOMAIN_IP (ожидается $SERVER_IP)"
    echo "     Настройте A-запись в Timeweb"
fi
echo ""

echo "2. ДОСТУПНОСТЬ СЕРВЕРА:"
if ping -c 1 -W 2 $SERVER_IP > /dev/null 2>&1; then
    echo "  ✓ Сервер $SERVER_IP доступен"
else
    echo "  ✗ Сервер $SERVER_IP недоступен"
fi
echo ""

echo "3. HTTP (порт 80):"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://$DOMAIN/ 2>/dev/null || echo "FAILED")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "  ✓ HTTP работает (код: $HTTP_CODE)"
elif [ "$HTTP_CODE" = "FAILED" ]; then
    echo "  ✗ HTTP не работает (connection refused)"
    echo "     Возможные причины:"
    echo "     - Nginx не запущен"
    echo "     - Firewall блокирует порт 80"
    echo "     - Nginx не настроен для домена"
else
    echo "  ✗ HTTP не работает (код: $HTTP_CODE)"
fi
echo ""

echo "4. HTTPS (порт 443):"
HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://$DOMAIN/ 2>/dev/null || echo "FAILED")
if [ "$HTTPS_CODE" = "200" ] || [ "$HTTPS_CODE" = "301" ] || [ "$HTTPS_CODE" = "302" ]; then
    echo "  ✓ HTTPS работает (код: $HTTPS_CODE)"
elif [ "$HTTPS_CODE" = "FAILED" ]; then
    echo "  ✗ HTTPS не работает (connection refused)"
    echo "     Возможные причины:"
    echo "     - SSL сертификат не получен"
    echo "     - Nginx не настроен для HTTPS"
    echo "     - Firewall блокирует порт 443"
else
    echo "  ✗ HTTPS не работает (код: $HTTPS_CODE)"
fi
echo ""

echo "=========================================="
echo "ЧТО ДЕЛАТЬ:"
echo "=========================================="
echo ""
echo "Подключитесь к серверу и выполните:"
echo ""
echo "  ssh root@$SERVER_IP"
echo "  cd ~/facy-app"
echo ""
echo "Затем проверьте:"
echo ""
echo "  1. Запущен ли Nginx:"
echo "     sudo systemctl status nginx"
echo ""
echo "  2. Запущен ли API:"
echo "     curl http://localhost:8000/health"
echo ""
echo "  3. Настроен ли firewall:"
echo "     sudo ufw status"
echo ""
echo "  4. Есть ли конфигурация Nginx:"
echo "     ls -la /etc/nginx/sites-enabled/"
echo ""
echo "Если что-то не работает, запустите:"
echo "  ./setup_domain_onlyface.sh"
echo ""
echo "Или скачайте скрипт с GitHub:"
echo "  wget https://raw.githubusercontent.com/GrekEv/facy-app/main/setup_domain_onlyface.sh"
echo "  chmod +x setup_domain_onlyface.sh"
echo "  ./setup_domain_onlyface.sh"
echo ""

