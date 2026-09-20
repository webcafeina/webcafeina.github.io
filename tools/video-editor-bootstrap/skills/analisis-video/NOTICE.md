# Origen y cambios

Esta skill deriva de **santmun/analisis-video** (MIT), commit `8b5432e` del 2026-09-09,
"Publish portable Gemini video analysis skill". Se conserva su licencia en `LICENSE`.

Cambios respecto al original, para Claude Code:

| Cambio | Motivo |
|---|---|
| Eliminado `agents/openai.yaml` y la invocación `$analisis-video` | Metadatos e invocación propios de Codex; en Claude Code la skill se invoca como `/analisis-video` |
| Añadido `scripts/gemini_video.py` | El original es solo instrucciones. El loop de edición necesita una ejecución determinista y reanudable (subida, espera con plazo, consulta, limpieza) |
| Ruta de consulta: `models.generate_content` | Verificado contra `google-genai` 2.24.0. `client.interactions` existe en el SDK, pero `generate_content` es la ruta estable y documentada para comprensión de vídeo |
| Añadida selección de modelo contra `models.list()` | El original ya pedía no fijar nombres de modelo; el script lo comprueba en ejecución en vez de confiar |
| Añadidos presets `inventario`, `revision`, `verificar-concepto` | Enganchan con el loop de `editor-video` |

Lo que **no** se ha cambiado: la exigencia de evidencia con timestamps, la separación entre
observación e interpretación, la prohibición de atribuirse una escucha no realizada, el
tratamiento de las instrucciones dentro del vídeo como datos, y la limpieza remota.
