# Entorno: qué hay instalado y qué significa cada pieza

## Los dos MCP no hacen lo mismo

| MCP | Qué es | Necesita Resolve abierto | Para qué |
|---|---|---|---|
| `davinci-resolve` | Servidor Python compuesto (37 herramientas) sobre la Scripting API oficial | **Sí** | Importar medios, crear timelines, cortar, grading, Fairlight, render |
| `davinci-resolve-advanced` | Servidor Node offline (18 herramientas) | **No** | Leer y editar `.drp` / `.drt` / `.drx` **sobre copias exportadas** |

**Nunca escribas con el servidor avanzado en la base de datos activa de Resolve.** Trabaja
sobre un `.drp` exportado y reimpórtalo.

## Servidor arrancado ≠ Resolve conectado

- `claude mcp list` y `/mcp` dicen si el **proceso MCP** arrancó y respondió al handshake.
- Que aparezca *Connected* no dice nada sobre DaVinci Resolve.
- La prueba real es una lectura inocua: versión de Resolve y proyecto actual. Si devuelve un
  handle vacío o un error de conexión, Resolve **no** está aceptando scripting.

Haz esa lectura al empezar cualquier sesión de montaje, antes de prometer nada.

## Si Resolve no conecta

1. **Resolve tiene que estar abierto y con un proyecto abierto.**
2. **Studio:** `DaVinci Resolve > Preferences > System > General > External scripting using`
   debe estar en **Local**. Cambiarlo habilita el scripting externo local; **pídeselo a Nacho
   antes de tocarlo** y explícale qué habilita. **No actives Network.** Reinicia Resolve
   después del cambio y vuelve a probar.
3. **Edición gratuita:** Blackmagic reserva el scripting externo a Studio. El repositorio
   ofrecía un puente in-app (`Workspace > Scripts`) que funcionaba hasta Resolve 21.0.x, pero
   **Resolve 21.1 movió el scripting Python a Studio** y el menú de Scripts ya no lo lista.
   Con Free 21.1 no hay ruta soportada: no prometas compatibilidad ni intentes eludir la
   licencia. Las salidas son bajar a 21.0.x, pasar a Studio, o editar sin control por MCP.
4. Comprueba la edición real en `DaVinci Resolve > About DaVinci Resolve`, no por el nombre
   de la carpeta.

## ffmpeg / ffprobe

Imprescindibles para el QC local de renders, el inventario técnico y las copias compatibles.
Si faltan: `brew install ffmpeg`. Sin `ffprobe`, `qc_render.py` se niega a dar un veredicto en
vez de inventarlo.

## Gemini

La credencial se lee **solo del entorno** (`GEMINI_API_KEY` / `GOOGLE_API_KEY`). No se pega en
el chat, no se pasa como argumento, no se imprime, no se guarda en ningún repositorio.

En el Mac de Nacho existe un lanzador privado que inyecta la credencial al proceso hijo:

```bash
<BASE>/venv/bin/python <BASE>/gemini_env.py check          # comprobar autenticación
<BASE>/venv/bin/python <BASE>/gemini_env.py -- <BASE>/venv/bin/python <script.py> [args]
```

Verifica los modelos disponibles antes de usarlos; los nombres del ejemplo caducan:

```bash
<lanzador> -- <python> ../analisis-video/scripts/gemini_video.py --listar-modelos
```

## Comprobación rápida de sesión

```bash
claude --version
claude mcp list
claude mcp get davinci-resolve
command -v ffprobe ffmpeg
python3 scripts/estado.py resumen --dir <carpeta-de-proyecto>
```
