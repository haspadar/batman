#!/usr/bin/env python3
"""
Создание/обновление гостевого пользователя на серверах.

Читает конфиг из .ssh_guest (логин пароль),
серверы из stdin в формате: root_password hostname ip

Использование:
  echo "root_pass hostname ip" | python3 setup-guest.py
  python3 list-servers.py | python3 setup-guest.py
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


def setup_guest(hostname, ip, root_password, login, password):
    cmd = (
        f"bash -c \"if id '{login}' >/dev/null 2>&1; then "
        f"printf '{login}:{password}\\n' | chpasswd && echo updated; "
        f"else useradd -m -s /bin/bash '{login}' && "
        f"printf '{login}:{password}\\n' | chpasswd && echo created; fi\""
    )
    try:
        result = subprocess.run(
            ['sshpass', '-p', root_password, 'ssh',
             '-o', 'ConnectTimeout=10',
             '-o', 'BatchMode=no',
             '-o', 'StrictHostKeyChecking=no',
             '-o', 'PasswordAuthentication=yes',
             f'root@{ip}', cmd],
            capture_output=True, text=True, timeout=20
        )
        output = result.stdout.strip()
        if 'created' in output:
            return 'CREATED'
        elif 'updated' in output:
            return 'UPDATED'
        else:
            error = result.stderr.strip() or output or 'неизвестная ошибка'
            return ('ERROR', error)
    except subprocess.TimeoutExpired:
        return ('ERROR', 'timeout')
    except Exception as e:
        return ('ERROR', str(e))


def main():
    try:
        login, password = parse_ssh_guest(SSH_GUEST_FILE)
    except FileNotFoundError:
        print("✗ .ssh_guest не найден. Создай файл: echo \"логин пароль\" > .ssh_guest", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Ошибка чтения .ssh_guest: {e}", file=sys.stderr)
        sys.exit(1)

    text = sys.stdin.read()
    servers = parse_servers(text)
    if not servers:
        print("Нет данных для настройки.", file=sys.stderr)
        sys.exit(1)

    ok = 0
    fail = 0

    for hostname, ip, root_password in servers:
        status = setup_guest(hostname, ip, root_password, login, password)
        if status == 'CREATED':
            print(f"✓ создан    {hostname:<25} {ip}")
            ok += 1
        elif status == 'UPDATED':
            print(f"✓ обновлён  {hostname:<25} {ip}")
            ok += 1
        else:
            _, error = status
            print(f"✗ FAIL      {hostname:<25} {ip:<20}  {error[:60]}")
            fail += 1

    print(f"\nИтого: {ok}/{len(servers)} настроены")


if __name__ == '__main__':
    main()
