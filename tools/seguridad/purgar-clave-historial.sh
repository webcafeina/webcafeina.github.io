#!/bin/bash
# purgar-clave-historial.sh
#
# Elimina del historial de webcafeina/webcafeina.github.io el archivo index.html que
# contenia una clave de la API de Gemini (commit d26408e, 03-06-2025), y .DS_Store.
#
# ESTO NO INVALIDA LA CLAVE. Rotala ANTES en https://aistudio.google.com/apikey
# GitHub conserva los commits inalcanzables accesibles por SHA hasta que su soporte
# los purga: https://support.github.com/contact  (pide "purge cached views").
#
# Procedimiento probado el 2026-09-20 en un clon espejo: deja 0 blobs de index.html
# y 0 objetos con la cadena 'generativelanguage'.
#
# ESTADO 2026-09-20: las ramas claude/* YA estan purgadas y subidas. Falta SOLO `main`,
# porque GitHub la rechaza desde fuera con "protected branch hook declined". Para main:
#   - quita temporalmente la proteccion en Settings > Branches, ejecuta con --subir y vuelve
#     a ponerla; o
#   - ejecuta este script desde tu Mac, con tus credenciales y la proteccion levantada.
#
# Uso:
#   bash purgar-clave-historial.sh              # simulacro: reescribe en local y verifica, NO sube
#   bash purgar-clave-historial.sh --subir      # ademas hace push --force de las tres ramas
set -euo pipefail

REPO=https://github.com/webcafeina/webcafeina.github.io
TRABAJO="${TMPDIR:-/tmp}/purga-webcafeina-$(date +%Y%m%d-%H%M%S)"
SUBIR=0
[ "${1:-}" = "--subir" ] && SUBIR=1

command -v git-filter-repo >/dev/null || { echo "Falta git-filter-repo. Instala: pip install git-filter-repo"; exit 1; }

mkdir -p "$TRABAJO" && cd "$TRABAJO"
echo "== 1. Clon espejo"
git clone --mirror "$REPO" repo
cd repo

echo "== 2. Respaldo completo (reversible)"
git bundle create "$TRABAJO/respaldo-antes-de-purga.bundle" --all
git for-each-ref --format='%(refname) %(objectname)' > "$TRABAJO/refs-antes.txt"
echo "   respaldo en $TRABAJO/respaldo-antes-de-purga.bundle"
cat "$TRABAJO/refs-antes.txt"

echo "== 3. Purga"
git filter-repo --force --invert-paths --path index.html --path .DS_Store

echo "== 4. Recrear main (queda vacia: sus unicos commits eran los del index.html)"
if ! git show-ref --quiet refs/heads/main; then
  W="$(mktemp -d)"
  export GIT_WORK_TREE="$W" GIT_INDEX_FILE="$W/.idx"
  cat > "$W/README.md" <<'MD'
# webcafeina.github.io

Historial reescrito para eliminar un archivo que contenia una clave de la API de Gemini
publicada por error. La clave fue rotada; eliminarla del historial no la invalidaba.
MD
  printf '.DS_Store\n__pycache__/\n*.pyc\n' > "$W/.gitignore"
  git add -A
  TREE="$(git write-tree)"
  C="$(git commit-tree "$TREE" -m 'Reinicia main tras purgar una clave de API del historial')"
  git update-ref refs/heads/main "$C"
  unset GIT_WORK_TREE GIT_INDEX_FILE
  echo "   main recreada en $C"
fi

echo "== 5. Verificacion"
N1=$(git rev-list --all --objects | grep -c 'index.html' || true)
N2=$(git cat-file --batch-all-objects --batch 2>/dev/null | grep -c 'generativelanguage' || true)
echo "   blobs index.html restantes      : $N1 (debe ser 0)"
echo "   objetos con 'generativelanguage': $N2 (debe ser 0)"
git for-each-ref --format='   %(refname) %(objectname:short)' refs/heads/
[ "$N1" = "0" ] && [ "$N2" = "0" ] || { echo "VERIFICACION FALLIDA: no se sube nada."; exit 1; }

if [ $SUBIR -eq 0 ]; then
  echo
  echo "Simulacro terminado. Nada subido. Para aplicarlo de verdad:"
  echo "  bash $0 --subir"
  exit 0
fi

echo "== 6. Subida forzada (reescribe el historial publico)"
git remote set-url --push origin "$REPO"
for b in main claude/affectionate-noether-lfsQ6 claude/ecstatic-hawking-xttlsz; do
  git show-ref --quiet "refs/heads/$b" && git push --force origin "refs/heads/$b:refs/heads/$b"
done

echo "== 7. Comprobacion contra el remoto"
cd "$TRABAJO" && git clone --mirror "$REPO" comprobacion
cd comprobacion
echo -n "   index.html en el remoto: "; git rev-list --all --objects | grep -c 'index.html' || true

cat <<'FIN'

Hecho en el repositorio. Falta, y no lo hace este script:
  1. Rotar la clave en https://aistudio.google.com/apikey (si no lo hiciste ya).
  2. Revisar consumo y facturacion de la clave antigua.
  3. Pedir a GitHub Support la purga de vistas cacheadas de los commits eliminados.
  4. Revisar si esa clave esta tambien en otros repos, gists, despliegues o copias.

Revertir:  git push --force origin <sha-de-refs-antes.txt>:refs/heads/<rama>
FIN
