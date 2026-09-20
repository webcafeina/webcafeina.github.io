# Revisión: cómo se critica una versión sin engañarse

## El ciclo de cada edición

**Paso 0 — puerta.** Comprueba que las versiones vigentes de `brief.md` y
`guion-audiovisual.md` están acordadas, o que hay delegación explícita.
No se inicia un loop de producción mientras se define el encargo.

```bash
python3 ../scripts/estado.py resumen --dir <proyecto>   # "Produccion: permitida" o BLOQUEADA
```

**1. Guardar y renderizar** una revisión numerada (`-r01`, `-r02`…) en la carpeta de exportación.

**2. Esperar el render y comprobar el archivo**, no la promesa de Resolve:

```bash
python3 ../scripts/qc_render.py --archivo <exports>/<nombre>-r01.mp4 \
  --duracion-esperada 20 --aspecto 9:16 --salida <proyecto>/<nombre>-r01-qc.json
```

Comprueba existencia, tamaño, pistas de vídeo y audio, duración, aspecto, **decodificación
completa** del archivo y loudness. Si sale `NO APTO`, se corrige antes de revisar nada.

**3. Analizar el export completo con audio** comparándolo con el brief:

```bash
<lanzador-gemini> -- <python> ../../analisis-video/scripts/gemini_video.py \
  --video <exports>/<nombre>-r01.mp4 --preset revision --brief <proyecto>/brief.md \
  --salida <proyecto>/<nombre>-r01-gemini.json
```

En piezas largas, cubre **todos los intervalos** con `--segmento` y registra qué quedó
cubierto y qué se muestreó. *Enviar el archivo entero no significa que se haya revisado cada
fotograma*: registra la cobertura real en `estado.json`.

**4. Crítica concreta.** Cada incidencia necesita: timestamp · evidencia visual y sonora ·
severidad · cambio propuesto.

| Severidad | Qué es | Efecto |
|---|---|---|
| **Crítica** | Incumple el brief, la marca o dice algo falso. Rótulo ilegible, CTA erróneo, corte que cambia el sentido, audio inservible | Bloquea la entrega |
| **Mayor** | Daña claramente la pieza: ritmo roto, salto de color evidente, logo fuera de zona segura | Bloquea la entrega |
| **Menor** | Mejorable: un frame de más, una respiración cortada justa | Se resuelve o se documenta |

Registra cada una:

```bash
python3 ../scripts/estado.py incidencia --dir <proyecto> --severidad critica \
  --timestamp 00:00:07 --texto "..." --evidencia "..." --render v1-r01
```

**Contrasta localmente** toda incidencia importante antes de actuar: abre el punto exacto,
mira y escucha. No te atribuyas una escucha que no has hecho. Gemini se equivoca: puede
inventar un corte, describir un color que no está o no oír una frase que sí suena.

**5. Corregir, renderizar de nuevo y buscar regresiones.** Un arreglo puede romper otra cosa:
vuelve a pasar el QC completo, no solo el punto tocado.

**6. Revisar el export final completo** y vincular el informe a su **ruta y hash**:

```bash
python3 ../scripts/estado.py render --dir <proyecto> --version v1-r03 \
  --archivo <exports>/<nombre>-r03.mp4 --qc <proyecto>/<nombre>-r03-qc.json
```

Así no se aprueba por error una versión anterior.

## Presupuesto de pasadas

Propón **hasta cuatro pasadas completas**, ajustables al material y al presupuesto acordado.

```bash
python3 ../scripts/estado.py pasada --dir <proyecto> --mejora si|no
```

Tras **dos pasadas sin mejora comprobable**, cambia de estrategia y comunica el límite.
Al agotarse el presupuesto o ante un bloqueo, conserva la mejor versión y explica lo
pendiente. **Nunca declares éxito por haber alcanzado un límite.** No ejecutes un bucle infinito.

## Cuándo se termina

Se cierra cuando **todo** esto es cierto:

- Se cumple el brief acordado.
- No queda ninguna incidencia crítica o mayor abierta.
- Las menores están resueltas o documentadas por escrito.
- Existen los entregables requeridos, comprobados en disco.

Una buena puntuación de Gemini **no** es ninguno de esos cuatro puntos.

## Informe de QC (`-qc.md`)

Qué se comprobó, cómo, con qué resultado, qué intervalos se cubrieron, qué quedó fuera,
qué incidencias se documentaron sin resolver y por qué, y el hash del archivo revisado.
