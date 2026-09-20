#!/bin/bash
# 10-registrar-mcp.sh — registra los dos MCP de DaVinci Resolve en Claude Code con alcance de usuario.
# Idempotente: si una entrada ya existe, NO la sobrescribe (avisa y sigue).
# Hace respaldo privado de ~/.claude.json antes de tocar nada.
# Uso: bash 10-registrar-mcp.sh [BASE]
set -uo pipefail

BASE="${1:-$HOME/Documents/Codex/tools/video-editor}"
BACKUP_DIR="$HOME/.claude-backups/video-editor-$(date +%Y%m%d-%H%M%S)"

die() { printf '\033[31mERROR:\033[0m %s\n' "$1" >&2; exit 1; }
inf() { printf '  %s\n' "$1"; }

command -v claude >/dev/null 2>&1 || die "claude no esta en PATH"
[ -x "$BASE/start-resolve-mcp.sh" ] || die "falta $BASE/start-resolve-mcp.sh (ejecuta antes 00-verificar-entorno.sh)"
[ -f "$BASE/davinci-resolve-mcp/bin/davinci-resolve-advanced-mcp.mjs" ] || die "falta el servidor avanzado .mjs"
[ -x "$BASE/venv/bin/python" ] || die "falta $BASE/venv/bin/python"

NODE_BIN="$(command -v node)" || die "node no esta en PATH"
[ -n "$NODE_BIN" ] || die "node no encontrado"
NODE_DIR="$(dirname "$NODE_BIN")"
# El MCP avanzado necesita ffmpeg/ffprobe en PATH para las rutas de audio.
FF_DIR="$(dirname "$(command -v ffmpeg || echo /opt/homebrew/bin/ffmpeg)")"
MCP_PATH="$NODE_DIR:$FF_DIR:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

printf '\n\033[1mRespaldo\033[0m\n'
mkdir -p "$BACKUP_DIR" && chmod 700 "$BACKUP_DIR"
for f in "$HOME/.claude.json" "$HOME/.claude/settings.json"; do
  if [ -f "$f" ]; then
    cp -p "$f" "$BACKUP_DIR/$(basename "$f")" && chmod 600 "$BACKUP_DIR/$(basename "$f")"
    inf "copiado $f -> $BACKUP_DIR/$(basename "$f")"
  fi
done
inf "respaldo en $BACKUP_DIR (contiene configuracion privada: no lo subas a ningun repositorio)"

registrar() {
  local nombre="$1"; shift
  if claude mcp get "$nombre" >/dev/null 2>&1; then
    printf '\n\033[33mYA EXISTE\033[0m %s — no se toca. Revisa con: claude mcp get %s\n' "$nombre" "$nombre"
    claude mcp get "$nombre" 2>&1 | sed 's/^/  /' | head -12
    return 0
  fi
  printf '\n\033[1mRegistrando %s\033[0m\n' "$nombre"
  if "$@"; then
    inf "registrado"
  else
    printf '\033[31mfallo al registrar %s\033[0m\n' "$nombre"
    return 1
  fi
}

# Principal: servidor Python compuesto (37 herramientas) a traves del lanzador existente.
registrar davinci-resolve \
  claude mcp add --scope user --transport stdio davinci-resolve \
    -- /bin/sh "$BASE/start-resolve-mcp.sh"

# Avanzado: servidor Node offline (.drp/.drt/.drx). Sin claves API en los argumentos.
registrar davinci-resolve-advanced \
  claude mcp add --scope user --transport stdio \
    -e "AAF_PROBE_PYTHON=$BASE/venv/bin/python" \
    -e "PATH=$MCP_PATH" \
    davinci-resolve-advanced \
    -- "$NODE_BIN" "$BASE/davinci-resolve-mcp/bin/davinci-resolve-advanced-mcp.mjs"

printf '\n\033[1mEstado tras el registro\033[0m\n'
claude mcp list 2>&1 | sed 's/^/  /'

cat <<'NOTA'

Siguiente paso (no lo da por hecho este script):
  1. Abre una sesion interactiva:  claude
  2. Ejecuta  /mcp  y comprueba que ambos aparecen "Connected".
     "Connected" = el proceso MCP arranco y respondio al handshake.
     NO significa que DaVinci Resolve este conectado.
  3. Pide una lectura inocua de version/proyecto con la herramienta del MCP principal.
     Si devuelve un handle vacio, Resolve no esta aceptando scripting: ver 30-comprobar-resolve.md
NOTA
