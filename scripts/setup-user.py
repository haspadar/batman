#!/usr/bin/env python3
"""
Создание/настройка SSH-пользователя на серверах.

Читает конфиг из .ssh_user (логин пароль /path/to/key.pub),
серверы из stdin в формате: root_password hostname ip

Использование:
  echo "root_pass hostname ip" | python3 setup-user.py
  python3 list-servers.py | python3 setup-user.py
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
         '-o', 'ConnectTimeout=10',
         '-o', 'BatchMode=no',
         '-o', 'StrictHostKeyChecking=no',
         '-o', 'PasswordAuthentication=yes',
         f'{user}@{ip}', command],
        capture_output=True, text=True, timeout=20
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def setup_user(hostname, ip, root_password, login, password, pub_key_path):
    try:
        pub_key = open(pub_key_path).read().strip()
    except Exception as e:
        return ('ERROR', f"не удалось прочитать ключ: {e}")

    try:
        # Создать юзера если не существует
        _, out, _ = ssh_run(ip, root_password,
            f"bash -c \"id '{login}' >/dev/null 2>&1 && echo EXISTS || (useradd -m -s /bin/bash '{login}' && printf '{login}:{password}\\n' | chpasswd && echo CREATED)\"")
        if 'CREATED' not in out and 'EXISTS' not in out:
            return ('ERROR', out or 'useradd failed')

        # Добавить в sudo
        ssh_run(ip, root_password,
            f"bash -c \"usermod -aG sudo '{login}' 2>/dev/null || usermod -aG wheel '{login}'; "
            f"echo '{login} ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/{login}; "
            f"chmod 440 /etc/sudoers.d/{login}\"")

        # Прописать SSH-ключ
        escaped_key = pub_key.replace('"', '\\"')
        ssh_run(ip, root_password,
            f"bash -c \""
            f"mkdir -p /home/{login}/.ssh && "
            f"chmod 700 /home/{login}/.ssh && "
            f"grep -qF \\\"{escaped_key}\\\" /home/{login}/.ssh/authorized_keys 2>/dev/null || "
            f"echo \\\"{escaped_key}\\\" >> /home/{login}/.ssh/authorized_keys && "
            f"chmod 600 /home/{login}/.ssh/authorized_keys && "
            f"chown -R {login}:{login} /home/{login}/.ssh"
            f"\"")

        # Проверить подключение по ключу
        private_key = pub_key_path.removesuffix('.pub')
        result = subprocess.run(
            ['ssh',
             '-o', 'ConnectTimeout=5',
             '-o', 'StrictHostKeyChecking=no',
             '-o', 'BatchMode=yes',
             '-o', 'PasswordAuthentication=no',
             '-i', private_key,
             f'{login}@{ip}', 'echo OK'],
            capture_output=True, text=True, timeout=15
        )
        if 'OK' in result.stdout:
            return ('OK',)
        else:
            return ('ERROR', f"ключ не работает: {result.stderr.strip()[:60]}")

    except subprocess.TimeoutExpired:
        return ('ERROR', 'timeout')
    except Exception as e:
        return ('ERROR', str(e))


def main():
    try:
        login, password, key_path = parse_ssh_user(SSH_USER_FILE)
    except FileNotFoundError:
        print("✗ .ssh_user не найден. Создай файл: echo \"логин пароль /path/to/key.pub\" > .ssh_user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Ошибка чтения .ssh_user: {e}", file=sys.stderr)
        sys.exit(1)

    text = sys.stdin.read()
    servers = parse_servers(text)
    if not servers:
        print("Нет данных для настройки.", file=sys.stderr)
        sys.exit(1)

    ok = 0
    fail = 0

    for hostname, ip, root_password in servers:
        status = setup_user(hostname, ip, root_password, login, password, key_path)
        if status[0] == 'OK':
            print(f"✓ OK        {hostname:<25} {ip}")
            ok += 1
        else:
            error = status[1] if len(status) > 1 else 'неизвестная ошибка'
            print(f"✗ FAIL      {hostname:<25} {ip:<20}  {error}")
            fail += 1

    print(f"\nИтого: {ok}/{len(servers)} настроены")


if __name__ == '__main__':
    main()
