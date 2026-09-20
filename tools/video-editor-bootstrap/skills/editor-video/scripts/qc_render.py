#!/usr/bin/env python3
"""QC local de un render, ANTES de mandarlo a revisar a ningun sitio.

Comprueba de verdad: existencia, tamano, pistas, duracion, relacion de aspecto,
decodificacion completa del archivo (no solo la cabecera) y, si esta disponible,
loudness integrado. Devuelve JSON y sale != 0 si algo falla.

Uso:
  qc_render.py --archivo RUTA [--duracion-esperada 20] [--tolerancia 1.5]
               [--aspecto 9:16] [--salida qc.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def correr(cmd: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def main() -> int:
    ap = argparse.ArgumentParser(description="QC local de un render")
    ap.add_argument("--archivo", type=Path, required=True)
    ap.add_argument("--duracion-esperada", type=float)
    ap.add_argument("--tolerancia", type=float, default=1.0, help="segundos de margen")
    ap.add_argument("--aspecto", help="p.ej. 9:16, 16:9, 1:1")
    ap.add_argument("--salida", type=Path)
    ap.add_argument("--sin-decodificar", action="store_true", help="salta la decodificacion completa")
    a = ap.parse_args()

    f = a.archivo.expanduser()
    r: dict[str, Any] = {"archivo": str(f), "momento": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                         "comprobaciones": [], "fallos": [], "avisos": []}

    def check(nombre: str, ok: bool, detalle: str = "", critico: bool = True) -> bool:
        r["comprobaciones"].append({"nombre": nombre, "ok": ok, "detalle": detalle})
        if not ok:
            (r["fallos"] if critico else r["avisos"]).append(f"{nombre}: {detalle}")
        return ok

    if not check("existe", f.is_file(), str(f)):
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 2
    tam = f.stat().st_size
    r["bytes"] = tam
    r["sha256"] = sha256(f)
    check("tamano_no_trivial", tam > 100_000, f"{tam} bytes")

    if not shutil.which("ffprobe"):
        r["fallos"].append("ffprobe ausente: no se puede verificar el render. Instala ffmpeg.")
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 3

    p = correr(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(f)])
    if p.returncode != 0:
        check("ffprobe_lee_el_archivo", False, p.stderr.strip()[:300])
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 4
    datos = json.loads(p.stdout)
    vs = [s for s in datos.get("streams", []) if s.get("codec_type") == "video"]
    aus = [s for s in datos.get("streams", []) if s.get("codec_type") == "audio"]
    dur = float(datos.get("format", {}).get("duration", 0) or 0)
    r["duracion_s"] = round(dur, 3)
    r["pistas_video"] = len(vs)
    r["pistas_audio"] = len(aus)
    if vs:
        v = vs[0]
        r["resolucion"] = f"{v.get('width')}x{v.get('height')}"
        r["fps"] = v.get("r_frame_rate")
        r["codec_video"] = v.get("codec_name")
    if aus:
        r["codec_audio"] = aus[0].get("codec_name")
        r["canales"] = aus[0].get("channels")

    check("tiene_video", len(vs) >= 1, f"{len(vs)} pista(s)")
    check("tiene_audio", len(aus) >= 1, f"{len(aus)} pista(s) — un render mudo casi nunca es lo pedido")
    check("duracion_mayor_que_cero", dur > 0.5, f"{dur:.3f}s")

    if a.duracion_esperada is not None:
        d = abs(dur - a.duracion_esperada)
        check("duracion_esperada", d <= a.tolerancia,
              f"{dur:.2f}s frente a {a.duracion_esperada:.2f}s (desvio {d:.2f}s)")

    if a.aspecto and vs:
        try:
            num, den = (int(x) for x in a.aspecto.split(":"))
            real = Fraction(int(vs[0]["width"]), int(vs[0]["height"]))
            check("aspecto", math.isclose(float(real), num / den, rel_tol=0.02),
                  f"{vs[0]['width']}x{vs[0]['height']} = {float(real):.4f}, esperado {num/den:.4f}")
        except (ValueError, KeyError, ZeroDivisionError) as exc:
            check("aspecto", False, f"no se pudo evaluar: {exc}", critico=False)

    if not a.sin_decodificar and shutil.which("ffmpeg"):
        d = correr(["ffmpeg", "-v", "error", "-xerror", "-i", str(f), "-f", "null", "-"])
        check("decodifica_entero", d.returncode == 0 and not d.stderr.strip(),
              (d.stderr.strip()[:300] or "sin errores de decodificacion"))
        if aus:
            lo = correr(["ffmpeg", "-v", "info", "-i", str(f), "-af", "ebur128=peak=true", "-f", "null", "-"])
            for linea in reversed(lo.stderr.splitlines()):
                if "I:" in linea and "LUFS" in linea:
                    r["loudness_integrado"] = linea.strip()
                    break
            if "loudness_integrado" not in r:
                r["avisos"].append("no se pudo medir loudness (ebur128)")
    elif not a.sin_decodificar:
        r["avisos"].append("ffmpeg ausente: no se verifico la decodificacion completa")

    r["veredicto"] = "APTO" if not r["fallos"] else "NO APTO"
    salida = json.dumps(r, indent=2, ensure_ascii=False)
    if a.salida:
        a.salida.expanduser().parent.mkdir(parents=True, exist_ok=True)
        a.salida.expanduser().write_text(salida, encoding="utf-8")
        print(f"QC en {a.salida}: {r['veredicto']}"
              + (f" — fallos: {'; '.join(r['fallos'])}" if r["fallos"] else ""))
    else:
        print(salida)
    return 0 if not r["fallos"] else 1


if __name__ == "__main__":
    sys.exit(main())
