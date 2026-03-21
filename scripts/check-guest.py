#!/usr/bin/env python3
"""
Проверка наличия гостевого пользователя на серверах.

Читает конфиг из .ssh_guest (логин пароль),
проверяет каждый сервер: существует ли юзер.

Использование:
  python3 check-guest.py servers.txt
  echo "root_password hostname ip" | python3 check-guest.py
  cat servers.txt | python3 check-guest.py

Формат servers.txt: root_пароль hostname ip
Формат .ssh_guest:  логин пароль
"""

import subprocess
import sys
import os

SSH_GUEST_FILE = os.path.join(os.path.dirname(__file__), '..', '.ssh_guest')


def parse_ssh_guest(path):
    for line in open(path):
        parts = line.strip().split()
        if len(parts) == 2:
            login, password = parts
            return login, password
    raise ValueError(f"Неверный формат {path}. Ожидается: логин пароль")


def parse_servers(text):
    servers = []
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) == 3:
            root_password, hostname, ip = parts
            servers.append((hostname, ip, root_password))
    return servers


def ssh_run(ip, password, command, user='root'):
    result = subprocess.run(
        ['sshpass', '-p', password, 'ssh',
         '-o', 'ConnectTimeout=5',
         '-o', 'BatchMode=no',
         '-o', 'StrictHostKeyChecking=no',
         '-o', 'PasswordAuthentication=yes',
         f'{user}@{ip}', command],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def check_guest(hostname, ip, root_password, login):
    try:
        rc, out, _ = ssh_run(ip, root_password, f'id {login} 2>/dev/null && echo EXISTS || echo MISSING')
        if 'MISSING' in out:
            return ('MISSING', hostname, ip)
        return ('OK', hostname, ip)

    except subprocess.TimeoutExpired:
        return ('TIMEOUT', hostname, ip)
    except Exception:
        return ('ERROR', hostname, ip)


def main():
    try:
        login, password = parse_ssh_guest(SSH_GUEST_FILE)
    except Exception as e:
        print(f"Ошибка чтения .ssh_guest: {e}", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    servers = parse_servers(text)
    if not servers:
        print("Нет данных для проверки.", file=sys.stderr)
        sys.exit(1)

    print(f"Проверка пользователя '{login}' на {len(servers)} серверах...\n")

    results = []
    for hostname, ip, root_password in servers:
        status, h, i = check_guest(hostname, ip, root_password, login)
        icon = '✓' if status == 'OK' else '✗'
        print(f"{icon} {status:<16} {h:<25} {i}")
        results.append(status)

    ok = results.count('OK')
    missing = results.count('MISSING')
    print(f"\nИтого: {ok}/{len(results)} существуют | {missing} отсутствуют")


if __name__ == '__main__':
    main()
