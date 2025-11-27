# Исправление ERR_CONNECTION_REFUSED

## Проблема
Домен `onlyface.art` не отвечает - ошибка `ERR_CONNECTION_REFUSED`.

## Причина
На сервере не запущен Nginx или не настроен firewall.

## Решение

### Вариант 1: Автоматическая настройка (рекомендуется)

Подключитесь к серверу и запустите скрипт:

```bash
ssh root@72.56.85.215
cd ~/facy-app

# Если скрипт есть локально
./setup_domain_onlyface.sh

# Или скачайте с GitHub
wget https://raw.githubusercontent.com/GrekEv/facy-app/main/setup_domain_onlyface.sh
chmod +x setup_domain_onlyface.sh
./setup_domain_onlyface.sh
```

Скрипт автоматически:
- Установит и настроит Nginx
- Получит SSL сертификат (Let's Encrypt)
- Запустит API (Docker Compose)
- Настроит firewall (порты 80, 443)

### Вариант 2: Ручная проверка

```bash
ssh root@72.56.85.215

# 1. Проверка Nginx
sudo systemctl status nginx
# Если не запущен:
sudo systemctl start nginx
sudo systemctl enable nginx

# 2. Проверка API
curl http://localhost:8000/health
# Если не работает:
cd ~/facy-app
docker compose -f docker-compose.prod.yml up -d

# 3. Проверка firewall
sudo ufw status
# Если порты закрыты:
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 4. Проверка конфигурации Nginx
ls -la /etc/nginx/sites-enabled/
# Если нет конфигурации для onlyface.art:
# Используйте скрипт setup_domain_onlyface.sh
```

## Проверка после исправления

```bash
# С вашего компьютера
curl -I http://onlyface.art
curl -I https://onlyface.art

# Должны вернуть HTTP 200 или 301/302
```

## Важно

- **DNS уже настроен** - домен указывает на правильный IP (72.56.85.215)
- **Проблема на сервере** - нужно настроить Nginx и запустить API
- **Timeweb/reg.ru** - только для DNS, настройки сервера делаются через SSH

