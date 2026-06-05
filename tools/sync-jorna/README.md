# sync-jorna — verificación lip-sync XT4 ↔ iPhone

Script para verificar (y refinar) los 53 emparejamientos entre clips de la
Fujifilm X-T4 (sin audio) y clips del iPhone (con audio) de la jornada
de Santos.

## Qué hace

Para cada par del CSV:

1. Detecta la cara en el vídeo XT4 con MediaPipe FaceMesh y extrae la
   **apertura de boca** frame a frame (derivada absoluta, suavizada).
2. Extrae del audio del iPhone la **envolvente RMS** en banda de voz
   (300–3400 Hz, ventanas de 20 ms).
3. **Cross-correla** ambas señales dentro de una ventana ±N segundos
   alrededor del `dStart_s` ya estimado en la hoja → devuelve un
   `score` y un `lag_refinado_s`.
4. Genera un **contact sheet** (6 frames XT4 arriba + 6 frames iPhone
   abajo, ya alineados por el lag refinado) para verificación visual.

Veredicto automático:

| score          | veredicto |
|---------------:|:----------|
| ≥ 0.35         | OK        |
| 0.20 – 0.35    | DUDOSO    |
| < 0.20         | REVISAR   |

(Los umbrales son ajustables. En diálogo frontal con micro cerca, los
matches correctos suelen pasar de 0.4–0.6.)

## Instalación (macOS, una sola vez)

```bash
brew install ffmpeg
cd /Volumes/SuperWebcafeto/Santos\ jorna/_sync
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> En Apple Silicon, si `mediapipe` no instala, prueba
> `pip install mediapipe-silicon` (versiones <0.10) o asegúrate de tener
> Python 3.10/3.11.

## Uso

Estructura esperada:

```
/Volumes/SuperWebcafeto/Santos jorna/
├── _sync/
│   ├── lipsync_verify.py
│   ├── pairs.csv
│   ├── requirements.txt
│   └── (resultados se generan aquí)
└── (todos los .MOV renombrados PAR-XX_*.MOV / PAR-XX_*.mov)
```

Ejecución completa (los 53 pares):

```bash
cd /Volumes/SuperWebcafeto/Santos\ jorna/_sync
source .venv/bin/activate
python lipsync_verify.py \
  --pairs pairs.csv \
  --media-dir "/Volumes/SuperWebcafeto/Santos jorna" \
  --out-dir . \
  --search-window 10 \
  --max-seconds 120
```

Procesar solo unos pares concretos:

```bash
python lipsync_verify.py --pairs pairs.csv \
  --media-dir "/Volumes/SuperWebcafeto/Santos jorna" \
  --out-dir . --only 2,10,12,16,19,21
```

Continuar tras una interrupción (no rehace los que ya tienen contact sheet):

```bash
python lipsync_verify.py ... --skip-existing
```

## Salida

- `lipsync_results.csv` — ordenado peor → mejor para que veas los
  problemáticos primero. Columnas:
  - `par, score, lag_refinado_s, overlap_s, frames_con_cara,
    xt4, iphone, dStart_s, confianza_previa, veredicto, contact_sheet`
- `contact_sheets/PAR-XX.jpg` — verificación visual lado a lado.

## Flujo de trabajo recomendado

1. Lanza la corrida completa (tardará: ~30–60s por par, depende de
   duración y tu Mac).
2. Abre `lipsync_results.csv` y revisa todo lo que **no** sea `OK`.
3. Para cada `DUDOSO` / `REVISAR`, mira el contact sheet correspondiente.
   - Si los movimientos cuadran → es match correcto pero el lip-sync no
     pudo medirlo (cara tapada, cámara lejos, poca habla en el solape).
   - Si los movimientos NO cuadran → no era el iPhone bueno. Anota el
     correcto y vuelve a ejecutar `--only XX` con `pairs.csv` editado.
4. Cuando todos sean OK o confirmados manualmente, el `lag_refinado_s`
   te sirve también como offset fino para alinear el audio en montaje.

## Notas técnicas

- El signo de `dStart_s` sigue la convención del sheet:
  positivo = XT4 empieza DESPUÉS que iPhone.
- `lag_refinado_s` es el **ajuste adicional** sobre `dStart_s`. El offset
  total iPhone→XT4 final es `dStart_s + lag_refinado_s`.
- El análisis se limita a los primeros `--max-seconds` (default 120) para
  acelerar. Tomas más largas no suelen necesitar más para correlar.
- Si una toma no tiene cara visible en ningún momento de la XT4, el
  script salta el lip-sync y solo genera el contact sheet (veredicto
  `SIN_CARA`): tendrás que validarla a ojo.
