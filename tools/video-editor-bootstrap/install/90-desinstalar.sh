#!/bin/bash
# 90-desinstalar.sh — deshace EXCLUSIVAMENTE lo que instalo este kit.
# No toca: ~/.codex/, la instalacion de /Users/<tu>/Documents/Codex/tools/video-editor/,
# Resolve, sus preferencias, ni ningun otro MCP o skill.
set -uo pipefail

printf '\033[1mSe van a eliminar:\033[0m\n'
printf '  - MCP de usuario: davinci-resolve, davinci-resolve-advanced\n'
printf '  - Skills: ~/.claude/skills/editor-video, ~/.claude/skills/analisis-video\n'
printf '\nNO se tocan: ~/.codex/, la carpeta de herramientas, Resolve ni sus preferencias.\n'
printf '\n¿Continuar? escribe SI: '
read -r R
[ "$R" = "SI" ] || { echo "Cancelado."; exit 0; }

for n in davinci-resolve davinci-resolve-advanced; do
  if claude mcp get "$n" >/dev/null 2>&1; then
    claude mcp remove "$n" --scope user 2>/dev/null || claude mcp remove "$n" 2>/dev/null
    printf '  eliminado MCP %s\n' "$n"
  else
    printf '  MCP %s no estaba registrado\n' "$n"
  fi
done

BACKUP_DIR="$HOME/.claude-backups/desinstalacion-$(date +%Y%m%d-%H%M%S)"
for s in editor-video analisis-video; do
  d="$HOME/.claude/skills/$s"
  if [ -d "$d" ]; then
    mkdir -p "$BACKUP_DIR" && chmod 700 "$BACKUP_DIR"
    mv "$d" "$BACKUP_DIR/$s"
    printf '  skill %s movida a %s/%s (no borrada)\n' "$s" "$BACKUP_DIR" "$s"
  fi
done

printf '\nHecho. Si cambiaste "External scripting using" a Local en Resolve y quieres revertirlo,\n'
printf 'hazlo a mano: DaVinci Resolve > Preferences > System > General.\n'
printf 'Los respaldos de ~/.claude.json siguen en ~/.claude-backups/ — borralos tu cuando quieras.\n'
