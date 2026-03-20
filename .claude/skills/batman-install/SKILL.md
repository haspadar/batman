# Скил `batman-install`

Установка batman-скилов глобально через симлинки в `~/.claude/skills/`.

## Инструкция

Выполни следующий bash-скрипт:

```bash
BATMAN_DIR="$(cd "$(dirname "$0")/../../../.." && pwd)"
SKILLS_SRC="$BATMAN_DIR/.claude/skills"
SKILLS_DST="$HOME/.claude/skills"

mkdir -p "$SKILLS_DST"

for skill_dir in "$SKILLS_SRC"/batman-*/; do
    skill_name=$(basename "$skill_dir")
    target="$SKILLS_DST/$skill_name"
    if [ -L "$target" ]; then
        echo "~ уже установлен: $skill_name"
    elif [ -d "$target" ]; then
        echo "✗ конфликт (папка существует): $skill_name"
    else
        ln -s "$skill_dir" "$target"
        echo "✓ установлен: $skill_name"
    fi
done

# Установка post-merge хука
HOOK_SRC="$BATMAN_DIR/hooks/post-merge"
HOOK_DST="$BATMAN_DIR/.git/hooks/post-merge"

if [ -f "$HOOK_SRC" ]; then
    cp "$HOOK_SRC" "$HOOK_DST"
    chmod +x "$HOOK_DST"
    echo "✓ post-merge хук установлен"
else
    echo "✗ файл hooks/post-merge не найден"
fi
```

Адаптируй путь `BATMAN_DIR` к реальному расположению репозитория batman на машине пользователя.

Для брата путь может отличаться — спроси где он склонировал репо, если не знаешь.

## После установки

Скилы `batman-*` станут доступны глобально во всех проектах Claude Code / Cursor.

Post-merge хук установлен в `.git/hooks/post-merge` — новые скилы будут подхватываться автоматически после `git pull`.
