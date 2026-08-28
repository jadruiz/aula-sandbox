#!/bin/bash
# Arranca el aula. Doble clic en macOS. Mensajes pensados para quien no programa.
set -uo pipefail
cd "$(dirname "$0")/.."

COMPOSE=(docker compose -f infrastructure/docker-compose.yml)

if ! AULA_WORKSPACE="$(scripts/validar_carpeta.sh "${1:-trabajo}")"; then
    read -r -p "Pulsa Enter para cerrar..."
    exit 1
fi
export AULA_WORKSPACE

echo "════════════════════════════════════════════════════"
echo "  Aula · Ecosistemas Inteligentes"
echo "════════════════════════════════════════════════════"

# 1. ¿Está Docker (OrbStack) corriendo?
if ! docker info >/dev/null 2>&1; then
    echo ""
    echo "  Falta OrbStack (o no está abierto)."
    echo ""
    echo "  1. Descárgalo de https://orbstack.dev (te lo abro ahora)"
    echo "  2. Arrástralo a Aplicaciones y ábrelo una vez"
    echo "  3. Vuelve a hacer doble clic en este archivo"
    open "https://orbstack.dev" 2>/dev/null
    read -r -p "Pulsa Enter para cerrar..."
    exit 1
fi

# 2. ¿Existe el .env con la clave?
if [[ ! -f .env ]]; then
    cp .env.ejemplo .env
    chmod 600 .env
    echo ""
    echo "  Te acabo de crear .env sin credenciales. Aula continuará en modo offline."
elif grep -q "PEGA-AQUI-TU-CLAVE" .env; then
    # Compatibilidad con clones anteriores; el marcador no es una credencial real.
    temporal="$(mktemp "${TMPDIR:-/tmp}/aula-env.XXXXXX")"
    sed 's/sk-proj-PEGA-AQUI-TU-CLAVE//' .env > "$temporal"
    chmod 600 "$temporal"
    mv "$temporal" .env
    echo ""
    echo "  Se quitó el marcador de ejemplo. Aula continuará en modo offline."
fi

# 3. Levantar. La primera vez construye la imagen: 10-15 minutos es normal.
echo ""
echo "  Levantando contenedores (la primera vez tarda 10-15 min)..."
if ! "${COMPOSE[@]}" up -d --build; then
    echo ""
    echo "  Algo falló al levantar. Haz una captura de lo de arriba y"
    echo "  mándasela al instructor."
    read -r -p "Pulsa Enter para cerrar..."
    exit 1
fi

echo ""
echo "  Listo. Tus herramientas:"
echo ""
echo "    JupyterLab (labs de código) →  http://localhost:8888"
echo "    LangFlow  (agentes visuales) →  http://localhost:7860"
echo ""
echo "  Tu carpeta de trabajo es:  ${AULA_WORKSPACE}"
echo "  Para apagar todo: doble clic en scripts/detener.command"
open "http://localhost:8888" 2>/dev/null || true
sleep 3
open "http://localhost:7860" 2>/dev/null || true
read -r -p "Pulsa Enter para cerrar esta ventana (el aula sigue corriendo)..."
