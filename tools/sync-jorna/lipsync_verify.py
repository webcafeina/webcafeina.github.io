#!/usr/bin/env python3
"""
Verifica los emparejamientos XT4↔iPhone usando lip-sync:
- Extrae apertura de boca del vídeo XT4 (sin audio) con MediaPipe FaceMesh.
- Extrae envolvente RMS de la voz del audio del iPhone (banda 300-3400 Hz).
- Cross-correla ambas señales dentro de una ventana de búsqueda ±N seg
  alrededor del dStart_s declarado en la hoja de cálculo.
- Devuelve score [-1..1] y lag refinado.
- Genera un contact sheet (6 frames XT4 arriba + 6 frames iPhone abajo)
  para verificación visual rápida.

Salida: lipsync_results.csv (ordenado por score ascendente, los peores primero).
"""
import argparse
import csv
import os
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
import cv2
import mediapipe as mp
from scipy.signal import butter, sosfiltfilt
from PIL import Image, ImageDraw, ImageFont

HZ = 50.0  # frecuencia común de muestreo para ambas señales


def run(cmd):
    return subprocess.run(cmd, capture_output=True, check=False)


def extract_audio_envelope(video_path, hz=HZ):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav = f.name
    try:
        r = run(["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "1",
                 "-ar", "16000", "-f", "wav", wav])
        if r.returncode != 0 or not os.path.exists(wav) or os.path.getsize(wav) < 1000:
            return None
        with wave.open(wav, "rb") as w:
            sr = w.getframerate()
            n = w.getnframes()
            pcm = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    finally:
        if os.path.exists(wav):
            os.unlink(wav)
    if len(pcm) < sr:
        return None
    # Filtro paso-banda para voz
    sos = butter(4, [300, 3400], btype="band", fs=sr, output="sos")
    pcm = sosfiltfilt(sos, pcm)
    # RMS en ventanas de 1/hz segundos
    win = int(sr / hz)
    n_frames = len(pcm) // win
    pcm = pcm[: n_frames * win].reshape(n_frames, win)
    rms = np.sqrt((pcm ** 2).mean(axis=1) + 1e-9)
    env = np.log1p(rms * 100.0).astype(np.float32)
    return env


def extract_mouth_signal(video_path, hz=HZ, max_seconds=None):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(1, int(round(fps / hz)))
    face = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False, max_num_faces=1,
        refine_landmarks=True, min_detection_confidence=0.4,
    )
    openings = []
    frame_idx = 0
    have_face = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if max_seconds and frame_idx / fps > max_seconds:
            break
        if frame_idx % step == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = face.process(rgb)
            if res.multi_face_landmarks:
                lm = res.multi_face_landmarks[0].landmark
                h, w = frame.shape[:2]
                up = np.array([lm[13].x * w, lm[13].y * h])
                lo = np.array([lm[14].x * w, lm[14].y * h])
                top = np.array([lm[10].x * w, lm[10].y * h])
                bot = np.array([lm[152].x * w, lm[152].y * h])
                face_h = np.linalg.norm(top - bot) + 1e-6
                openings.append(np.linalg.norm(up - lo) / face_h)
                have_face += 1
            else:
                openings.append(np.nan)
        frame_idx += 1
    cap.release()
    face.close()
    if not openings or have_face < 20:
        return None, have_face
    arr = np.array(openings, dtype=np.float32)
    mask = np.isnan(arr)
    if mask.any():
        idx = np.arange(len(arr))
        arr[mask] = np.interp(idx[mask], idx[~mask], arr[~mask])
    # Derivada absoluta suavizada -> proxy de "movimiento de boca"
    deriv = np.abs(np.diff(arr, prepend=arr[0]))
    k = 5
    kern = np.ones(k) / k
    deriv = np.convolve(deriv, kern, mode="same").astype(np.float32)
    return deriv, have_face


def correlate_signals(xt4_sig, iph_sig, dStart_s, search_window_s=10.0, hz=HZ):
    """
    dStart_s > 0  => XT4 empieza dStart_s después que iPhone.
                     XT4[0] alinea con iPhone[dStart_s].
    dStart_s < 0  => XT4 empieza |dStart_s| antes que iPhone.
                     XT4[|dStart_s|] alinea con iPhone[0].
    """
    xt4_off_s = max(0.0, -dStart_s)
    iph_off_s = max(0.0, dStart_s)
    x = xt4_sig[int(xt4_off_s * hz):]
    y = iph_sig[int(iph_off_s * hz):]
    L = min(len(x), len(y))
    if L < int(2 * hz):
        return -1.0, 0.0, 0.0
    x = x[:L].copy()
    x = (x - x.mean()) / (x.std() + 1e-9)
    W = int(search_window_s * hz)
    best_score = -np.inf
    best_lag_samples = 0
    # Probamos desplazar y (iPhone) ±W respecto a la alineación inicial
    for lag in range(-W, W + 1):
        if lag >= 0:
            seg = y[lag : lag + L]
        else:
            # lag negativo: necesitamos muestras "antes" -> recortar x desde la izquierda
            seg = y[: L + lag]
            if len(seg) < int(2 * hz):
                continue
            xseg = x[-lag : -lag + len(seg)]
            score = float(np.dot((xseg - xseg.mean()) / (xseg.std() + 1e-9),
                                 (seg - seg.mean()) / (seg.std() + 1e-9))) / len(seg)
            if score > best_score:
                best_score = score
                best_lag_samples = lag
            continue
        if len(seg) < int(2 * hz):
            continue
        xseg = x[: len(seg)]
        score = float(np.dot((xseg - xseg.mean()) / (xseg.std() + 1e-9),
                             (seg - seg.mean()) / (seg.std() + 1e-9))) / len(seg)
        if score > best_score:
            best_score = score
            best_lag_samples = lag
    overlap_s = L / hz
    return best_score, best_lag_samples / hz, overlap_s


def grab_frame(path, t):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        out = f.name
    r = run(["ffmpeg", "-y", "-ss", f"{max(0,t):.3f}", "-i", path,
             "-frames:v", "1", "-q:v", "3", out])
    if r.returncode != 0 or not os.path.exists(out) or os.path.getsize(out) < 500:
        if os.path.exists(out):
            os.unlink(out)
        return None
    img = Image.open(out).convert("RGB")
    os.unlink(out)
    return img


def make_contact_sheet(xt4_path, iph_path, xt4_start_s, iph_start_s,
                       overlap_s, out_path, header_text, n=6):
    if overlap_s < 2.0:
        overlap_s = 2.0
    times = np.linspace(0.5, max(0.5, overlap_s - 0.5), n)
    xt4_imgs = [grab_frame(xt4_path, xt4_start_s + t) for t in times]
    iph_imgs = [grab_frame(iph_path, iph_start_s + t) for t in times]
    xt4_imgs = [i for i in xt4_imgs if i is not None]
    iph_imgs = [i for i in iph_imgs if i is not None]
    if not xt4_imgs or not iph_imgs:
        return False
    H = 220

    def resize(im):
        w, h = im.size
        return im.resize((max(1, int(w * H / h)), H))

    xt4_imgs = [resize(i) for i in xt4_imgs]
    iph_imgs = [resize(i) for i in iph_imgs]
    W = max(sum(i.size[0] for i in xt4_imgs), sum(i.size[0] for i in iph_imgs))
    pad = 24
    sheet = Image.new("RGB", (W, H * 2 + pad * 3), "black")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except Exception:
        font = ImageFont.load_default()
    draw.text((8, 4), header_text, fill="white", font=font)
    x = 0
    for im in xt4_imgs:
        sheet.paste(im, (x, pad))
        x += im.size[0]
    draw.text((8, pad + H + 4), "XT4 ↑   iPhone ↓", fill="yellow", font=font)
    x = 0
    for im in iph_imgs:
        sheet.paste(im, (x, pad * 2 + H))
        x += im.size[0]
    sheet.save(out_path, quality=85)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True, help="CSV con par,xt4_file,iphone_file,dStart_s")
    ap.add_argument("--media-dir", required=True, help="Carpeta donde están los .MOV renombrados")
    ap.add_argument("--out-dir", required=True, help="Carpeta de salida (se crea si no existe)")
    ap.add_argument("--search-window", type=float, default=10.0,
                    help="Ventana de búsqueda del lag refinado, en segundos (default 10)")
    ap.add_argument("--max-seconds", type=float, default=120.0,
                    help="Máximo de segundos a analizar de cada clip (default 120, 0=sin límite)")
    ap.add_argument("--only", type=str, default="",
                    help="Lista separada por comas de pares a procesar (ej. 1,7,12). Vacío=todos.")
    ap.add_argument("--skip-existing", action="store_true",
                    help="Saltar pares que ya tengan contact sheet generado")
    args = ap.parse_args()

    out = Path(args.out_dir)
    sheets_dir = out / "contact_sheets"
    sheets_dir.mkdir(parents=True, exist_ok=True)

    only = set()
    if args.only.strip():
        only = {s.strip() for s in args.only.split(",") if s.strip()}

    with open(args.pairs, newline="") as f:
        pairs = list(csv.DictReader(f))

    results = []
    max_s = args.max_seconds if args.max_seconds > 0 else None

    for i, p in enumerate(pairs, 1):
        par = p["par"]
        if only and par not in only:
            continue
        xt4_file = p["xt4_file"]
        iph_file = p["iphone_file"]
        dStart = float(p["dStart_s"])
        prev = p.get("confianza_previa", "")
        cs_path = sheets_dir / f"PAR-{int(par):02d}.jpg"
        if args.skip_existing and cs_path.exists():
            print(f"[{i}/{len(pairs)}] PAR-{par} skip (existe)", flush=True)
            continue

        xt4_path = os.path.join(args.media_dir, xt4_file)
        iph_path = os.path.join(args.media_dir, iph_file)
        if not os.path.exists(xt4_path) or not os.path.exists(iph_path):
            print(f"[{i}/{len(pairs)}] PAR-{par} FALTA ARCHIVO", flush=True)
            results.append({"par": par, "score": 0.0, "lag_refinado_s": 0.0,
                            "overlap_s": 0.0, "frames_con_cara": 0,
                            "xt4": xt4_file, "iphone": iph_file,
                            "dStart_s": dStart, "confianza_previa": prev,
                            "veredicto": "FALTA_ARCHIVO", "contact_sheet": ""})
            continue

        print(f"[{i}/{len(pairs)}] PAR-{par}  XT4={xt4_file}  iPhone={iph_file}  dStart={dStart:+.0f}s",
              flush=True)
        mouth, n_face = extract_mouth_signal(xt4_path, max_seconds=max_s)
        audio = extract_audio_envelope(iph_path)

        if mouth is None or audio is None:
            note = "SIN_CARA" if mouth is None else "SIN_AUDIO"
            print(f"   -> {note}", flush=True)
            # Aun así generamos contact sheet visual
            make_contact_sheet(xt4_path, iph_path, 0,
                               max(0, dStart), 30,
                               str(cs_path),
                               f"PAR-{par}  {note}  dStart={dStart:+.0f}s")
            results.append({"par": par, "score": 0.0, "lag_refinado_s": 0.0,
                            "overlap_s": 0.0, "frames_con_cara": n_face if mouth is None else -1,
                            "xt4": xt4_file, "iphone": iph_file,
                            "dStart_s": dStart, "confianza_previa": prev,
                            "veredicto": note, "contact_sheet": str(cs_path)})
            continue

        score, lag_s, overlap_s = correlate_signals(
            mouth, audio, dStart, search_window_s=args.search_window
        )
        refined_dStart = dStart + lag_s
        # Para el contact sheet usamos el lag refinado
        xt4_off = max(0.0, -refined_dStart)
        iph_off = max(0.0, refined_dStart)

        if score >= 0.35:
            veredicto = "OK"
        elif score >= 0.20:
            veredicto = "DUDOSO"
        else:
            veredicto = "REVISAR"

        header = (f"PAR-{par}  prev={prev}  dStart={dStart:+.0f}s  "
                  f"lag_refinado={lag_s:+.2f}s  score={score:.3f}  {veredicto}")
        make_contact_sheet(xt4_path, iph_path, xt4_off, iph_off,
                           overlap_s, str(cs_path), header)

        print(f"   score={score:.3f}  lag={lag_s:+.2f}s  overlap={overlap_s:.1f}s  {veredicto}",
              flush=True)
        results.append({"par": par, "score": round(score, 3),
                        "lag_refinado_s": round(lag_s, 2),
                        "overlap_s": round(overlap_s, 1),
                        "frames_con_cara": n_face,
                        "xt4": xt4_file, "iphone": iph_file,
                        "dStart_s": dStart,
                        "confianza_previa": prev,
                        "veredicto": veredicto,
                        "contact_sheet": str(cs_path)})

    # CSV ordenado: peor score primero
    results.sort(key=lambda r: (r["veredicto"] != "OK", r["score"]))
    csv_path = out / "lipsync_results.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    n_ok = sum(1 for r in results if r["veredicto"] == "OK")
    n_dud = sum(1 for r in results if r["veredicto"] == "DUDOSO")
    n_rev = sum(1 for r in results if r["veredicto"] == "REVISAR")
    print(f"\nResumen: OK={n_ok}  DUDOSO={n_dud}  REVISAR/error={n_rev}")
    print(f"CSV:           {csv_path}")
    print(f"Contact sheets:{sheets_dir}")


if __name__ == "__main__":
    main()
