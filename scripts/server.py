#!/usr/bin/env python3
"""
Получение реквизитов для подключения к серверу.

Читает логин/ключ из .ssh_user, IP — из Bitwarden по hostname.
Выводит переменные окружения для подстановки в shell.

Использование:
  eval $(python3 server.py danon)
  python3 server.py danon --json
"""

import subprocess
import json
import sys
import os

BW_PASSWORD_FILE = os.path.join(os.path.dirname(__file__), '..', '.bw_password')
SSH_USER_FILE = os.path.join(os.path.dirname(__file__), '..', '.ssh_user')
COLLECTION_ID = 'a879e149-9510-4fbe-9644-b41300e6a521'


def parse_ssh_user(path):
    for line in open(path):
        parts = line.strip().split()
        if len(parts) == 3:
            login, password, key_path = parts
            return login, password, key_path
    raise ValueError(f"Неверный формат {path}. Ожидается: логин пароль /path/to/key.pub")


def main():
    as_json = '--json' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]

    if len(args) != 1:
        print(f"Использование: {sys.argv[0]} <hostname> [--json]", file=sys.stderr)
        sys.exit(1)

    hostname = args[0]

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

    for item in items:
        if item.get('name') == hostname:
            uris = item.get('login', {}).get('uris', [])
            ip = uris[0].get('uri', '') if uris else ''
            if not ip:
                print(f"✗ IP не найден для {hostname}", file=sys.stderr)
                sys.exit(1)

            if as_json:
                print(json.dumps({
                    'host': ip,
                    'user': login,
                    'password': password,
                    'key': private_key,
                }))
            else:
                print(f"export SSH_HOST={ip}")
                print(f"export SSH_USER={login}")
                print(f"export SSH_PASSWORD={password}")
                print(f"export SSH_KEY={private_key}")
            sys.exit(0)

    print(f"✗ Сервер '{hostname}' не найден в Bitwarden", file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
    main()
