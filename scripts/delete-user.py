#!/usr/bin/env python3
"""
Удаление пользователя на серверах.

Читает серверы из stdin в формате: root_password hostname ip

Использование:
  echo "root_pass hostname ip" | python3 delete-user.py <login>
  python3 list-servers.py | python3 delete-user.py <login>
"""

import subprocess
import sys
import os


def parse_servers(text):
    servers = []
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) == 3:
            root_password, hostname, ip = parts
            servers.append((hostname, ip, root_password))
    return servers


def delete_user(hostname, ip, root_password, login):
    try:
        result = subprocess.run(
            ['sshpass', '-p', root_password, 'ssh',
             '-o', 'ConnectTimeout=10',
             '-o', 'BatchMode=no',
             '-o', 'StrictHostKeyChecking=no',
             '-o', 'PasswordAuthentication=yes',
             f'root@{ip}',
             f"bash -c \"if id '{login}' >/dev/null 2>&1; then userdel -r '{login}' 2>/dev/null; echo deleted; else echo missing; fi\""],
            capture_output=True, text=True, timeout=20
        )
        output = result.stdout.strip()
        if 'deleted' in output:
            return 'DELETED'
        elif 'missing' in output:
            return 'MISSING'
        else:
            return ('ERROR', result.stderr.strip() or output or 'неизвестная ошибка')
    except subprocess.TimeoutExpired:
        return ('ERROR', 'timeout')
    except Exception as e:
        return ('ERROR', str(e))


def main():
    if len(sys.argv) != 2:
        print(f"Использование: python3 {os.path.basename(__file__)} <login>", file=sys.stderr)
        sys.exit(1)

    login = sys.argv[1]

    text = sys.stdin.read()
    servers = parse_servers(text)
    if not servers:
        print("Нет данных для обработки.", file=sys.stderr)
        sys.exit(1)

    ok = 0
    for hostname, ip, root_password in servers:
        status = delete_user(hostname, ip, root_password, login)
        if status == 'DELETED':
            print(f"✓ удалён    {hostname:<25} {ip}")
            ok += 1
        elif status == 'MISSING':
            print(f"  нет       {hostname:<25} {ip}")
            ok += 1
        else:
            _, error = status
            print(f"✗ FAIL      {hostname:<25} {ip:<20}  {error[:60]}")

    print(f"\nИтого: {ok}/{len(servers)} обработано")


if __name__ == '__main__':
    main()
