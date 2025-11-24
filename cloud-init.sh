#!/bin/bash

set -e

apt-get update
apt-get upgrade -y

apt-get install -y curl wget git apt-transport-https ca-certificates gnupg lsb-release ufw python3-pip

if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

if [ -n "$SUDO_USER" ]; then
    usermod -aG docker $SUDO_USER
elif [ -n "$USER" ]; then
    usermod -aG docker $USER || true
fi
usermod -aG docker ubuntu || true

ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp

if [ -d "/home/ubuntu" ]; then
    APP_DIR="/home/ubuntu/facy-app"
    cd /home/ubuntu
elif [ -d "/root" ]; then
    APP_DIR="/root/facy-app"
    cd /root
else
    APP_DIR="$HOME/facy-app"
    cd $HOME
fi

if [ ! -d "$APP_DIR" ]; then
    git clone https://github.com/GrekEv/facy-app.git
    cd facy-app
else
    cd facy-app
    git pull || true
fi

mkdir -p data uploads generated temp

if [ ! -f .env ]; then
    SERVER_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "YOUR_SERVER_IP")
    cat > .env << EOF
BOT_TOKEN=your_bot_token_here
WEBAPP_URL=http://${SERVER_IP}:8000
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
HOST=0.0.0.0
PORT=8000
ADMIN_IDS=
DEEPFACE_API_KEY=
DEEPFACE_API_URL=https://deepfacevideo.com/api
REPLICATE_API_KEY=
REPLICATE_API_URL=https://api.replicate.com/v1
REPLICATE_IMAGE_MODEL=ideogram-ai/ideogram-v3-turbo
REPLICATE_VIDEO_MODEL=minimax/video-01
OPENAI_API_KEY=
SORA_MODEL=sora-1.0-pro
HIGGSFIELD_API_KEY=
HIGGSFIELD_API_URL=https://api.higgsfield.ai
IMAGE_GENERATION_PROVIDER=replicate
VIDEO_GENERATION_PROVIDER=replicate
EOF
fi
