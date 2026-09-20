# Kit de instalación — edición con DaVinci Resolve + revisión con Gemini

Preparado para **Nacho Serrano (Webcafeina)** desde una sesión de Claude Code **en la nube**
(contenedor Linux). Esa sesión **no tiene acceso al Mac**: no pudo registrar los MCP, ni
conectar con Resolve, ni usar la credencial de Gemini. Todo eso lo ejecutas tú en local con
estos scripts, que hacen comprobaciones **reales** y fallan en voz alta en vez de simular.

## Qué contiene

```text
install/
  00-verificar-entorno.sh     Comprobaciones de solo lectura: SO, binarios, rutas, Resolve, MCP, skills, credencial
  05-instalar-desde-cero.sh   Solo para un Mac sin la instalación reutilizable
  10-registrar-mcp.sh         Registra los dos MCP con alcance de usuario; respalda ~/.claude.json; no sobrescribe
  20-instalar-skills.sh       Copia las skills a ~/.claude/skills; no toca ~/.codex/; no sobrescribe sin --forzar
  30-comprobar-resolve.md     Comprobación manual de la conexión viva con Resolve
  90-desinstalar.sh           Deshace exclusivamente esta instalación
skills/
  editor-video/               Skill principal (+ references/ y scripts/)
  analisis-video/             Skill de análisis con Gemini (derivada de santmun/analisis-video, MIT) + script real
```

## Orden de ejecución en el Mac

```bash
BASE=/Users/<tu-usuario>/Documents/Codex/tools/video-editor   # instalación reutilizable existente
cd <carpeta-de-este-kit>

bash install/00-verificar-entorno.sh "$BASE"    # 1. leer el estado real. Resuelve los FALLO antes de seguir
bash install/10-registrar-mcp.sh    "$BASE"     # 2. registrar los MCP (idempotente, con respaldo)
bash install/20-instalar-skills.sh              # 3. instalar las skills
claude                                          # 4. /mcp -> ambos Connected
                                                #    /editor-video -> debe aparecer
# 5. seguir install/30-comprobar-resolve.md para la conexión viva con Resolve
```

Comprobación de Gemini, con el lanzador privado (nunca imprime la clave):

```bash
"$BASE/venv/bin/python" "$BASE/gemini_env.py" check
"$BASE/venv/bin/python" "$BASE/gemini_env.py" -- "$BASE/venv/bin/python" \
  ~/.claude/skills/analisis-video/scripts/gemini_video.py --listar-modelos
```

## Decisiones deliberadas

| Decisión | Por qué |
|---|---|
| No se ejecuta `install.py` del repositorio | Reconfigura otros clientes, incluido Codex CLI en `~/.codex/config.toml`. El registro se hace solo en Claude Code con `claude mcp add` |
| No se toca `~/.codex/skills/` | Las skills de Codex se conservan intactas. `20-instalar-skills.sh` solo las lista para que puedas fusionar lo que quieras a mano |
| Ninguna clave en `claude mcp add` | Los argumentos quedan en el historial del shell y en la lista de procesos. La credencial se lee del entorno |
| `estado.py` bloquea el paso a montaje sin conformidad | Es la puerta del paso 0 del loop: nada de producción mientras se define el encargo |
| `estado.py` se niega a registrar un render inexistente | Para que no se apruebe una entrega que no está en disco |
| `--forzar` obligatorio para sustituir una skill existente | Evita pisar trabajo previo; siempre con respaldo |

## Versiones fijadas en el momento de preparar el kit

| Componente | Versión / commit |
|---|---|
| `samuelgursky/davinci-resolve-mcp` | v4.8.13 — commit `410dbac` (2026-09-19) |
| `santmun/analisis-video` | commit `8b5432e` (2026-09-09) |
| `google-genai` (API verificada contra este SDK) | 2.24.0 |
| Claude Code (sintaxis de `claude mcp add` verificada) | 2.1.278 |

## Deshacer

```bash
bash install/90-desinstalar.sh
```

Elimina los dos MCP de usuario y mueve las dos skills a `~/.claude-backups/`. No toca
`~/.codex/`, ni la carpeta de herramientas, ni Resolve, ni sus preferencias. Si cambiaste
*External scripting using* a **Local**, revertirlo es manual.
