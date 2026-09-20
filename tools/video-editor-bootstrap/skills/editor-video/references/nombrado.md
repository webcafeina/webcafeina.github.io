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
