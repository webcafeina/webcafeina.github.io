#!/usr/bin/env python3
"""Estado persistente de una edicion (estado.json). Mecanismo de continuidad del loop.

NO es un demonio ni un proceso en segundo plano: es un fichero que permite reanudar el
trabajo en otra sesion. Nada de esto sigue ejecutandose con Claude Code cerrado.

Uso:
  estado.py init   --dir CARPETA --proyecto NOMBRE [--material RUTA] [--exportacion RUTA]
  estado.py ver    --dir CARPETA [--campo fase]
  estado.py fase   --dir CARPETA --valor montaje
  estado.py conformidad --dir CARPETA --documento brief|guion --archivo RUTA --quien "Nacho" [--delegado]
  estado.py render --dir CARPETA --version v1-r01 --archivo RUTA [--qc RUTA_JSON]
  estado.py incidencia --dir CARPETA --severidad critica --timestamp 00:00:07 --texto "..." [--render v1-r01]
  estado.py cerrar-incidencia --dir CARPETA --id 3 [--motivo documentada]
  estado.py pasada --dir CARPETA [--mejora si|no]
  estado.py job    --dir CARPETA --archivo-remoto files/abc [--estado pendiente|borrado]
  estado.py coste  --dir CARPETA --entrada 1234 --salida 567
  estado.py bloqueo --dir CARPETA --texto "..." | --limpiar
  estado.py siguiente --dir CARPETA --texto "..."
  estado.py resumen --dir CARPETA
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

FASES = ["preproduccion", "montaje", "revision", "entrega", "bloqueado", "cerrado"]
SEVERIDADES = ["critica", "mayor", "menor"]


def ahora() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def ruta(dir_: Path) -> Path:
    return dir_.expanduser() / "estado.json"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def cargar(dir_: Path) -> dict[str, Any]:
    p = ruta(dir_)
    if not p.is_file():
        sys.exit(f"ERROR: no existe {p}. Ejecuta primero: estado.py init --dir {dir_} --proyecto NOMBRE")
    return json.loads(p.read_text(encoding="utf-8"))


def guardar(dir_: Path, d: dict[str, Any]) -> None:
    d["actualizado"] = ahora()
    p = ruta(dir_)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)
    print(f"estado actualizado: {p}")


def plantilla(proyecto: str, material: str | None, exportacion: str | None, dir_: Path) -> dict[str, Any]:
    return {
        "proyecto": proyecto,
        "creado": ahora(),
        "actualizado": ahora(),
        "fase": "preproduccion",
        "rutas": {
            "carpeta_proyecto": str(dir_.expanduser()),
            "carpeta_exportacion": exportacion,
            "material_original": material,
        },
        "conformidad": {
            "brief": {"archivo": None, "sha256": None, "acordado_por": None, "fecha": None},
            "guion": {"archivo": None, "sha256": None, "acordado_por": None, "fecha": None},
            "delegacion_explicita": False,
        },
        "pasadas": {"maximo_acordado": 4, "hechas": 0, "sin_mejora_consecutivas": 0},
        "renders": [],
        "cobertura": [],
        "incidencias": [],
        "jobs_gemini": [],
        "coste": {"tokens_entrada": 0, "tokens_salida": 0, "notas": "tokens comprobables; el coste en euros depende de la tarifa vigente"},
        "siguiente_accion": "Concretar brief.md y guion-audiovisual.md y obtener conformidad.",
        "bloqueo": None,
    }


def puede_producir(d: dict[str, Any]) -> tuple[bool, str]:
    c = d["conformidad"]
    if c.get("delegacion_explicita"):
        return True, "delegacion explicita registrada"
    faltan = [k for k in ("brief", "guion") if not c[k].get("acordado_por")]
    if faltan:
        return False, "sin conformidad registrada de: " + ", ".join(faltan)
    return True, "brief y guion acordados"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def con_dir(p):
        p.add_argument("--dir", type=Path, required=True, help="carpeta de proyecto")
        return p

    p = con_dir(sub.add_parser("init"))
    p.add_argument("--proyecto", required=True)
    p.add_argument("--material")
    p.add_argument("--exportacion")

    p = con_dir(sub.add_parser("ver")); p.add_argument("--campo")
    p = con_dir(sub.add_parser("fase")); p.add_argument("--valor", required=True, choices=FASES)

    p = con_dir(sub.add_parser("conformidad"))
    p.add_argument("--documento", required=True, choices=["brief", "guion"])
    p.add_argument("--archivo", type=Path, required=True)
    p.add_argument("--quien", required=True)
    p.add_argument("--delegado", action="store_true", help="marca delegacion explicita para produccion")

    p = con_dir(sub.add_parser("render"))
    p.add_argument("--version", required=True)
    p.add_argument("--archivo", type=Path, required=True)
    p.add_argument("--qc", type=Path)

    p = con_dir(sub.add_parser("incidencia"))
    p.add_argument("--severidad", required=True, choices=SEVERIDADES)
    p.add_argument("--timestamp", required=True)
    p.add_argument("--texto", required=True)
    p.add_argument("--render")
    p.add_argument("--evidencia", default="")

    p = con_dir(sub.add_parser("cerrar-incidencia"))
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--motivo", default="resuelta", choices=["resuelta", "documentada", "descartada"])

    p = con_dir(sub.add_parser("pasada")); p.add_argument("--mejora", choices=["si", "no"], default="si")
    p = con_dir(sub.add_parser("job"))
    p.add_argument("--archivo-remoto", required=True)
    p.add_argument("--estado", default="pendiente", choices=["pendiente", "borrado"])

    p = con_dir(sub.add_parser("coste")); p.add_argument("--entrada", type=int, default=0); p.add_argument("--salida", type=int, default=0)
    p = con_dir(sub.add_parser("bloqueo")); p.add_argument("--texto"); p.add_argument("--limpiar", action="store_true")
    p = con_dir(sub.add_parser("siguiente")); p.add_argument("--texto", required=True)
    con_dir(sub.add_parser("resumen"))

    a = ap.parse_args()

    if a.cmd == "init":
        if ruta(a.dir).is_file():
            sys.exit(f"ERROR: ya existe {ruta(a.dir)}. No se sobrescribe.")
        guardar(a.dir, plantilla(a.proyecto, a.material, a.exportacion, a.dir))
        return 0

    d = cargar(a.dir)

    if a.cmd == "ver":
        print(json.dumps(d.get(a.campo, d) if a.campo else d, indent=2, ensure_ascii=False))
        return 0

    if a.cmd == "fase":
        ok, motivo = puede_producir(d)
        if a.valor in ("montaje", "revision", "entrega") and not ok:
            sys.exit(f"BLOQUEADO: no se pasa a '{a.valor}' {motivo}.\n"
                     f"Registra conformidad con: estado.py conformidad --dir {a.dir} --documento brief --archivo brief.md --quien 'Nacho'")
        d["fase"] = a.valor

    elif a.cmd == "conformidad":
        f = a.archivo.expanduser()
        if not f.is_file():
            sys.exit(f"ERROR: no existe {f}")
        d["conformidad"][a.documento] = {
            "archivo": str(f), "sha256": sha256(f), "acordado_por": a.quien, "fecha": ahora(),
        }
        if a.delegado:
            d["conformidad"]["delegacion_explicita"] = True

    elif a.cmd == "render":
        f = a.archivo.expanduser()
        if not f.is_file():
            sys.exit(f"ERROR: no existe el render {f}. No se registra un render inexistente.")
        reg = {"version": a.version, "ruta": str(f), "sha256": sha256(f),
               "bytes": f.stat().st_size, "momento": ahora(), "qc": None}
        if a.qc and a.qc.expanduser().is_file():
            reg["qc"] = json.loads(a.qc.expanduser().read_text(encoding="utf-8"))
        d["renders"].append(reg)

    elif a.cmd == "incidencia":
        nid = max([i["id"] for i in d["incidencias"]], default=0) + 1
        d["incidencias"].append({
            "id": nid, "severidad": a.severidad, "timestamp": a.timestamp, "descripcion": a.texto,
            "evidencia": a.evidencia, "render": a.render, "estado": "abierta", "creada": ahora(),
        })
        print(f"incidencia #{nid} registrada")

    elif a.cmd == "cerrar-incidencia":
        for i in d["incidencias"]:
            if i["id"] == a.id:
                i["estado"] = a.motivo
                i["cerrada"] = ahora()
                break
        else:
            sys.exit(f"ERROR: no existe la incidencia #{a.id}")

    elif a.cmd == "pasada":
        d["pasadas"]["hechas"] += 1
        if a.mejora == "no":
            d["pasadas"]["sin_mejora_consecutivas"] += 1
        else:
            d["pasadas"]["sin_mejora_consecutivas"] = 0
        if d["pasadas"]["sin_mejora_consecutivas"] >= 2:
            print("AVISO: dos pasadas sin mejora comprobable. Cambia de estrategia y comunicalo.")
        if d["pasadas"]["hechas"] >= d["pasadas"]["maximo_acordado"]:
            print("AVISO: alcanzado el maximo de pasadas acordado. Alcanzar el limite NO es aprobar.")

    elif a.cmd == "job":
        d["jobs_gemini"].append({"archivo_remoto": a.archivo_remoto, "estado": a.estado, "momento": ahora()})

    elif a.cmd == "coste":
        d["coste"]["tokens_entrada"] += a.entrada
        d["coste"]["tokens_salida"] += a.salida

    elif a.cmd == "bloqueo":
        d["bloqueo"] = None if a.limpiar else {"texto": a.texto, "desde": ahora()}
        if not a.limpiar:
            d["fase"] = "bloqueado"

    elif a.cmd == "siguiente":
        d["siguiente_accion"] = a.texto

    elif a.cmd == "resumen":
        ok, motivo = puede_producir(d)
        abiertas = [i for i in d["incidencias"] if i["estado"] == "abierta"]
        ult = d["renders"][-1] if d["renders"] else None
        pend = [j for j in d["jobs_gemini"] if j["estado"] == "pendiente"]
        print(f"Proyecto      : {d['proyecto']}")
        print(f"Fase          : {d['fase']}")
        print(f"Produccion    : {'permitida' if ok else 'BLOQUEADA'} ({motivo})")
        print(f"Pasadas       : {d['pasadas']['hechas']}/{d['pasadas']['maximo_acordado']}"
              f" (sin mejora: {d['pasadas']['sin_mejora_consecutivas']})")
        print(f"Ultimo render : {ult['version'] + ' ' + ult['sha256'][:12] if ult else 'ninguno'}")
        print(f"Incidencias   : {len(abiertas)} abiertas "
              f"({sum(1 for i in abiertas if i['severidad'] == 'critica')} criticas, "
              f"{sum(1 for i in abiertas if i['severidad'] == 'mayor')} mayores)")
        print(f"Subidas pend. : {len(pend)}" + (" -> " + ", ".join(j["archivo_remoto"] for j in pend) if pend else ""))
        print(f"Tokens        : {d['coste']['tokens_entrada']} entrada / {d['coste']['tokens_salida']} salida")
        print(f"Bloqueo       : {d['bloqueo']['texto'] if d['bloqueo'] else 'ninguno'}")
        print(f"Siguiente     : {d['siguiente_accion']}")
        listo = ok and not abiertas and ult is not None
        print(f"\nCriterio de cierre: {'se cumple lo comprobable (revisa entregables a mano)' if listo else 'NO se cumple'}")
        return 0

    guardar(a.dir, d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
