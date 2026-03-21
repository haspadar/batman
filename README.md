# Batman

Снаряжение для акробатов. Помогает держать серверную труппу в форме — синхронизирует реквизит, раздаёт ключи, проверяет готовность к выступлению.

## Быстрый старт

```bash
# 1. Создать .bw_password
echo "твой_пароль_bitwarden" > .bw_password

# 2. Создать .ssh_user
echo "логин пароль /path/to/key.pub" > .ssh_user

# 3. Установить снаряжение
/batman-install
```

## Конфиг-файлы

| Файл | Формат | Назначение |
|------|--------|------------|
| `.bw_password` | строка | Пароль для разблокировки Bitwarden CLI |
| `.ssh_user` | `логин пароль /path/to/key.pub [nosudo]` | Акробат, его пароль и пропуск за кулисы |

Оба файла в `.gitignore`. Если ключ не существует — создастся автоматически при первом `/batman-doctor`.

## Скилы

### `/batman-install`
Создаёт симлинки всех `batman-*` скилов в `~/.claude/skills/` — после этого они доступны глобально во всех проектах. Устанавливает post-merge хук: новые скилы подхватываются автоматически после `git pull`.

### `/batman-bitwarden`
Синхронизирует серверы в Bitwarden — общий реестр труппы:
- из файла в формате `пароль hostname ip` (сначала dry-run, потом подтверждение)
- или правка одной записи: добавить / обновить / удалить

### `/batman-doctor`
Аудит SSH-доступа ко всем серверам из Bitwarden. Проходит по шагам:

1. Проверяет `.bw_password` и `.ssh_user` — если ключа нет, создаёт автоматически
2. Получает список серверов из Bitwarden
3. Проверяет root SSH-доступ по паролю для каждого сервера
4. Проверяет наличие пользователя, sudo и ключа — если не настроен, предлагает `/batman-user`
5. Проверяет вход по ключу — если не работает, запускает `/batman-user` автоматически
6. Сверяет `/etc/hosts` с Bitwarden — если расхождения, синкает сам
7. По недоступным серверам спрашивает: удалить или обновить данные в Bitwarden

### `/batman-sync-hosts`
Синхронизирует серверы из Bitwarden в локальные файлы:

- `/etc/hosts` — batman-блок `ip hostname` между маркерами `# batman begin` / `# batman end`
- `~/.ssh/config` — batman-блок со всеми хостами и настройками ключа

Ручные записи не трогает.

### `/batman-user`
Выписывает пропуск акробату на сервер: создаёт пользователя, даёт sudo, прописывает ключ, проверяет вход.

```
/batman-user dumin         # конкретный сервер
/batman-user               # спросит сам
```

### `/bw-secret`
Управление секретами в Bitwarden (Secure Note). Namespace определяется по имени проекта из `git remote`.

```
/bw-secret get <key>           # прочитать секрет
/bw-secret set <key> <value>   # создать или обновить
/bw-secret delete <key>        # удалить
```

## Скрипты

| Скрипт | Что делает |
|--------|------------|
| `scripts/check-ssh.py` | Root SSH по паролю. Stdin: `пароль hostname ip` |
| `scripts/check-user.py` | Пользователь, sudo, ключ. Stdin: `пароль hostname ip` |
| `scripts/check-key.py` | Вход по ключу. Stdin: `hostname ip` |
| `scripts/sync-bitwarden.py` | Синк `actual.txt` → Bitwarden. Есть `--dry-run` |

## Зависимости

- `bw` — Bitwarden CLI: `brew install bitwarden-cli`
- `sshpass`: `brew install sshpass`
