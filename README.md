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
| `.ssh_user` | `логин пароль /path/to/key.pub` | Акробат, его пароль и пропуск за кулисы |

Файлы в `.gitignore`. Если ключ не существует — создастся автоматически при первом `/batman-doctor`.

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

### `/batman-kick`
Удаляет пользователя с серверов.

```
/batman-kick guest         # удалить на всех серверах
/batman-kick guest dumin   # удалить на конкретном сервере
```

### `/batman-secret`
Управление секретами в Bitwarden (Secure Note). Namespace определяется по имени проекта из `git remote`.

```
/batman-secret get <key>           # прочитать секрет
/batman-secret set <key> <value>   # создать или обновить
/batman-secret delete <key>        # удалить
```

## Скрипты

| Скрипт | Что делает |
|--------|------------|
| `scripts/list-servers.py` | Список серверов из Bitwarden. В терминале — с цветами и паролями, в pipe — `пароль hostname ip` |
| `scripts/server.py` | Реквизиты конкретного сервера по hostname. Stdout: `export SSH_*` или `--json` |
| `scripts/setup-user.py` | Создать/настроить SSH-юзера (sudo + ключ). Stdin: `пароль hostname ip` |
| `scripts/delete-user.py` | Удалить пользователя. Аргумент: логин. Stdin: `пароль hostname ip` |
| `scripts/check-ssh.py` | Root SSH по паролю. Stdin: `пароль hostname ip` |
| `scripts/check-user.py` | Пользователь, sudo, ключ. Stdin: `пароль hostname ip` |
| `scripts/check-key.py` | Вход по ключу. Stdin: `hostname ip` |
| `scripts/sync-bitwarden.py` | Синк `actual.txt` → Bitwarden. Есть `--dry-run` |

### Примеры

```bash
# Список всех серверов
python3 scripts/list-servers.py

# Реквизиты конкретного сервера
eval $(python3 scripts/server.py danon)
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST

# Настроить SSH-юзера на конкретном сервере
echo "root_pass hostname ip" | python3 scripts/setup-user.py
```

## Зависимости

- `bw` — Bitwarden CLI: `brew install bitwarden-cli`
- `sshpass`: `brew install sshpass`
