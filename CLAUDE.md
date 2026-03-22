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
- `/batman-kick` — удаление пользователя с серверов
- `/batman-secret` — управление секретами в Bitwarden (Secure Note)

## Скрипты

- `scripts/list-servers.py` — список серверов из Bitwarden (в pipe: `пароль hostname ip`, в терминале: цвета)
- `scripts/server.py <hostname>` — реквизиты сервера: `export SSH_*` или `--json`
- `scripts/setup-user.py` — создать/настроить SSH-юзера (sudo + ключ). Stdin: `пароль hostname ip`
- `scripts/delete-user.py <login>` — удалить пользователя. Stdin: `пароль hostname ip`
- `scripts/amnesia.py` — вывести все серверы с реквизитами в цвете
- `scripts/check-ssh.py` — проверка root SSH по паролю
- `scripts/check-user.py` — проверка юзера, sudo, ключа
- `scripts/check-key.py` — проверка входа по ключу
- `scripts/sync-bitwarden.py` — синк `actual.txt` → Bitwarden
- `scripts/db-creds.py <hostname>` — получить DB_USER и DB_PASSWORD с сервера через SSH

## Зависимости

- `bw` (Bitwarden CLI) — `brew install bitwarden-cli`
- `sshpass` — `brew install sshpass`
