# Скил `batman-guest`

Создание гостевого пользователя на серверах — только с паролем, без SSH-ключей и без sudo.

Конфиг берётся из `/Users/haspadar/Projects/batman/.ssh_guest`:
```
логин пароль
```

Перед началом проверь наличие файла:
```bash
cat /Users/haspadar/Projects/batman/.ssh_guest
```
Если файл отсутствует или пуст — выведи:
```
✗ .ssh_guest не найден. Создай файл: echo "логин пароль" > .ssh_guest
```
И останови выполнение.

## Определение сценария

### Сценарий А — Конкретный сервер
Признаки: передан hostname или список hostname'ов.

Выполнить настройку только на указанных серверах.

### Сценарий Б — Все серверы
Признаки: передано «все» или ничего не передано.

Спроси: **"Создать гостевого пользователя на всех серверах?"**

## Алгоритм настройки на каждом сервере

### Все серверы
```bash
python3 /Users/haspadar/Projects/batman/scripts/list-servers.py | python3 /Users/haspadar/Projects/batman/scripts/setup-guest.py
```

### Конкретные серверы
Передай только нужные строки в `setup-guest.py` (формат: `root_password hostname ip`):
```bash
echo "root_pass hostname ip" | python3 /Users/haspadar/Projects/batman/scripts/setup-guest.py
```

## Вывод

```
✓ создан    autode-master   116.203.102.213
✓ обновлён  chilo-master    5.161.201.61
✗ FAIL      danon           159.69.159.91   ошибка: ...

Итого: 2/3 настроены
```

## Технические детали

- Конфиг гостя: `/Users/haspadar/Projects/batman/.ssh_guest`
- Скрипт проверки: `/Users/haspadar/Projects/batman/scripts/check-guest.py`
- BW разблокировка: `bw unlock --passwordfile /Users/haspadar/Projects/batman/.bw_password --raw`
- Коллекция: `a879e149-9510-4fbe-9644-b41300e6a521`
