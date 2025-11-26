# Копирование скрипта на сервер

## Вариант 1: Создать скрипт прямо на сервере

Выполните на сервере:

```bash
ssh root@72.56.85.215
cd ~/facy-app

# Скачайте скрипт из GitHub
wget https://raw.githubusercontent.com/GrekEv/facy-app/main/setup_domain_onlyface.sh
chmod +x setup_domain_onlyface.sh
./setup_domain_onlyface.sh
```

## Вариант 2: Скопировать с локального компьютера

```bash
# С вашего компьютера
scp setup_domain_onlyface.sh root@72.56.85.215:~/facy-app/
ssh root@72.56.85.215 "cd ~/facy-app && chmod +x setup_domain_onlyface.sh && ./setup_domain_onlyface.sh"
```

## Вариант 3: Создать вручную на сервере

```bash
ssh root@72.56.85.215
cd ~/facy-app
nano setup_domain_onlyface.sh
# Вставьте содержимое скрипта, сохраните (Ctrl+O, Enter, Ctrl+X)
chmod +x setup_domain_onlyface.sh
./setup_domain_onlyface.sh
```

## Быстрое решение без скрипта

Если скрипт не нужен, выполните команды из `FIX_SERVER.md` вручную на сервере.

