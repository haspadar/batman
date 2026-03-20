#!/usr/bin/env python3
"""
Синхронизация actual.txt → Bitwarden организация Acrobats, коллекция Hetzner.

actual.txt — источник правды: пароль hostname ip
- Записи из actual.txt, которых нет в BW → добавить
- Записи есть в обоих, но пароль или IP отличается → обновить
- Записи в BW, которых нет в actual.txt → удалить

Использование:
  python3 sync-bitwarden.py [--dry-run]
"""

import json
import os
import subprocess
import sys

DRY_RUN = '--dry-run' in sys.argv
ORG_NAME = 'Acrobats'
COLLECTION_NAME = 'Hetzner'
ACTUAL_FILE = 'actual.txt'
BW_PASSWORD_FILE = '.bw_password'


def bw(args, input_data=None):
    result = subprocess.run(
        ['bw'] + args,
        capture_output=True, text=True,
        input=input_data
    )
    if result.returncode != 0:
        print(f"bw error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def get_session():
    token = bw(['unlock', '--passwordfile', BW_PASSWORD_FILE, '--raw'])
    return token


def parse_actual(path):
    servers = {}
    for line in open(path):
        parts = line.strip().split()
        if len(parts) == 3:
            password, hostname, ip = parts
            servers[hostname] = {'ip': ip, 'password': password}
    return servers


def get_bw_servers(session, collection_id):
    out = subprocess.run(
        ['bw', 'list', 'items', '--collectionid', collection_id],
        capture_output=True, text=True,
        env={**os.environ, 'BW_SESSION': session}
    ).stdout
    items = json.loads(out)
    servers = {}
    for item in items:
        name = item['name']
        password = item.get('login', {}).get('password', '')
        uris = item.get('login', {}).get('uris', [])
        ip = uris[0]['uri'] if uris else ''
        servers[name] = {'ip': ip, 'password': password, 'id': item['id'], 'raw': item}
    return servers


def get_org_id(session, name):
    out = subprocess.run(
        ['bw', 'list', 'organizations'],
        capture_output=True, text=True,
        env={**os.environ, 'BW_SESSION': session}
    ).stdout
    for org in json.loads(out):
        if org['name'] == name:
            return org['id']
    return None


def get_collection_id(session, org_id, name):
    out = subprocess.run(
        ['bw', 'list', 'collections', '--organizationid', org_id],
        capture_output=True, text=True,
        env={**os.environ, 'BW_SESSION': session}
    ).stdout
    for col in json.loads(out):
        if col['name'] == name:
            return col['id']
    return None


def make_item(hostname, ip, password, org_id, collection_id, existing_raw=None):
    if existing_raw:
        item = existing_raw.copy()
    else:
        item = {
            'type': 1,
            'name': hostname,
            'login': {},
        }
    item['name'] = hostname
    item['organizationId'] = org_id
    item['collectionIds'] = [collection_id]
    item.pop('folderId', None)
    item['login'] = {
        'username': 'root',
        'password': password,
        'uris': [{'uri': ip, 'match': None}],
    }
    return item


def run_bw(args, session, input_data=None):
    result = subprocess.run(
        ['bw'] + args,
        capture_output=True, text=True,
        input=input_data,
        env={**os.environ, 'BW_SESSION': session}
    )
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}", file=sys.stderr)
        return None
    return result.stdout.strip()


def main():
    print(f"{'[DRY RUN] ' if DRY_RUN else ''}Синхронизация {ACTUAL_FILE} → Bitwarden/{ORG_NAME}/{COLLECTION_NAME}\n")

    session = get_session()
    run_bw(['sync'], session)

    org_id = get_org_id(session, ORG_NAME)
    if not org_id:
        print(f"Организация '{ORG_NAME}' не найдена в Bitwarden", file=sys.stderr)
        sys.exit(1)

    collection_id = get_collection_id(session, org_id, COLLECTION_NAME)
    if not collection_id:
        print(f"Коллекция '{COLLECTION_NAME}' не найдена в организации '{ORG_NAME}'", file=sys.stderr)
        sys.exit(1)

    actual = parse_actual(ACTUAL_FILE)
    bw_servers = get_bw_servers(session, collection_id)

    to_add = {h: v for h, v in actual.items() if h not in bw_servers}
    to_delete = {h: v for h, v in bw_servers.items() if h not in actual}
    to_update = {
        h: actual[h] for h in actual
        if h in bw_servers and (
            actual[h]['password'] != bw_servers[h]['password'] or
            actual[h]['ip'] != bw_servers[h]['ip']
        )
    }
    unchanged = {h for h in actual if h in bw_servers and h not in to_update}

    print(f"  Без изменений: {len(unchanged)}")
    print(f"  Добавить:      {len(to_add)}")
    print(f"  Обновить:      {len(to_update)}")
    print(f"  Удалить:       {len(to_delete)}\n")

    # Добавить
    for hostname, data in sorted(to_add.items()):
        print(f"  + {hostname} ({data['ip']})", end='', flush=True)
        if not DRY_RUN:
            item = make_item(hostname, data['ip'], data['password'], org_id, collection_id)
            encoded = run_bw(['encode'], session, json.dumps(item))
            if encoded:
                run_bw(['create', 'item', encoded], session)
                print(' ✓')
            else:
                print(' ✗')
        else:
            print()

    # Обновить
    for hostname, data in sorted(to_update.items()):
        old = bw_servers[hostname]
        changes = []
        if data['ip'] != old['ip']:
            changes.append(f"ip: {old['ip']} → {data['ip']}")
        if data['password'] != old['password']:
            changes.append('password изменён')
        print(f"  ~ {hostname} ({', '.join(changes)})", end='', flush=True)
        if not DRY_RUN:
            item = make_item(hostname, data['ip'], data['password'], org_id, collection_id, old['raw'])
            encoded = run_bw(['encode'], session, json.dumps(item))
            if encoded:
                run_bw(['edit', 'item', old['id'], encoded], session)
                print(' ✓')
            else:
                print(' ✗')
        else:
            print()

    # Удалить
    for hostname, data in sorted(to_delete.items()):
        print(f"  - {hostname} ({data['ip']})", end='', flush=True)
        if not DRY_RUN:
            result = run_bw(['delete', 'item', data['id']], session)
            print(' ✓' if result is not None else ' ✗')
        else:
            print()

    print('\nГотово.')


if __name__ == '__main__':
    main()
