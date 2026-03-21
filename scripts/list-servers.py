#!/usr/bin/env python3
"""
Получение списка серверов из Bitwarden.

Выводит в stdout строки формата: root_password hostname ip

Использование:
  python3 list-servers.py
  python3 list-servers.py | python3 setup-guest.py
"""

import subprocess
import json
import sys
import os

BW_PASSWORD_FILE = os.path.join(os.path.dirname(__file__), '..', '.bw_password')
COLLECTION_ID = 'a879e149-9510-4fbe-9644-b41300e6a521'


def bw_unlock(password_file):
    result = subprocess.run(
        ['bw', 'unlock', '--passwordfile', password_file, '--raw'],
        capture_output=True, text=True
    )
    session = result.stdout.strip()
    if not session:
        raise RuntimeError(f"Не удалось разблокировать Bitwarden: {result.stderr.strip()}")
    return session


def bw_list_items(session, collection_id):
    result = subprocess.run(
        ['bw', 'list', 'items', '--collectionid', collection_id],
        capture_output=True, text=True,
        env={**os.environ, 'BW_SESSION': session}
    )
    if result.returncode != 0:
        raise RuntimeError(f"Ошибка bw list: {result.stderr.strip()}")
    return json.loads(result.stdout)


COLORS = ['\033[36m', '\033[32m', '\033[33m', '\033[35m', '\033[34m']
RESET = '\033[0m'


def main():
    try:
        session = bw_unlock(BW_PASSWORD_FILE)
    except Exception as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)

    try:
        items = bw_list_items(session, COLLECTION_ID)
    except Exception as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)

    servers = []
    for item in items:
        hostname = item.get('name', '')
        login_data = item.get('login', {})
        uris = login_data.get('uris', [])
        ip = uris[0].get('uri', '') if uris else ''
        root_password = login_data.get('password', '')
        if hostname and ip and root_password:
            servers.append((hostname, ip, root_password))

    servers.sort(key=lambda s: s[0])

    tty = sys.stdout.isatty()
    for i, (hostname, ip, root_password) in enumerate(servers):
        if tty:
            color = COLORS[i % len(COLORS)]
            print(f"{color}{hostname:<25}{RESET}  {ip:<20}  {root_password}")
        else:
            print(f"{root_password} {hostname} {ip}")


if __name__ == '__main__':
    main()
