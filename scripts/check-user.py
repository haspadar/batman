#!/usr/bin/env python3
"""
Проверка наличия SSH-пользователя на серверах.

Читает конфиг пользователя из .ssh_user (логин пароль путь_к_ключу),
проверяет каждый сервер: существует ли юзер, есть ли sudo, прописан ли ключ.

Использование:
  python3 check-user.py servers.txt
  echo "root_password hostname ip" | python3 check-user.py
  cat servers.txt | python3 check-user.py

Формат servers.txt: root_пароль hostname ip
Формат .ssh_user:   логин пароль /path/to/key.pub
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
            return login, password, key_path
    raise ValueError(f"Неверный формат {path}. Ожидается: логин пароль /path/to/key.pub")


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


def check_user(hostname, ip, root_password, login, pub_key_path):
    try:
        # Проверить существует ли юзер
        rc, out, _ = ssh_run(ip, root_password, f'id {login} 2>/dev/null && echo EXISTS || echo MISSING')
        if 'MISSING' in out:
            return ('MISSING', hostname, ip)

        # Проверить sudo
        rc, out, _ = ssh_run(ip, root_password, f'groups {login}')
        has_sudo = 'sudo' in out or 'wheel' in out

        # Проверить SSH-ключ
        pub_key = open(pub_key_path).read().strip()
        rc, out, _ = ssh_run(ip, root_password, f'cat /home/{login}/.ssh/authorized_keys 2>/dev/null || echo ""')
        has_key = pub_key in out

        if has_sudo and has_key:
            return ('OK', hostname, ip)
        elif not has_sudo and not has_key:
            return ('NO_SUDO+NO_KEY', hostname, ip)
        elif not has_sudo:
            return ('NO_SUDO', hostname, ip)
        else:
            return ('NO_KEY', hostname, ip)

    except subprocess.TimeoutExpired:
        return ('TIMEOUT', hostname, ip)
    except Exception as e:
        return ('ERROR', hostname, ip)


def main():
    try:
        login, password, key_path = parse_ssh_user(SSH_USER_FILE)
    except Exception as e:
        print(f"Ошибка чтения .ssh_user: {e}", file=sys.stderr)
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
        status, h, i = check_user(hostname, ip, root_password, login, key_path)
        icon = '✓' if status == 'OK' else '✗'
        print(f"{icon} {status:<16} {h:<25} {i}")
        results.append(status)

    ok = results.count('OK')
    missing = results.count('MISSING')
    print(f"\nИтого: {ok}/{len(results)} настроены | {missing} отсутствуют")


if __name__ == '__main__':
    main()
