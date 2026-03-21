# Скил `batman-kick`

Удаление пользователя с серверов.

Конфиг логина берётся из аргумента. Если не передан — спроси: **"Какого пользователя удалить?"**

## Определение сценария

### Сценарий А — Конкретный сервер
Признаки: передан hostname или список hostname'ов.

### Сценарий Б — Все серверы
Признаки: передано «все» или ничего не передано.

Спроси: **"Удалить пользователя <login> на всех серверах?"**

## Алгоритм

### Все серверы
```bash
python3 /Users/haspadar/Projects/batman/scripts/list-servers.py | python3 /Users/haspadar/Projects/batman/scripts/delete-user.py <login>
```

### Конкретные серверы
```bash
echo "root_pass hostname ip" | python3 /Users/haspadar/Projects/batman/scripts/delete-user.py <login>
```

## Вывод

```
✓ удалён    danon                     159.69.159.91
  нет       dumin                     116.203.114.225
✗ FAIL      dadyr                     157.180.116.92       timeout

Итого: 2/3 обработано
```
