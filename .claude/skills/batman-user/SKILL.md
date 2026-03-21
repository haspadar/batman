# Скил `batman-user`

Создание и настройка SSH-пользователя на серверах Hetzner.

Конфиг пользователя берётся из `/Users/haspadar/Projects/batman/.ssh_user`:
```
логин пароль /path/to/key.pub [nosudo]
```

4-е поле опциональное. Если указано `nosudo` — пользователь создаётся без sudo. По умолчанию (поле отсутствует) — sudo выдаётся.

## Определение сценария

### Сценарий А — Конкретный сервер
Признаки: передан hostname или список hostname'ов.

Выполнить настройку только на указанных серверах.

### Сценарий Б — Все серверы с проблемами
Признаки: вызван из `batman-doctor` со списком серверов где юзер MISSING/NO_SUDO/NO_KEY.

Выполнить настройку на всех переданных серверах.

### Сценарий В — Ничего не передано
Спроси: **"На каких серверах настроить пользователя? Укажи hostname или 'все'."**

## Алгоритм настройки на каждом сервере

Реквизиты root берутся из Bitwarden — коллекция Hetzner:
```
bw unlock --passwordfile /Users/haspadar/Projects/batman/.bw_password --raw
bw list items --collectionid a879e149-9510-4fbe-9644-b41300e6a521
```

Для каждого сервера выполнить через SSH от root:

1. **Создать юзера** (если MISSING):
```bash
useradd -m -s /bin/bash <login>
echo "<login>:<password>" | chpasswd
```

2. **Добавить в sudo** (если 4-е поле `.ssh_user` не равно `nosudo`):
```bash
usermod -aG sudo <login>
echo "<login> ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/<login>
```

3. **Прописать SSH-ключ**:
```bash
mkdir -p /home/<login>/.ssh
echo "<pub_key>" >> /home/<login>/.ssh/authorized_keys
chmod 700 /home/<login>/.ssh
chmod 600 /home/<login>/.ssh/authorized_keys
chown -R <login>:<login> /home/<login>/.ssh
```

4. **Проверить** — подключиться под новым юзером:
```
ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i <private_key> <login>@<ip> echo OK
```

## Вывод

```
✓ OK      autode-master   116.203.102.213   создан + sudo + ключ
✓ OK      chilo-master    5.161.201.61      уже существовал, добавлен ключ
✗ FAIL    danon           159.69.159.91     ошибка: ...

Итого: 2/3 настроены
```

## Технические детали

- Конфиг юзера: `/Users/haspadar/Projects/batman/.ssh_user`
- Скрипт проверки: `/Users/haspadar/Projects/batman/scripts/check-user.py`
- BW разблокировка: `bw unlock --passwordfile /Users/haspadar/Projects/batman/.bw_password --raw`
- Коллекция: `a879e149-9510-4fbe-9644-b41300e6a521`
- Приватный ключ — путь к `.pub` из `.ssh_user` без суффикса `.pub`
