#!/usr/bin/env python3
"""
Проверка SSH-доступа к серверам.

Использование:
  echo "password hostname ip" | python3 check-ssh.py

Формат строки: пароль hostname ip
"""

import subprocess
import sys


def parse_servers(text):
    servers = []
    for line in text.splitlines():
        # Strip emojis and non-ASCII
        line = line.encode('ascii', 'ignore').decode()
        parts = line.strip().split()
        if len(parts) == 3:
            password, hostname, ip = parts
            servers.append((hostname, ip, password))
    return servers


def check_ssh(hostname, ip, password):
    try:
        result = subprocess.run(
            ['sshpass', '-p', password, 'ssh',
             '-o', 'ConnectTimeout=5',
             '-o', 'BatchMode=no',
             '-o', 'StrictHostKeyChecking=no',
             '-o', 'PasswordAuthentication=yes',
             f'root@{ip}', 'echo OK'],
            capture_output=True, text=True, timeout=10
        )
        if result.stdout.strip() == 'OK':
            return 'OK'
        err = result.stderr
        if 'Permission denied' in err or 'Authentication failed' in err:
            return 'AUTH_FAIL'
        if 'Connection refused' in err:
            return 'REFUSED'
        return 'UNREACHABLE'
    except subprocess.TimeoutExpired:
        return 'TIMEOUT'


def main():
    text = sys.stdin.read()

    servers = parse_servers(text)
    if not servers:
        print("Нет данных для проверки. Формат: пароль hostname ip", file=sys.stderr)
        sys.exit(1)

    results = []
    for hostname, ip, password in servers:
        status = check_ssh(hostname, ip, password)
        icon = '✓' if status == 'OK' else '✗'
        print(f"{icon} {status:<12} {hostname:<25} {ip}")
        results.append(status)

    ok = results.count('OK')
    print(f"\nИтого: {ok}/{len(results)} доступны")


if __name__ == '__main__':
    main()
