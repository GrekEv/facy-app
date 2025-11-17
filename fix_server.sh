#!/bin/bash
# Команда для выполнения на сервере через SSH
# Скопируйте и выполните эту команду на сервере

cd ~/facy-app && cat > fix_all.sh << 'SCRIPTEOF'
#!/bin/bash
set -e
cd ~/facy-app || exit 1
echo "🔧 Исправление всех проблем..."

# 1. Config.py - ENVIRONMENT
if ! grep -q "ENVIRONMENT: str" config.py; then
    sed -i '/WEBAPP_URL: str/a\    \n    # Environment\n    ENVIRONMENT: str = "production"  # development, production' config.py
fi

# 2. Config.py - extra = "ignore"
if ! grep -q 'extra = "ignore"' config.py; then
    sed -i '/case_sensitive = True/a\        extra = "ignore"  # Игнорировать дополнительные поля из .env' config.py
fi

# 3. api/main.py - импорты
sed -i 's/from \.schemas import/from api.schemas import/g' api/main.py
sed -i 's/from \. import payments/from api import payments/g' api/main.py

# 4. docker-compose.yml - удаляем version
sed -i '/^version:/d' docker-compose.yml

# 5. models.py - DeclarativeBase
sed -i 's/from sqlalchemy.ext.declarative import declarative_base/from sqlalchemy.orm import DeclarativeBase, relationship/g' database/models.py
if grep -q "^Base = declarative_base()" database/models.py; then
    sed -i 's/^Base = declarative_base()$/class Base(DeclarativeBase):\n    """Базовый класс для всех моделей"""\n    pass/g' database/models.py
fi

# 6. КРИТИЧЕСКОЕ: metadata -> transaction_metadata
sed -i 's/^    metadata = Column(Text, nullable=True)/    transaction_metadata = Column(Text, nullable=True)/g' database/models.py

# 7. docker-compose.prod.yml - healthcheck
if ! grep -q "start_period" docker-compose.prod.yml; then
    sed -i '/retries: 3$/a\      start_period: 40s' docker-compose.prod.yml 2>/dev/null || sed -i '/retries: 5$/a\      start_period: 40s' docker-compose.prod.yml
    sed -i 's/retries: 3/retries: 5/g' docker-compose.prod.yml
fi

echo "✅ Все исправлено!"
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose down 2>/dev/null || true
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
sleep 25
docker compose -f docker-compose.prod.yml ps
echo ""
echo "📋 Логи API:"
docker compose -f docker-compose.prod.yml logs api --tail=40
SCRIPTEOF
chmod +x fix_all.sh && ./fix_all.sh


