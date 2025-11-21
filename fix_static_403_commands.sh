#!/bin/bash
# Команды для исправления 403 на статических файлах
# Выполните эти команды на сервере

echo "=== Исправление прав доступа ==="
chmod -R 755 ~/facy-app/static/
chmod -R 755 ~/facy-app/uploads/
chmod -R 755 ~/facy-app/generated/

# Исправленная команда find (без проблем с экранированием)
find ~/facy-app/static/ -type f -exec chmod 644 {} +
find ~/facy-app/uploads/ -type f -exec chmod 644 {} +
find ~/facy-app/generated/ -type f -exec chmod 644 {} +

echo "=== Обновление конфигурации Nginx ==="
APP_DIR=$(cd ~/facy-app && pwd)

sudo tee /etc/nginx/sites-available/onlyface > /dev/null <<NGINX_EOF
server {
    listen 80;
    server_name onlyface.art www.onlyface.art;

    client_max_body_size 100M;

    location /static/ {
        alias ${APP_DIR}/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    location /uploads/ {
        alias ${APP_DIR}/uploads/;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }
    
    location /generated/ {
        alias ${APP_DIR}/generated/;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
NGINX_EOF

sudo ln -sf /etc/nginx/sites-available/onlyface /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo "=== Проверка и перезапуск Nginx ==="
sudo nginx -t && sudo systemctl restart nginx

echo "=== Готово! ==="
echo "Проверка:"
echo "  curl -I http://localhost/static/css/style.css"
