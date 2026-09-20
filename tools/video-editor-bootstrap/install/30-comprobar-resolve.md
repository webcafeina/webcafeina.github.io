# 30 — Comprobar la conexión real con DaVinci Resolve

Un MCP arrancado **no** prueba que Resolve esté conectado. Esta comprobación es manual porque
depende de la interfaz de Resolve y de una decisión de Nacho.

## 1. Identifica la edición real

`DaVinci Resolve > About DaVinci Resolve`. Anota versión y si pone **Studio**.
El nombre de la carpeta de la aplicación no lo demuestra.

## 2. Según la edición

### Studio

1. `DaVinci Resolve > Preferences > System > General > External scripting using`.
2. Si está en **Ninguno**, hay que ponerlo en **Local**.
   - Esto habilita el scripting externo **local** (procesos de tu propio Mac).
   - **No actives Network.**
   - Es una decisión de Nacho: pídela explícitamente antes de cambiarla.
3. Guarda, **reinicia Resolve**, abre un proyecto y vuelve a probar.

### Gratuita (Free)

Blackmagic reserva el scripting externo a Studio. El repositorio ofrecía un puente in-app
desde `Workspace > Scripts`, pero **Resolve 21.1 movió el scripting Python a Studio** y ese
menú ya no lo lista. Con **Free 21.1 no hay ruta soportada**.

Opciones honestas, sin eludir la licencia:
- Bajar a Resolve 21.0.x y usar el puente (`python scripts/install_resolve_bridge.py`).
- Pasar a Studio.
- Editar sin control por MCP y usar solo el servidor avanzado (offline, sobre `.drp` exportados)
  más el análisis con Gemini.

## 3. Prueba en sesión

```text
claude
/mcp                      → ambos servidores deben decir Connected
```

Y después, en el chat, una lectura inocua con el MCP principal: versión de Resolve y nombre
del proyecto actual.

| Resultado | Significado |
|---|---|
| Devuelve versión y proyecto | Conexión viva. Puedes trabajar |
| Handle vacío / "no Resolve instance" | Resolve no acepta scripting: vuelve al punto 2 |
| El servidor MCP no arranca | Problema del lanzador o del venv: `bash 00-verificar-entorno.sh` |

## 4. Si necesitas escribir para probar

Crea un **proyecto de prueba claramente identificado** (por ejemplo
`ZZZ-prueba-instalacion-YYYYMMDD`) y bórralo al terminar. **No toques proyectos reales.**
