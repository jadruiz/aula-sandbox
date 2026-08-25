#!/usr/bin/env bash
# macOS: elegir una carpeta en Finder y arrancar Aula con un único bind mount.
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v osascript >/dev/null 2>&1; then
    echo "Este selector requiere macOS. En terminal usa:"
    echo "  scripts/arrancar.sh /ruta/a/tu/carpeta"
    read -r -p "Pulsa Enter para cerrar..."
    exit 1
fi

if ! CARPETA="$(osascript -e 'POSIX path of (choose folder with prompt "Elige la carpeta que verá Aula")')"; then
    exit 0
fi

exec scripts/arrancar.command "${CARPETA}"
