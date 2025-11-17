# 🔧 Решение проблемы SSH: Permission denied (publickey)

## Проблема: Ключ добавлен, но подключение не работает

Если вы видите ключ в метаданных ВМ, но подключение не работает, попробуйте следующие решения:

## ✅ Решение 1: Проверьте правильность ключа

**На вашем Mac проверьте ключ:**

```bash
cat ~/.ssh/id_rsa.pub
```

**Убедитесь, что этот же ключ добавлен в ВМ:**
- Откройте ВМ в консоли Яндекс.Облака
- Перейдите в раздел "Метаданные"
- Проверьте значение `ssh-keys` - должно начинаться с `ubuntu:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDP0ygn...`

## ✅ Решение 2: Перезагрузите ВМ

**В консоли Яндекс.Облака:**

1. Откройте вашу ВМ
2. Нажмите кнопку **"Остановить"** (Stop)
3. Подождите остановки (1-2 минуты)
4. Нажмите **"Запустить"** (Start)
5. Подождите запуска (1-2 минуты)
6. Попробуйте подключиться снова

## ✅ Решение 3: Добавьте ключ через редактирование ВМ

**В консоли Яндекс.Облака:**

1. Откройте вашу ВМ
2. Нажмите кнопку **"Изменить ВМ"** (Edit VM) в правой панели
3. Прокрутите до раздела **"Доступ"** (Access)
4. Найдите поле **"SSH-ключ"** (SSH key)
5. Удалите старый ключ (если есть)
6. Нажмите **"Добавить ключ"**
7. Вставьте ваш ключ:

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDP0ygn/Ga+V3AmuxO5oAYOd0gcFEWovDRwqVf3DUlvP/N5BLP7E3BZ4JH2mm3kNQBq0/WehX9PcwzirQMNvChvuo7D6fA7VAuld1oT42ZhVSk2mEzRSO3klH3YWzwOyWropCCHxWhxv+yYW7ELZYdHfuvMi2r/gAYlR1kh4fYkd6HOr/0HimrMx16tBy8m98+0UJTKMinc1tlWlvOp+g3MnnPJFK4WWLq43xonLohY9NNq0ZZjSi5ws9xa551t197YvPw8Vn4ZUAuQaortDiXBuSeEI8KFXYpGgMj9E7S3g4Oo6sGx10qYH4C0dsABVrE4Aqm+smHbzaHQNQM0XLZg+x7kMiTlqA3gJqx6hYjPO9cbwRV9O71q0J4tGsA409poUn4MHweyD0x0cJglfpLnF6kvl2QDGPkrWiyybD53czv+h7ZMf73llObjOyN0p1ER+8/LdNWmHUSRNn0otO1xPdGRZe3rkXApozrfR9fBtR0yIGLMQ7gNothh8Jv05fm1kLYzJFCFaIFYEWxcSiRIByQUdD73R7uPRiNlQ7SKzDX7oAXebYdAxeCGfi3yv6d/gAHKMybPE5nexYB/QXvkDvw8qFVcDnogB4dALVlQGtPB9zcH3gJdSscA2R3WA+bTe1rdYNkaXIUblcfyNX5BGSGNrXjpV7MqD02oawxePQ== kirilldeniushkin@Mac-mini-Kirill.local
```

8. Нажмите **"Сохранить"** внизу страницы
9. Подождите 2-3 минуты

## ✅ Решение 4: Используйте серийную консоль (временное решение)

**В консоли Яндекс.Облака:**

1. Откройте вашу ВМ
2. В левом меню найдите **"Серийная консоль"** (Serial console)
3. Нажмите на неё
4. Вы сможете подключиться без SSH ключа
5. Через серийную консоль добавьте ваш ключ вручную:

```bash
# В серийной консоли выполните:
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDP0ygn/Ga+V3AmuxO5oAYOd0gcFEWovDRwqVf3DUlvP/N5BLP7E3BZ4JH2mm3kNQBq0/WehX9PcwzirQMNvChvuo7D6fA7VAuld1oT42ZhVSk2mEzRSO3klH3YWzwOyWropCCHxWhxv+yYW7ELZYdHfuvMi2r/gAYlR1kh4fYkd6HOr/0HimrMx16tBy8m98+0UJTKMinc1tlWlvOp+g3MnnPJFK4WWLq43xonLohY9NNq0ZZjSi5ws9xa551t197YvPw8Vn4ZUAuQaortDiXBuSeEI8KFXYpGgMj9E7S3g4Oo6sGx10qYH4C0dsABVrE4Aqm+smHbzaHQNQM0XLZg+x7kMiTlqA3gJqx6hYjPO9cbwRV9O71q0J4tGsA409poUn4MHweyD0x0cJglfpLnF6kvl2QDGPkrWiyybD53czv+h7ZMf73llObjOyN0p1ER+8/LdNWmHUSRNn0otO1xPdGRZe3rkXApozrfR9fBtR0yIGLMQ7gNothh8Jv05fm1kLYzJFCFaIFYEWxcSiRIByQUdD73R7uPRiNlQ7SKzDX7oAXebYdAxeCGfi3yv6d/gAHKMybPE5nexYB/QXvkDvw8qFVcDnogB4dALVlQGtPB9zcH3gJdSscA2R3WA+bTe1rdYNkaXIUblcfyNX5BGSGNrXjpV7MqD02oawxePQ== kirilldeniushkin@Mac-mini-Kirill.local" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

После этого попробуйте подключиться через SSH снова.

## ✅ Решение 5: Проверьте группы безопасности

**Убедитесь, что порт 22 открыт:**

1. В консоли Яндекс.Облака: **"Virtual Private Cloud"** → **"Группы безопасности"**
2. Найдите группу `default-sg-enphh0lu4156jbt957h1` (из метаданных ВМ)
3. Проверьте, что есть правило для порта 22 (SSH)
4. Если нет - добавьте:
   - Направление: Входящий трафик
   - Протокол: TCP
   - Порт: 22
   - Источник: 0.0.0.0/0 (или ваш IP)

## 🔍 Диагностика

**Проверьте подключение с подробным выводом:**

```bash
ssh -v ubuntu@158.160.96.182
```

**Проверьте доступность порта:**

```bash
nc -zv 158.160.96.182 22
```

## 💡 Рекомендация

Попробуйте **Решение 3** (добавить ключ через редактирование ВМ) - это самый надежный способ.


