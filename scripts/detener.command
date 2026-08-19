#!/bin/bash
# Apaga el aula. Los flujos de LangFlow y tu carpeta trabajo/ se conservan.
set -uo pipefail
cd "$(dirname "$0")/.."
docker compose -f infrastructure/docker-compose.yml down
echo ""
echo "  Aula apagada. Tu trabajo sigue en la carpeta trabajo/ y tus flujos"
echo "  de LangFlow reaparecerán en el próximo arranque."
read -r -p "Pulsa Enter para cerrar..."
