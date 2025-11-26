# Настройка SSL для onlyface.art

## Let's Encrypt на сервере

Скрипт setup_domain_onlyface.sh автоматически:
- Устанавливает Certbot
- Получает SSL сертификат от Let's Encrypt
- Настраивает автоматическое обновление
- Настраивает Nginx для HTTPS

Запуск:
```bash
./setup_domain_onlyface.sh
```

## SSL от Timeweb

1. "Домены и SSL" → onlyface.art → "SSL сертификаты"
2. "Получить бесплатный SSL" или "Активировать SSL"

Если используете SSL от Timeweb, пропустите шаг получения SSL в скрипте.

## Проверка SSL

```bash
curl -I https://onlyface.art
```
