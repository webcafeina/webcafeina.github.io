# Almacenamiento, proyectos, timelines y nombres (obligatorio)

## Dos rutas distintas, siempre preguntadas

| Carpeta | Contiene | Nunca contiene |
|---|---|---|
| **Proyecto** | proyecto de Resolve, `brief.md`, `guion-audiovisual.md`, `estado.json`, inventarios, catálogos, proxies, revisiones, `.drp` editable | — |
| **Exportación** | lo que Nacho revisa o publica | proxies, cachés, originales |

No elijas ninguna de las dos por tu cuenta. No mezcles derivados con los originales.
Los originales quedan intactos: no se renombran, no se mueven, no se sobrescriben.

## Convención de nombres

```text
YYYYMMDD-cliente-cta-formatoVersion
```

- **Fecha** de arranque del encargo, en la zona horaria del cliente.
- `cliente` y `cta`: minúsculas, sin tildes, sin `ñ`, sin espacios; guiones entre palabras.
- Formato y versión: `v1`, `v2`… vertical 9:16 · `h1`, `h2`… horizontal 16:9 · `c1`, `c2`… cuadrado 1:1.
- Revisión interna: `r01`, `r02`… → `...-v1-r01.mp4`.
- Una **nueva edición** de verdad sube el número del formato (`v1` → `v2`).
- **Nunca uses `final`** en un nombre.

## Archivos junto a cada export

```text
YYYYMMDD-cliente-cta-formatoVersion.mp4
YYYYMMDD-cliente-cta-formatoVersion-briefing.md
YYYYMMDD-cliente-cta-formatoVersion-qc.md
YYYYMMDD-cliente-cta-formatoVersion.srt
YYYYMMDD-cliente-cta-formatoVersion.drp
```

El `-briefing.md` es una **copia Markdown autocontenida** del brief vigente: objetivo, copy,
CTA, estilo, marca, estado y decisiones, legible sin abrir Resolve.

## Un proyecto por idea creativa

```text
Proyecto:  20260920-cliente-idea-creativa
Timelines: 20260920-cliente-idea-creativa-v1
           20260920-cliente-idea-creativa-h1
           20260920-cliente-idea-creativa-c1
```

La carpeta de proyecto lleva el nombre base **sin** `formatoVersion`. Cada timeline tiene sus
propios ajustes, reencuadre, mezcla y gráficos cuando el formato lo requiera.

Crea otro proyecto cuando cambie la pieza, la idea o el CTA, salvo que Nacho pida agruparlas.

## Varios agentes sobre el mismo encargo

Cuando más de un agente (o más de una herramienta) monta las mismas piezas para compararlas,
cada uno **etiqueta sus archivos con su nombre, justo antes de la extensión**, y exporta a su
propia subcarpeta. Nunca se sobrescriben los archivos del otro.

```text
exports/<agente>/                       exports/<agente>/briefings/
exports/<agente>/audio/                 exports/<agente>/broll/

YYYYMMDD-cliente-cta-formatoVersion-<agente>.mp4
YYYYMMDD-cliente-cta-formatoVersion-<agente>-briefing.md
YYYYMMDD-cliente-cta-formatoVersion-<agente>.fcpxml
```

La etiqueta va también en el proyecto y en las timelines de Resolve
(`20260920-cliente-idea-creativa-claude`), para que los dos proyectos puedan convivir.

**Aviso sobre carpetas sincronizadas (Google Drive, Dropbox, iCloud).** Escribir el proyecto
de Resolve, los renders intermedios o el `estado.json` directamente en una carpeta
sincronizada produce copias de conflicto («archivo copia.ext») cuando el cliente de
sincronización compite con el proceso que escribe, y puede corromper un proyecto de Resolve
abierto. Trabaja en disco local y **copia a la carpeta sincronizada solo el resultado**, con
la sincronización en pausa durante el render si hace falta.
