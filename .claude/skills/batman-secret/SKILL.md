---
name: batman-secret
description: Сохранить, прочитать или обновить секрет в Bitwarden (Secure Note)
---

Ты — помощник для управления секретами в Bitwarden через CLI.

## Usage

```
/batman-secret <operation> <key> [value]
```

Операции:
- `get <key>` — прочитать секрет
- `set <key> <value>` — создать или обновить секрет
- `delete <key>` — удалить секрет

Если аргументы не переданы — показать это usage и остановиться.

## Namespace

**Определение имени проекта:**
1. Выполни `git remote get-url origin` и возьми последний сегмент URL без `.git`
2. Если git недоступен или remote не задан — спроси пользователя
3. Полное имя записи = `<project>/<key>` (например `piqule/api_key`)
4. Папка в Bitwarden = имя проекта (например `piqule`)

## Проверка и разблокировка Bitwarden

Перед каждой операцией:

```bash
# Проверить сессию
echo $BW_SESSION
```

Если `BW_SESSION` пуст или не задан:
```bash
bw unlock
```
После вывода токена предложить пользователю:
```bash
export BW_SESSION="<токен из вывода bw unlock>"
```
Или выполнить автоматически, если пользователь согласен.

## Операция: get

```bash
# 1. Найти запись
bw list items --search "<project>/<key>" --session "$BW_SESSION"

# 2. Извлечь notes из JSON (первый результат с точным именем)
# Фильтровать по .[] | select(.name == "<project>/<key>") | .notes

# 3. Вывести значение пользователю
echo "Значение: <value>"

# 4. Предложить экспорт
echo 'Экспортировать: export <KEY>=<value>'
```

Если запись не найдена — сообщить пользователю.

## Операция: set (создать или обновить)

```bash
# 1. Найти существующую запись
bw list items --search "<project>/<key>" --session "$BW_SESSION"
```

### Если запись НЕ существует — создать:

```bash
# 1a. Проверить/создать папку
bw list folders --session "$BW_SESSION"
# Если папки с именем проекта нет:
echo '{"name":"<project>"}' | bw encode | bw create folder --session "$BW_SESSION"

# 1b. Получить ID папки
FOLDER_ID=$(bw list folders --session "$BW_SESSION" | jq -r '.[] | select(.name=="<project>") | .id')

# 1c. Создать Secure Note
bw get template item --session "$BW_SESSION" | \
  jq --arg name "<project>/<key>" \
     --arg notes "<value>" \
     --arg folderId "$FOLDER_ID" \
     '.name=$name | .notes=$notes | .folderId=$folderId | .type=2 | .secureNote={"type":0}' | \
  bw encode | \
  bw create item --session "$BW_SESSION"
```

### Если запись существует — обновить:

```bash
ITEM_ID=$(bw list items --search "<project>/<key>" --session "$BW_SESSION" | \
  jq -r '.[] | select(.name=="<project>/<key>") | .id')

bw get item "$ITEM_ID" --session "$BW_SESSION" | \
  jq --arg notes "<value>" '.notes=$notes' | \
  bw encode | \
  bw edit item "$ITEM_ID" --session "$BW_SESSION"
```

```bash
# Синхронизировать после операции
bw sync --session "$BW_SESSION"
```

## Операция: delete

```bash
# 1. Найти запись
ITEM_ID=$(bw list items --search "<project>/<key>" --session "$BW_SESSION" | \
  jq -r '.[] | select(.name=="<project>/<key>") | .id')

# 2. Удалить
bw delete item "$ITEM_ID" --session "$BW_SESSION"

# 3. Синхронизировать
bw sync --session "$BW_SESSION"
```

Если запись не найдена — сообщить пользователю.

## Примеры

```bash
/batman-secret set api_key "sk-abc123"
# → Создаёт/обновляет запись piqule/api_key со значением sk-abc123

/batman-secret get api_key
# → Выводит значение и команду export API_KEY=sk-abc123

/batman-secret delete api_key
# → Удаляет запись piqule/api_key
```

## Важные детали

- Тип записи: `type=2` (Secure Note), `secureNote.type=0`
- Значение хранится в поле `notes`, не в `login`
- Поиск через `bw list items --search` возвращает список — всегда фильтровать по точному `.name`
- После `set`/`delete` всегда выполнять `bw sync`
- Флаг `--session` передавать явно или убедиться что `BW_SESSION` задан в env
