#!/usr/bin/env python3
"""
Получение DB_USER и DB_PASSWORD с удалённого сервера через SSH.

Читает логин/ключ из .ssh_user, IP — из Bitwarden по hostname.
Выполняет grep на сервере и выводит пары KEY=value.

Использование:
  python3 scripts/db-creds.py apola-master
"""

import subprocess
import json
import sys
import os

BW_PASSWORD_FILE = os.path.join(os.path.dirname(__file__), '..', '.bw_password')
SSH_USER_FILE = os.path.join(os.path.dirname(__file__), '..', '.ssh_user')
COLLECTION_ID = 'a879e149-9510-4fbe-9644-b41300e6a521'
ENV_PATH = '/var/www/palto/configs/.env.local'


def parse_ssh_user(path):
    for line in open(path):
        parts = line.strip().split()
        if len(parts) == 3:
            login, password, key_path = parts
            return login, password, key_path
    raise ValueError(f"Неверный формат {path}. Ожидается: логин пароль /path/to/key.pub")


def main():
    if len(sys.argv) != 2:
        print(f"Использование: {sys.argv[0]} <hostname>", file=sys.stderr)
        sys.exit(1)

    hostname = sys.argv[1]

    try:
        login, password, key_pub = parse_ssh_user(SSH_USER_FILE)
    except Exception as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)

    private_key = key_pub.removesuffix('.pub')

    result = subprocess.run(
        ['bw', 'unlock', '--passwordfile', BW_PASSWORD_FILE, '--raw'],
        capture_output=True, text=True
    )
    session = result.stdout.strip()
    if not session:
        print(f"✗ Не удалось разблокировать Bitwarden: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        ['bw', 'list', 'items', '--collectionid', COLLECTION_ID],
        capture_output=True, text=True,
        env={**os.environ, 'BW_SESSION': session}
    )
    items = json.loads(result.stdout)

    ip = None
    for item in items:
        if item.get('name') == hostname:
            uris = item.get('login', {}).get('uris', [])
            ip = uris[0].get('uri', '') if uris else ''
            break

    if not ip:
        print(f"✗ Сервер '{hostname}' не найден в Bitwarden или IP отсутствует", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        [
            'ssh', '-i', private_key,
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'BatchMode=yes',
            f'{login}@{ip}',
            f"grep -E '^DB_(USER|PASSWORD)' {ENV_PATH}"
        ],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"✗ SSH ошибка: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    for line in result.stdout.splitlines():
        if '=' not in line:
            continue
        key, _, value = line.partition('=')
        value = value.strip().strip("'").strip('"')
        print(f"{key}={value}")


if __name__ == '__main__':
    main()
