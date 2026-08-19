#!/usr/bin/env bash
# Variante para Linux / terminal (misma lógica que arrancar.command, sin `open`).
set -uo pipefail
cd "$(dirname "$0")/.."
if ! docker info >/dev/null 2>&1; then
    echo "Docker no responde. Instala OrbStack (macOS) o Docker Engine y reintenta." >&2
    exit 1
fi
if [[ ! -f .env ]]; then
    cp .env.ejemplo .env
    echo "Creado .env — pega tu clave (OPENAI_API_KEY) y vuelve a ejecutar."
    exit 0
fi
if grep -q "PEGA-AQUI-TU-CLAVE" .env; then
    echo "El .env todavía tiene la clave de ejemplo. Edítalo y reintenta." >&2
    exit 1
fi
docker compose -f infrastructure/docker-compose.yml up -d --build
echo "JupyterLab: http://localhost:8888 · LangFlow: http://localhost:7860"
