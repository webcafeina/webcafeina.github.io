#!/bin/bash
# 05-instalar-desde-cero.sh — SOLO para un Mac sin la instalacion reutilizable.
# Descarga los repositorios oficiales y crea un entorno virtual aislado.
# NO ejecuta install.py del repositorio: ese instalador reconfigura otros clientes
# (Claude Desktop, Cursor, VS Code, Zed, JetBrains y Codex CLI en ~/.codex/config.toml).
# El registro en Claude Code lo hace 10-registrar-mcp.sh, que solo toca Claude Code.
set -euo pipefail

BASE="${1:-$HOME/Documents/video-editor}"
echo "Instalando en $BASE"
mkdir -p "$BASE"
cd "$BASE"

if [ -d davinci-resolve-mcp/.git ]; then
  echo "== repositorio ya presente; actualizando"
  git -C davinci-resolve-mcp pull --ff-only
else
  git clone https://github.com/samuelgursky/davinci-resolve-mcp.git
fi
git -C davinci-resolve-mcp log -1 --format='commit %H (%ad) %s' --date=short | tee COMMIT-davinci-resolve-mcp.txt

echo "== entorno virtual propio"
PY="${PYTHON:-python3}"
"$PY" -m venv venv
./venv/bin/pip install --upgrade pip
# Orden importante: requirements.txt fija mcp<2 (server.py usa mcp.server.fastmcp, que 2.x elimino)
./venv/bin/pip install -r davinci-resolve-mcp/requirements.txt
./venv/bin/pip install google-genai
./venv/bin/python -c "import mcp, google.genai as g; print('mcp OK, google-genai', g.__version__)"

echo "== dependencias Node del servidor avanzado"
( cd davinci-resolve-mcp && npm install --omit=dev --omit=optional )
echo "   (better-sqlite3 / sharp / pg son opcionales: instalalos solo si una ruta concreta los pide;"
echo "    consulta antes la herramienta 'capabilities' del MCP avanzado con su esquema real)"

echo "== lanzador del MCP principal"
cat > start-resolve-mcp.sh <<LANZADOR
#!/bin/sh
# Lanzador del MCP principal de DaVinci Resolve. Generado por 05-instalar-desde-cero.sh
BASE="$BASE"
RESOLVE_SUPPORT="/Library/Application Support/Blackmagic Design/DaVinci Resolve"
export RESOLVE_SCRIPT_API="\$RESOLVE_SUPPORT/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
export PYTHONPATH="\$RESOLVE_SCRIPT_API/Modules:\${PYTHONPATH:-}"
exec "\$BASE/venv/bin/python" "\$BASE/davinci-resolve-mcp/src/server.py" "\$@"
LANZADOR
chmod +x start-resolve-mcp.sh

cat <<NOTA

Hecho. Falta, y NO lo hace este script:
  - La credencial de Gemini: creala en https://aistudio.google.com/apikey y ponla en el
    entorno de forma privada (GEMINI_API_KEY). No la pegues en el chat, ni en 'claude mcp add',
    ni en el historial del shell, ni en un archivo versionado.
  - Registrar los MCP:   bash 10-registrar-mcp.sh "$BASE"
  - Instalar las skills: bash 20-instalar-skills.sh
  - Verificar:           bash 00-verificar-entorno.sh "$BASE"
NOTA
