#!/usr/bin/env python3
"""Crea timelines vacías en el proyecto de DaVinci Resolve YA ABIERTO.

No abre, no cierra y no modifica ningún proyecto ni timeline existente. Si una timeline
con el mismo nombre ya existe, la deja como está y lo dice.

Requiere macOS, Resolve **Studio** con `Preferences > System > General >
External scripting using` en **Local**, y Resolve abierto con un proyecto abierto.

Uso:
  python3 crear_timelines.py --comprobar
  python3 crear_timelines.py --bin claude \
      --timeline 20260920-zeris-primera-reaccion-v1-claude \
      --timeline 20260920-zeris-a-que-sabe-v1-claude \
      --timeline 20260920-zeris-pruebalo-en-caceres-v1-claude \
      --ancho 1080 --alto 1920
"""
from __future__ import annotations

import argparse
import os
import sys

MODULOS = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
LIB = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"


def conectar():
    if sys.platform != "darwin":
        sys.exit("ERROR: este script solo funciona en el Mac donde corre Resolve.")
    os.environ.setdefault("RESOLVE_SCRIPT_API", os.path.dirname(MODULOS))
    os.environ.setdefault("RESOLVE_SCRIPT_LIB", LIB)
    if MODULOS not in sys.path:
        sys.path.append(MODULOS)
    try:
        import DaVinciResolveScript as dvr
    except ImportError:
        sys.exit(f"ERROR: no encuentro el modulo de scripting en {MODULOS}.\n"
                 "Comprueba que Resolve esta instalado y que es la edicion Studio.")
    resolve = dvr.scriptapp("Resolve")
    if resolve is None:
        sys.exit("ERROR: handle vacio. Resolve no esta aceptando scripting.\n"
                 "Comprueba: Resolve abierto, con un proyecto abierto, y\n"
                 "Preferences > System > General > External scripting using = Local (reinicia despues).")
    return resolve


def describir(resolve) -> tuple:
    pm = resolve.GetProjectManager()
    proyecto = pm.GetCurrentProject()
    if proyecto is None:
        sys.exit("ERROR: no hay ningun proyecto abierto en Resolve.")
    print(f"Resolve          : {resolve.GetVersionString()}")
    print(f"Pagina actual    : {resolve.GetCurrentPage()}")
    print(f"Proyecto abierto : {proyecto.GetName()}")
    print(f"Timelines        : {proyecto.GetTimelineCount()}")
    for i in range(1, int(proyecto.GetTimelineCount()) + 1):
        tl = proyecto.GetTimelineByIndex(i)
        print(f"  {i}. {tl.GetName()}  "
              f"{tl.GetSetting('timelineResolutionWidth')}x{tl.GetSetting('timelineResolutionHeight')} "
              f"@ {tl.GetSetting('timelineFrameRate')}")
    return pm, proyecto


def buscar_bin(mp, nombre: str):
    raiz = mp.GetRootFolder()
    for sub in raiz.GetSubFolderList():
        if sub.GetName() == nombre:
            return sub
    return mp.AddSubFolder(raiz, nombre)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--comprobar", action="store_true", help="solo leer: version, proyecto y timelines")
    ap.add_argument("--timeline", action="append", default=[], help="nombre de timeline a crear (repetible)")
    ap.add_argument("--bin", dest="carpeta", help="bin del Media Pool donde crearlas")
    ap.add_argument("--ancho", type=int, default=1080)
    ap.add_argument("--alto", type=int, default=1920)
    ap.add_argument("--fps", help="por defecto, el del proyecto")
    a = ap.parse_args()

    resolve = conectar()
    _, proyecto = describir(resolve)

    if a.comprobar or not a.timeline:
        if not a.comprobar:
            print("\n(no se indico ninguna --timeline: no se ha creado nada)")
        return 0

    mp = proyecto.GetMediaPool()
    existentes = {proyecto.GetTimelineByIndex(i).GetName()
                  for i in range(1, int(proyecto.GetTimelineCount()) + 1)}

    carpeta_previa = mp.GetCurrentFolder()
    if a.carpeta:
        destino = buscar_bin(mp, a.carpeta)
        if destino is None:
            sys.exit(f"ERROR: no pude crear ni encontrar el bin '{a.carpeta}'")
        mp.SetCurrentFolder(destino)
        print(f"\nBin destino      : {a.carpeta}")

    fps = a.fps or proyecto.GetSetting("timelineFrameRate")
    print(f"Ajustes          : {a.ancho}x{a.alto} @ {fps}\n")

    creadas, omitidas = [], []
    for nombre in a.timeline:
        if nombre in existentes:
            print(f"  YA EXISTE  {nombre} — no se toca")
            omitidas.append(nombre)
            continue
        tl = mp.CreateEmptyTimeline(nombre)
        if tl is None:
            print(f"  FALLO      {nombre} — Resolve no la creo")
            continue
        tl.SetSetting("useCustomSettings", "1")
        tl.SetSetting("timelineResolutionWidth", str(a.ancho))
        tl.SetSetting("timelineResolutionHeight", str(a.alto))
        tl.SetSetting("timelineOutputResolutionWidth", str(a.ancho))
        tl.SetSetting("timelineOutputResolutionHeight", str(a.alto))
        if fps:
            tl.SetSetting("timelineFrameRate", str(fps))
        creadas.append(nombre)
        print(f"  CREADA     {nombre}")

    if a.carpeta and carpeta_previa is not None:
        mp.SetCurrentFolder(carpeta_previa)

    # Verificacion por lectura posterior: que la operacion devuelva exito no prueba nada.
    print("\n--- verificacion leyendo el proyecto otra vez ---")
    ok = True
    final = {}
    for i in range(1, int(proyecto.GetTimelineCount()) + 1):
        tl = proyecto.GetTimelineByIndex(i)
        final[tl.GetName()] = (tl.GetSetting("timelineResolutionWidth"),
                               tl.GetSetting("timelineResolutionHeight"),
                               tl.GetSetting("timelineFrameRate"))
    for nombre in creadas:
        if nombre not in final:
            print(f"  NO APARECE {nombre}")
            ok = False
            continue
        w, h, f = final[nombre]
        bien = (str(w) == str(a.ancho) and str(h) == str(a.alto))
        print(f"  {'OK   ' if bien else 'MAL  '} {nombre}  {w}x{h} @ {f}")
        ok = ok and bien

    print(f"\nCreadas: {len(creadas)} · Ya existian: {len(omitidas)} · Total en proyecto: {proyecto.GetTimelineCount()}")
    if creadas:
        print("Las timelines estan VACIAS: contienen los ajustes, no el montaje.")
        print("Guarda el proyecto en Resolve (Cmd+S) para consolidar los cambios.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
