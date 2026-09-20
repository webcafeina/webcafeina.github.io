# Preproducción: del encargo al guion acordado

La preproducción permite **lectura e inventario local y propuestas**. No autoriza análisis
externo, montaje, generación de recursos ni exportación.

## Qué preguntar, y en qué orden

Primero (sin repetir lo que ya sabes):

1. Rutas y selección del material.
2. Cuántas piezas.
3. Formato y medio de publicación.
4. Objetivo y audiencia.
5. Carpeta de proyecto y carpeta de exportación.

Después, **solo lo que falte**: duración · estilo y referencias · guion o voz · subtítulos e
idioma · restricciones · música y licencias · entrega y plazo · presupuesto y qué se puede
enviar a Gemini.

Propón soluciones en vez de pedir que Nacho rellene un formulario.

## Inventario técnico real

```bash
for f in <material>/*; do
  ffprobe -v error -print_format json -show_format -show_streams "$f"
done
```

Registra por archivo: duración, resolución, fps, codecs, pistas de audio, y si el audio es
utilizable. **No deduzcas el contenido del nombre del archivo.**

## Catálogo de tomas y transcripción

Requieren mirar y escuchar de verdad. El análisis audiovisual con Gemini necesita alcance
acordado para esa carpeta; hasta entonces, el catálogo se hace con lo que puedas comprobar
localmente y se marca lo que queda pendiente.

Catálogo: archivo · entrada · salida · qué ocurre · encuadre · calidad técnica · audio ·
para qué sirve. Transcripción: literal, con tiempos, marcando `[inaudible]`.

## brief.md

Cada punto etiquetado **confirmado / propuesto / pendiente / no aplica**:

```markdown
# Brief — <proyecto>
Estado: propuesta v1 · Fecha: YYYY-MM-DD

## Encargo
- Cliente / marca: ... [confirmado]
- Piezas y formatos: ... [confirmado]
- Medio de publicación: ... [propuesto]

## Mensaje
- Objetivo: ...
- Audiencia: ...
- Mensaje principal / secundario: ...
- CTA y URL exactos: ...

## Estilo y dirección de arte
- Referencias o descriptores: ...
- Temperatura / contraste / saturación / textura / pieles / luz / límite del grading: ...

## Marca
- Archivos de logo (rutas): ...
- Variante, ubicación y duración: [delegado en el editor | especificado]

## Restricciones
- Qué NO se puede hacer: ...
- Música y licencias: ...
- Presupuesto y envío a Gemini: ...

## Entregables
- Archivos, subtítulos, .drp, manifiesto: ...

## Decisiones registradas
- YYYY-MM-DD: ...
```

## guion-audiovisual.md

Historia · secuencias · **planos necesarios** frente a **planos verificados en el material**
(con archivo y tiempos) · diálogos y voz en off · textos y títulos **exactos** · logos · CTA
y URL. Marca los planos que no existen: son una decisión pendiente, no un detalle.

## Conformidad

```bash
python3 ../scripts/estado.py conformidad --dir <proyecto> --documento brief \
  --archivo <proyecto>/brief.md --quien "Nacho Serrano"
python3 ../scripts/estado.py conformidad --dir <proyecto> --documento guion \
  --archivo <proyecto>/guion-audiovisual.md --quien "Nacho Serrano"
```

Queda guardado el sha256 de lo aprobado. Si el documento cambia después, se ve.
Sin esto (o sin `--delegado`), `estado.py` bloquea el paso a montaje.
