#!/bin/bash
# �олн�й �к��пт дл� ��п�авлен�� в�е� п�о�лем на �е�ве�е

set -e

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

echo " И�п�авлен�е в�е� п�о�лем..."

# 1. И�п�авл�ем config.py - до�авл�ем ENVIRONMENT поле
if ! grep -q "ENVIRONMENT: str" config.py; then
    echo "   �о�авл�� поле ENVIRONMENT в config.py..."
    sed -i '/WEBAPP_URL: str/a\    \n    # Environment\n    ENVIRONMENT: str = "production"  # development, production' config.py
else
    echo "   �оле ENVIRONMENT уже �у�е�твует"
fi

# 2. �о�авл�ем extra = "ignore" в Config кла��
if ! grep -q 'extra = "ignore"' config.py; then
    echo "   �о�авл�� extra = \"ignore\" в Config кла��..."
    sed -i '/case_sensitive = True/a\        extra = "ignore"  # И�но���оват� дополн�тел�н�е пол� �з .env' config.py
else
    echo "   extra = \"ignore\" уже на�т�оен"
fi

# 3. И�п�авл�ем �мпо�т� в api/main.py
echo "   И�п�авл�� �мпо�т� в api/main.py..."
sed -i 's/from \.schemas import/from api.schemas import/g' api/main.py
sed -i 's/from \. import payments/from api import payments/g' api/main.py

# 4. Удал�ем у�та�евш�й version �з docker-compose.yml
if grep -q "^version:" docker-compose.yml; then
    echo "   Удал�� у�та�евш�й version �з docker-compose.yml..."
    sed -i '/^version:/d' docker-compose.yml
else
    echo "   version уже удален"
fi

echo ""
echo " ��е файл� ��п�авлен�!"
echo ""
echo "� О�танавл�ва� контейне��..."
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose down 2>/dev/null || true

echo ""
echo " �е�е�о���а� о��аз�..."
docker compose -f docker-compose.prod.yml build

echo ""
echo " Запу�ка� контейне��..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo " Ож�дан�е запу�ка (15 �екунд)..."
sleep 15

echo ""
echo " �тату� контейне�ов:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo " �о�ледн�е ло�� API:"
docker compose -f docker-compose.prod.yml logs api --tail=30

echo ""
echo " �отово!"
echo ""
echo "��ове�ка:"
echo "  - API Health: http://158.160.96.182:8000/health"
echo "  - Web App: http://158.160.96.182:8000"
echo ""
echo "��о�мот� ло�ов:"
echo "  docker compose -f docker-compose.prod.yml logs -f"

