#!/usr/bin/env python3
"""
Проверка SSH-входа по ключу для пользователя из .ssh_user.

Использование:
  echo "hostname ip" | python3 check-key.py

Формат входных данных: hostname ip  (root_password не нужен, можно передать 3 поля — третье игнорируется)
Формат .ssh_user: логин пароль /path/to/key.pub
"""

import subprocess
import sys
import os

SSH_USER_FILE = os.path.join(os.path.dirname(__file__), '..', '.ssh_user')


def parse_ssh_user(path):
    for line in open(path):
        parts = line.strip().split()
        if len(parts) == 3:
            login, password, key_path = parts
            key_path = key_path.replace('.pub', '')
            return login, key_path
    raise ValueError(f"Неверный формат {path}. Ожидается: логин пароль /path/to/key.pub")


def parse_servers(text):
    servers = []
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            hostname, ip = parts[0], parts[1]
            servers.append((hostname, ip))
    return servers


def check_key(hostname, ip, login, key_path):
    try:
        result = subprocess.run(
            ['ssh',
             '-i', key_path,
             '-o', 'BatchMode=yes',
             '-o', 'ConnectTimeout=5',
             '-o', 'StrictHostKeyChecking=no',
             '-o', 'PasswordAuthentication=no',
             f'{login}@{ip}', 'echo OK'],
            capture_output=True, text=True, timeout=10
        )
        if result.stdout.strip() == 'OK':
            return 'OK'
        err = result.stderr
        if 'Permission denied' in err:
            return 'NO_KEY'
        if 'Connection refused' in err:
            return 'REFUSED'
        return 'UNREACHABLE'
    except subprocess.TimeoutExpired:
        return 'TIMEOUT'


def main():
    try:
        login, key_path = parse_ssh_user(SSH_USER_FILE)
    except Exception as e:
        print(f"Ошибка чтения .ssh_user: {e}", file=sys.stderr)
        sys.exit(1)

    text = sys.stdin.read()

    servers = parse_servers(text)
    if not servers:
        print("Нет данных для проверки. Формат: hostname ip", file=sys.stderr)
        sys.exit(1)

    print(f"Проверка входа по ключу '{key_path}' (user: {login}) на {len(servers)} серверах...\n")

    results = []
    for hostname, ip in servers:
        status = check_key(hostname, ip, login, key_path)
        icon = '✓' if status == 'OK' else '✗'
        print(f"{icon} {status:<12} {hostname:<25} {ip}")
        results.append(status)

    ok = results.count('OK')
    no_key = results.count('NO_KEY')
    print(f"\nИтого: {ok}/{len(results)} OK | {no_key} без ключа — запусти /batman-user")


if __name__ == '__main__':
    main()
