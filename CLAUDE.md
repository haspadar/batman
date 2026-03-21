# CLAUDE.md

Этот файл содержит инструкции для Claude Code при работе с кодом в данном репозитории.

## Обзор проекта

Batman — набор скилов для Claude Code для автоматизации серверной инфраструктуры. Скилы синхронизируют общие данные через Bitwarden и управляют машинами через SSH.

## Контекст

- **Общее хранилище** — Bitwarden Organization (коллекция Acrobats/Hetzner)
- **Конфиг** — `.bw_password` (пароль Bitwarden), `.ssh_user` (логин пароль /path/to/key.pub)

## Скилы

- `/batman-install` — симлинки скилов в `~/.claude/skills/`, post-merge хук
- `/batman-bitwarden` — синхронизация серверов в Bitwarden из файла или правка одной записи
- `/batman-doctor` — аудит SSH-доступа ко всем серверам, автофикс проблем
- `/batman-sync-hosts` — синхронизация серверов из Bitwarden в `/etc/hosts` и `~/.ssh/config`
- `/batman-user` — создание пользователя, sudo, ключ на сервере
- `/batman-guest` — создание гостевого пользователя (пароль, без ключей и sudo)
- `/bw-secret` — управление секретами в Bitwarden (Secure Note)

## Зависимости

- `bw` (Bitwarden CLI) — `brew install bitwarden-cli`
- `sshpass` — `brew install sshpass`
