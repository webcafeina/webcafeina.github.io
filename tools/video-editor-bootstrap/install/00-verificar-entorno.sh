#!/bin/bash
# 00-verificar-entorno.sh — comprobaciones REALES, solo lectura. No instala ni modifica nada.
# Uso:  bash 00-verificar-entorno.sh [BASE]
#       BASE = raiz de la instalacion reutilizable (por defecto la de este Mac).
set -uo pipefail

BASE="${1:-$HOME/Documents/Codex/tools/video-editor}"
RESOLVE_APP="${RESOLVE_APP:-/Applications/DaVinci Resolve/DaVinci Resolve.app}"
FALLOS=0

ok()   { printf '  \033[32mOK\033[0m    %s\n' "$1"; }
warn() { printf '  \033[33mAVISO\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31mFALLO\033[0m %s\n' "$1"; FALLOS=$((FALLOS+1)); }
tit()  { printf '\n\033[1m%s\033[0m\n' "$1"; }

tit "1. Sistema"
printf '  %-22s %s\n' "SO"       "$(uname -s) $(uname -r) $(uname -m)"
if command -v sw_vers >/dev/null 2>&1; then
  printf '  %-22s %s\n' "macOS"  "$(sw_vers -productVersion) (build $(sw_vers -buildVersion))"
else
  bad "sw_vers ausente: esto NO es macOS. El puente con Resolve no puede funcionar aqui."
fi
printf '  %-22s %s\n' "Usuario"  "$(whoami)"
printf '  %-22s %s\n' "HOME"     "$HOME"
printf '  %-22s %s\n' "Fecha"    "$(date '+%Y-%m-%d %H:%M:%S %Z')"

tit "2. Herramientas de linea de comandos"
for b in claude node npm python3 git ffmpeg ffprobe; do
  p="$(command -v "$b" 2>/dev/null || true)"
  if [ -n "$p" ]; then
    case "$b" in
      claude)  v="$(claude --version 2>/dev/null | head -1)";;
      node)    v="$(node --version 2>/dev/null)";;
      npm)     v="$(npm --version 2>/dev/null)";;
      python3) v="$(python3 --version 2>&1)";;
      git)     v="$(git --version 2>/dev/null)";;
      ffmpeg)  v="$(ffmpeg -version 2>/dev/null | head -1 | cut -c1-40)";;
      ffprobe) v="$(ffprobe -version 2>/dev/null | head -1 | cut -c1-40)";;
    esac
    ok "$(printf '%-8s %-28s %s' "$b" "$p" "$v")"
  else
    case "$b" in
      ffmpeg|ffprobe) bad "$b ausente. Necesario para QC local de renders y para copias compatibles. Instalalo con: brew install ffmpeg";;
      *)              bad "$b ausente en PATH";;
    esac
  fi
done

tit "3. Instalacion reutilizable en $BASE"
if [ ! -d "$BASE" ]; then
  bad "No existe $BASE. Esta maquina no tiene la instalacion previa: usa 05-instalar-desde-cero.sh"
else
  for f in venv/bin/python start-resolve-mcp.sh gemini_env.py \
           davinci-resolve-mcp/src/server.py davinci-resolve-mcp/bin/davinci-resolve-advanced-mcp.mjs; do
    if [ -e "$BASE/$f" ]; then
      [ -x "$BASE/$f" ] || [ "${f##*.}" = "py" ] || [ "${f##*.}" = "mjs" ] \
        && ok "$f" || warn "$f existe pero no es ejecutable"
    else
      bad "falta $BASE/$f"
    fi
  done
  if [ -x "$BASE/venv/bin/python" ]; then
    printf '  %-22s %s\n' "venv python" "$("$BASE/venv/bin/python" --version 2>&1)"
    "$BASE/venv/bin/python" -c 'import mcp, sys; print("  mcp SDK             ", mcp.__version__ if hasattr(mcp,"__version__") else "instalado")' 2>/dev/null \
      || warn "el venv no tiene el paquete mcp importable"
    "$BASE/venv/bin/python" -c 'import google.genai as g; print("  google-genai        ", g.__version__)' 2>/dev/null \
      || bad "el venv no tiene google-genai: sin el no hay analisis con Gemini"
  fi
  if [ -d "$BASE/davinci-resolve-mcp/.git" ]; then
    printf '  %-22s %s\n' "davinci-resolve-mcp" "$(git -C "$BASE/davinci-resolve-mcp" log -1 --format='%h %ad %s' --date=short 2>/dev/null | cut -c1-70)"
    printf '  %-22s %s\n' "version package.json" "$(python3 -c "import json;print(json.load(open('$BASE/davinci-resolve-mcp/package.json'))['version'])" 2>/dev/null)"
  fi
fi

tit "4. DaVinci Resolve"
if [ -d "$RESOLVE_APP" ]; then
  PLIST="$RESOLVE_APP/Contents/Info.plist"
  VER="$(defaults read "$PLIST" CFBundleShortVersionString 2>/dev/null || echo '?')"
  NOM="$(defaults read "$PLIST" CFBundleName 2>/dev/null || echo '?')"
  ok "instalado: $NOM $VER"
  case "$NOM" in
    *Studio*) printf '  %-22s %s\n' "Edicion" "Studio (scripting externo soportado)";;
    *)        warn "El bundle NO se llama Studio. Si es la edicion gratuita, Resolve 21.1 movio el scripting Python a Studio: ni el scripting externo ni el puente in-app del repositorio funcionan. Compruebalo en DaVinci Resolve > About.";;
  esac
  printf '  %-22s %s\n' "Proceso en marcha" "$(pgrep -x 'DaVinci Resolve' >/dev/null && echo 'si' || echo 'no')"
  # Preferencia de scripting externo (solo lectura)
  CFG="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/config.dat"
  if [ -f "$CFG" ]; then
    if strings "$CFG" 2>/dev/null | grep -qi 'ExternalScripting'; then
      printf '  %-22s %s\n' "config.dat" "contiene clave de ExternalScripting (valor no legible de forma fiable; verifica en Preferences > System > General)"
    else
      printf '  %-22s %s\n' "config.dat" "sin clave ExternalScripting visible: probablemente en 'Ninguno'"
    fi
  fi
  API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
  [ -d "$API" ] && ok "modulos de scripting presentes en $API" || warn "no encuentro $API"
else
  bad "No existe $RESOLVE_APP"
fi

tit "5. Claude Code: MCP ya registrados"
if command -v claude >/dev/null 2>&1; then
  claude mcp list 2>&1 | sed 's/^/  /' | head -30
else
  bad "claude no esta en PATH"
fi

tit "6. Skills ya presentes"
for d in "$HOME/.claude/skills" "$HOME/.codex/skills"; do
  if [ -d "$d" ]; then
    printf '  %s:\n' "$d"
    ls -1 "$d" 2>/dev/null | sed 's/^/    - /'
  else
    printf '  %s: no existe\n' "$d"
  fi
done

tit "7. Credencial de Gemini (sin imprimir su valor)"
if [ -x "$BASE/venv/bin/python" ] && [ -f "$BASE/gemini_env.py" ]; then
  OUT="$("$BASE/venv/bin/python" "$BASE/gemini_env.py" check 2>&1)"
  RC=$?
  printf '%s\n' "$OUT" | sed -E 's/(AIza|sk-)[A-Za-z0-9_-]+/[REDACTADO]/g' | sed 's/^/  /'
  [ $RC -eq 0 ] && ok "gemini_env.py check devolvio 0" || bad "gemini_env.py check devolvio $RC"
else
  warn "no hay lanzador gemini_env.py en $BASE; se usara la variable GEMINI_API_KEY del entorno"
  [ -n "${GEMINI_API_KEY:-}${GOOGLE_API_KEY:-}" ] && ok "hay una credencial en el entorno (valor no mostrado)" \
                                                  || bad "no hay credencial de Gemini en el entorno"
fi

tit "Resultado"
if [ $FALLOS -eq 0 ]; then
  printf '  \033[32mSin fallos bloqueantes.\033[0m Revisa los AVISO antes de continuar.\n\n'
else
  printf '  \033[31m%d comprobacion(es) fallida(s).\033[0m No continues sin resolverlas o sin decidir explicitamente saltartelas.\n\n' "$FALLOS"
fi
exit $FALLOS
