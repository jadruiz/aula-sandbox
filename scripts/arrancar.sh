#!/usr/bin/env bash
# Variante para Linux / terminal (misma lógica que arrancar.command, sin `open`).
set -uo pipefail
cd "$(dirname "$0")/.."

if ! AULA_WORKSPACE="$(scripts/validar_carpeta.sh "${1:-trabajo}")"; then
    exit 1
fi
export AULA_WORKSPACE

if ! docker info >/dev/null 2>&1; then
    echo "Docker no responde. Instala OrbStack (macOS) o Docker Engine y reintenta." >&2
    exit 1
fi
if [[ ! -f .env ]]; then
    cp .env.ejemplo .env
    chmod 600 .env
    echo "Creado .env sin credenciales: Aula continuará en modo offline."
elif grep -q "PEGA-AQUI-TU-CLAVE" .env; then
    # Compatibilidad con clones anteriores: sólo elimina el marcador didáctico, nunca una
    # clave que la persona haya escrito. Así el primer arranque no exige saber editar .env.
    temporal="$(mktemp "${TMPDIR:-/tmp}/aula-env.XXXXXX")"
    sed 's/sk-proj-PEGA-AQUI-TU-CLAVE//' .env > "$temporal"
    chmod 600 "$temporal"
    mv "$temporal" .env
    echo "Se quitó el marcador de ejemplo: Aula continuará en modo offline."
fi
docker compose -f infrastructure/docker-compose.yml up -d --build
echo "JupyterLab: http://localhost:8888 · LangFlow: http://localhost:7860"
echo "Carpeta montada: ${AULA_WORKSPACE}"
