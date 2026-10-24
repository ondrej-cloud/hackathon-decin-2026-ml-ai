#!/bin/bash
# Čistá kopie k odevzdání: kód, výsledky, CSV, prezentace a dokumentace. Bez dat, vah modelů, .venv, interních
# souborů týmu a pracovních snímků decku a webu. Spouští se z kořene repa: bash odevzdani/vytvor.sh [cílová složka]
set -euo pipefail
CIL=${1:-../hackathon-2026-odevzdani}
TMP=$(mktemp -d)

.venv/bin/python src/export_csv.py > /dev/null

git ls-files -- app src web prezentace results models/ridge_intervaly.json data/external/README.md \
  data/external/nahled netlify.toml .streamlit/config.toml docs/grafy \
  docs/PREHLED.md docs/CESTA_MODELU.md docs/POKUSY.md docs/DENIK.md docs/DATA.md docs/POROZUMENI.md docs/WEB.md \
  ':!results/predpovedi' ':!results/csv' ':!docs/grafy/deck*' ':!docs/grafy/web*' ':!docs/grafy/ui*' > "$TMP/seznam"
mkdir "$TMP/kopie"
rsync -a --files-from="$TMP/seznam" . "$TMP/kopie/"
mkdir -p "$TMP/kopie/results/csv"
cp results/csv/*.csv "$TMP/kopie/results/csv/"
test -f odevzdani/README.md || { echo "chybí odevzdani/README.md"; exit 1; }
cp odevzdani/README.md "$TMP/kopie/README.md"
sed -i '' 's/, zapsáno do Stavu\././' "$TMP/kopie/docs/DENIK.md"
cp odevzdani/gitignore "$TMP/kopie/.gitignore"
cp odevzdani/requirements.txt "$TMP/kopie/requirements.txt"

mkdir -p "$CIL"
rsync -a --delete --exclude .git "$TMP/kopie/" "$CIL/"
rm -rf "$TMP"
echo "hotovo: $CIL ($(du -sh "$CIL" | cut -f1), $(find "$CIL" -type f -not -path '*/.git/*' | wc -l | tr -d ' ') souborů)"
