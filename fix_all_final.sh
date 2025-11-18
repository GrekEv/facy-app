#!/bin/bash
# �олн�й �к��пт дл� ��п�авлен�� в�е� п�о�лем на �е�ве�е

set -e

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

echo " И�п�авлен�е в�е� п�о�лем..."

# 1. И�п�авл�ем config.py - до�авл�ем ENVIRONMENT поле
if ! grep -q "ENVIRONMENT: str" config.py; then
    echo "   �о�авл�� поле ENVIRONMENT в config.py..."
    sed -i '/WEBAPP_URL: str/a\    \n    # Environment\n    ENVIRONMENT: str = "production"  # development, production' config.py
fi

# 2. �о�авл�ем extra = "ignore" в Config кла��
if ! grep -q 'extra = "ignore"' config.py; then
    echo "   �о�авл�� extra = \"ignore\" в Config кла��..."
    sed -i '/case_sensitive = True/a\        extra = "ignore"  # И�но���оват� дополн�тел�н�е пол� �з .env' config.py
fi

# 3. И�п�авл�ем �мпо�т� в api/main.py
echo "   И�п�авл�� �мпо�т� в api/main.py..."
sed -i 's/from \.schemas import/from api.schemas import/g' api/main.py
sed -i 's/from \. import payments/from api import payments/g' api/main.py

# 4. Удал�ем у�та�евш�й version �з docker-compose.yml
if grep -q "^version:" docker-compose.yml; then
    echo "   Удал�� у�та�евш�й version �з docker-compose.yml..."
    sed -i '/^version:/d' docker-compose.yml
fi

# 5. И�п�авл�ем models.py - о�новл�ем Base на DeclarativeBase
echo "   О�новл�� Base на DeclarativeBase в models.py..."
sed -i 's/from sqlalchemy.ext.declarative import declarative_base/from sqlalchemy.orm import DeclarativeBase, relationship/g' database/models.py
sed -i 's/^Base = declarative_base()$/class Base(DeclarativeBase):\n    """Базов�й кла�� дл� в�е� моделей"""\n    pass/g' database/models.py

# 6. ��ИТИ�Е��ОЕ И�����ЛЕ�ИЕ: Замен�ем metadata на transaction_metadata
echo "   И�п�авл�� metadata на transaction_metadata в Transaction кла��е..."
sed -i 's/^    metadata = Column(Text, nullable=True)/    transaction_metadata = Column(Text, nullable=True)/g' database/models.py

# 7. О�новл�ем healthcheck в docker-compose.prod.yml
echo "   О�новл�� healthcheck..."
if ! grep -q "start_period" docker-compose.prod.yml; then
    sed -i '/retries: 3$/a\      start_period: 40s' docker-compose.prod.yml
    sed -i 's/retries: 3/retries: 5/g' docker-compose.prod.yml
fi

echo ""
echo " ��е файл� ��п�авлен�!"
echo ""
echo "� О�танавл�ва� контейне��..."
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose down 2>/dev/null || true

echo ""
echo " �е�е�о���а� о��аз�..."
docker compose -f docker-compose.prod.yml build --no-cache

echo ""
echo " Запу�ка� контейне��..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo " Ож�дан�е запу�ка (25 �екунд)..."
sleep 25

echo ""
echo " �тату� контейне�ов:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo " �о�ледн�е ло�� API:"
docker compose -f docker-compose.prod.yml logs api --tail=40

echo ""
echo " �о�ледн�е ло�� Bot:"
docker compose -f docker-compose.prod.yml logs bot --tail=20

echo ""
echo " ��ове�ка health endpoint:"
sleep 5
curl -f http://localhost:8000/health 2>/dev/null && echo " API �а�отает!" || echo " API е�е запу�кает��..."

echo ""
echo " �отово!"
echo ""
echo "��ове�ка:"
echo "  - API Health: http://158.160.96.182:8000/health"
echo "  - Web App: http://158.160.96.182:8000"
echo ""
echo "��о�мот� ло�ов:"
echo "  docker compose -f docker-compose.prod.yml logs -f"

