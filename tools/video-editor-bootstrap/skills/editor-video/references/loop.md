# Continuidad: estado persistente y reanudación

## Qué mecanismo se usa, y qué no

Claude Code **no tiene** un equivalente a `create_goal` / `update_goal` de Codex. No copies
esas llamadas. Lo que hay en esta versión:

| Mecanismo | Qué hace | Límite real |
|---|---|---|
| `estado.json` + `scripts/estado.py` | Estado persistente en disco, reanudable en cualquier sesión | Lo tienes que leer y actualizar tú |
| Lista de tareas de la sesión | Sigue los pasos dentro de una conversación | Muere con la conversación |
| `/loop` | Repite un prompt a intervalos dentro de la sesión | **Se detiene al cerrar Claude Code** |

**Nada de esto sigue ejecutándose con la sesión cerrada.** No se lo digas a Nacho de otra
manera. Y no se crea ningún hook global que impida terminar las conversaciones, ni se
desactivan permisos para forzar autonomía.

## estado.json

Un fichero por proyecto, en la carpeta de proyecto. Campos: fase, conformidad (con el sha256
del brief y del guion aprobados), rutas, pasadas, renders (ruta + hash + QC), cobertura,
incidencias, `jobs_gemini`, coste en tokens, siguiente acción y bloqueo.

```bash
python3 ../scripts/estado.py init --dir <proyecto> --proyecto <nombre-base> \
  --material <ruta-originales> --exportacion <ruta-exports>
python3 ../scripts/estado.py resumen --dir <proyecto>
python3 ../scripts/estado.py siguiente --dir <proyecto> --texto "..."
python3 ../scripts/estado.py bloqueo --dir <proyecto> --texto "Resolve no acepta scripting"
```

Dos comportamientos deliberados del script:

- **No deja pasar a montaje, revisión o entrega sin conformidad registrada** (o `--delegado`).
- **No registra un render que no existe en disco.** No se aprueba una entrega inexistente.

## Reanudar una edición

1. `estado.py resumen --dir <proyecto>`.
2. Lee `bloqueo` y `siguiente_accion` antes que nada.
3. Comprueba `jobs_gemini` con estado `pendiente`: hay subidas remotas sin borrar. Reutilízalas
   o bórralas; no subas otra vez el mismo archivo.
4. Comprueba que el último render sigue en disco con el mismo hash. Si no coincide, alguien lo
   cambió: no razones sobre él.
5. Comprueba que el sha256 del brief acordado sigue siendo el del `brief.md` actual. Si cambió,
   vuelve a acordarlo antes de seguir.
6. Continúa por `siguiente_accion`.

## Uso opcional de `/loop`

Para iterar dentro de una sesión larga, `/loop` puede repetir un prompt (por ejemplo:
"continúa la pasada de revisión de <proyecto> según estado.json"). Úsalo solo con el loop de
producción ya autorizado, con un presupuesto de pasadas acordado, y detenlo en cuanto
`estado.py resumen` diga que se cumple el criterio de cierre o aparezca un bloqueo.
