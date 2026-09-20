#!/bin/bash
# 20-instalar-skills.sh — instala las skills en ~/.claude/skills/ SIN tocar ~/.codex/skills/.
# No sobrescribe una skill existente salvo --forzar (y siempre con respaldo previo).
# Uso: bash 20-instalar-skills.sh [--forzar]
set -uo pipefail

FORZAR=0
[ "${1:-}" = "--forzar" ] && FORZAR=1

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORIGEN="$(cd "$AQUI/../skills" && pwd)"
DESTINO="$HOME/.claude/skills"
BACKUP_DIR="$HOME/.claude-backups/skills-$(date +%Y%m%d-%H%M%S)"

[ -d "$ORIGEN" ] || { echo "ERROR: no encuentro $ORIGEN" >&2; exit 1; }

CREADO_DIR=0
[ -d "$DESTINO" ] || CREADO_DIR=1
mkdir -p "$DESTINO"

for skill in editor-video analisis-video; do
  src="$ORIGEN/$skill"; dst="$DESTINO/$skill"
  [ -d "$src" ] || { echo "ERROR: falta $src" >&2; exit 1; }
  if [ -e "$dst" ] && [ $FORZAR -eq 0 ]; then
    printf '\033[33mYA EXISTE\033[0m %s — no se toca. Revisa y decide; usa --forzar para sustituir (con respaldo).\n' "$dst"
    continue
  fi
  if [ -e "$dst" ]; then
    mkdir -p "$BACKUP_DIR" && chmod 700 "$BACKUP_DIR"
    cp -R "$dst" "$BACKUP_DIR/$skill"
    printf '  respaldo de la version anterior en %s/%s\n' "$BACKUP_DIR" "$skill"
    rm -rf "$dst"
  fi
  cp -R "$src" "$dst"
  find "$dst" -name '*.py' -exec chmod +x {} \;
  printf '\033[32mINSTALADA\033[0m %s\n' "$dst"
done

printf '\n\033[1mSkills de Codex encontradas (solo lectura, NO se modifican)\033[0m\n'
if [ -d "$HOME/.codex/skills" ]; then
  for s in "$HOME"/.codex/skills/*/; do
    n="$(basename "$s")"
    printf '  %-20s %s\n' "$n" "$(find "$s" -type f | wc -l | tr -d ' ') archivo(s)"
  done
  cat <<'NOTA'
  Para fusionar contenido util de Codex en la version de Claude, compara a mano:
    diff -ru ~/.codex/skills/editor-video ~/.claude/skills/editor-video | less
  No copies literalmente rutas, invocaciones ni metadatos propios de Codex
  (~/.codex/..., $skill, agents/openai.yaml, create_goal/update_goal).
NOTA
else
  printf '  ~/.codex/skills no existe en esta maquina.\n'
fi

printf '\n\033[1mComo cargarlas\033[0m\n'
if [ $CREADO_DIR -eq 1 ]; then
  cat <<'NOTA'
  He creado ~/.claude/skills por primera vez: REINICIA Claude Code para que empiece a vigilar
  ese directorio (documentado por Anthropic: si el directorio no existia al arrancar, hace falta reinicio).
NOTA
else
  cat <<'NOTA'
  Claude Code vigila ~/.claude/skills en caliente: los cambios se aplican en la sesion en curso.
  Si no aparece, reinicia la sesion.
NOTA
fi
printf '  Comprueba escribiendo  /editor-video  y  /analisis-video  en el prompt.\n'
