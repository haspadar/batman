# CLAUDE.md

Этот файл содержит инструкции для Claude Code при работе с кодом в данном репозитории.

## Обзор проекта

Batman — набор скилов для Claude Code для автоматизации серверной инфраструктуры. Два пользователя (haspadar и брат) работают с одними и теми же серверами Hetzner. Скилы синхронизируют общие данные через Bitwarden и управляют машинами через SSH.

## Контекст

- **haspadar** — доступ через SSH-ключи, ведёт `/etc/hosts`, использует Claude Code
- **Брат** — доступ root по паролю, использует Cursor, не ведёт `/etc/hosts`
- **Общее хранилище** — Bitwarden Organization (оба пользователя)
- **Серверы** — Hetzner

## Структура данных в Bitwarden

Серверы хранятся как Secure Notes или Login-записи с полями:
- `ip` — IP-адрес машины
- `hostname` — имя хоста для `/etc/hosts`
- `root_password` — пароль root

## Скилы

### Реализованные
- `sync-hosts` — синхронизация серверов из Bitwarden в `/etc/hosts`
- `sync-passwords` — обновление паролей в Bitwarden

### Планируемые
- Бэкапы
- Управление машиной по SSH

## Зависимости

- `bw` (Bitwarden CLI) — `brew install bitwarden-cli`
- Сессия: `export BW_SESSION=...` или `bw login` перед запуском скилов
