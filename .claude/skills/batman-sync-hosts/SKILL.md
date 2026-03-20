# Скил `batman-sync-hosts`

Синхронизация серверов из Bitwarden в `/etc/hosts`.

## Шаг 1 — Получить список серверов из Bitwarden

Разблокировка:
```
bw unlock --passwordfile /Users/haspadar/Projects/batman/.bw_password --raw
```

Синк и получение записей из коллекции:
```
bw sync
bw list items --collectionid a879e149-9510-4fbe-9644-b41300e6a521
```

Для каждой записи взять:
- `name` → hostname
- `login.uris[0].uri` → ip

Пропусти записи без ip или без hostname.

## Шаг 2 — Сформировать блок для /etc/hosts

Собери строки в формате `ip hostname` и оберни в маркеры:

```
# batman begin
116.203.102.213 autode-master
159.69.159.91   danon
# batman end
```

## Шаг 3 — Обновить /etc/hosts

Прочитай текущий `/etc/hosts`. Найди блок между `# batman begin` и `# batman end`.

- Если блок есть — замени его целиком на новый.
- Если блока нет — добавь в конец файла.

Запись через `sudo tee`:
```bash
sudo tee /etc/hosts <<'EOF'
<полное содержимое файла с новым блоком>
EOF
```

## Шаг 4 — Итог

Выведи что изменилось:
```
✓ добавлен:   new-server      1.2.3.4
~ без изменений: autode-master   116.203.102.213
✗ удалён:     old-server      5.6.7.8

Итого: 18 записей в /etc/hosts
```
