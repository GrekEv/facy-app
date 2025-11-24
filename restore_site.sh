#!/bin/bash

set -e

if [ ! -d "/home/ubuntu" ]; then
    exit 1
fi

cd ~/facy-app || exit 1

if command -v docker &> /dev/null; then
    if ! docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        docker compose -f docker-compose.prod.yml up -d
    fi
else
    if ! pgrep -f "run_api.py\|main.py" > /dev/null; then
        nohup python3 run_api.py > /tmp/api.log 2>&1 &
        nohup python3 main.py > /tmp/bot.log 2>&1 &
        sleep 2
    fi
fi

if ! sudo systemctl is-active --quiet nginx; then
    sudo systemctl start nginx
fi

if ! sudo nginx -t 2>&1 | grep -q "successful"; then
    APP_DIR=$(pwd)
    sudo tee /etc/nginx/sites-available/onlyface > /dev/null <<NGINX_EOF
server {
    listen 80;
    server_name onlyface.art www.onlyface.art;
    client_max_body_size 100M;

    location /static/ {
        alias ${APP_DIR}/static/;
    }
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
NGINX_EOF
    
    sudo rm -f /etc/nginx/sites-enabled/*
    sudo ln -sf /etc/nginx/sites-available/onlyface /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx
else
    sudo systemctl reload nginx
fi

