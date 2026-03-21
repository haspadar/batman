#!/usr/bin/env python3
"""
Вывод всех реквизитов серверов: root-логин, пароль, hostname, ip.

Использование:
  python3 amnesia.py
"""

import subprocess
import json
import sys
import os

BW_PASSWORD_FILE = os.path.join(os.path.dirname(__file__), '..', '.bw_password')
COLLECTION_ID = 'a879e149-9510-4fbe-9644-b41300e6a521'

COLORS = ['\033[36m', '\033[32m', '\033[33m', '\033[35m', '\033[34m']
BOLD = '\033[1m'
DIM = '\033[2m'
RESET = '\033[0m'


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
        login = login_data.get('username', 'root')
        password = login_data.get('password', '')
        if hostname and ip and password:
            servers.append((hostname, ip, login, password))

    servers.sort(key=lambda s: s[0])

    print(f"\n  {DIM}{'HOSTNAME':<25}  {'IP':<20}  {'LOGIN':<12}  PASSWORD{RESET}\n")
    for i, (hostname, ip, login, password) in enumerate(servers):
        color = COLORS[i % len(COLORS)]
        print(f"  {color}{BOLD}{hostname:<25}{RESET}  {ip:<20}  {DIM}{login:<12}{RESET}  {password}")
    print()


if __name__ == '__main__':
    main()
