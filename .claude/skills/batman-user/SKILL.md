# Скил `batman-user`

Создание и настройка SSH-пользователя на серверах Hetzner.

Конфиг пользователя берётся из `/Users/haspadar/Projects/batman/.ssh_user`:
```
логин пароль /path/to/key.pub
```

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

### Все серверы
```bash
python3 /Users/haspadar/Projects/batman/scripts/list-servers.py | python3 /Users/haspadar/Projects/batman/scripts/setup-user.py
```

### Конкретные серверы
```bash
echo "root_pass hostname ip" | python3 /Users/haspadar/Projects/batman/scripts/setup-user.py
```

Скрипт выполняет на каждом сервере:
1. Создаёт юзера (если не существует)
2. Добавляет в sudo + sudoers.d
3. Прописывает SSH-ключ в authorized_keys
4. Проверяет подключение по ключу

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
