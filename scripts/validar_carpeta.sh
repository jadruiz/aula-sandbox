#!/usr/bin/env bash
# Devuelve una única ruta canónica apta para montarse como /workspace.
set -euo pipefail

if [[ $# -ne 1 || -z "${1}" ]]; then
    echo "Uso: validar_carpeta.sh /ruta/a/la/carpeta" >&2
    exit 2
fi

CANDIDATA="${1}"
if [[ -L "${CANDIDATA}" ]]; then
    echo "La carpeta elegida no puede ser un enlace simbólico." >&2
    exit 2
fi
if [[ ! -d "${CANDIDATA}" ]]; then
    echo "La carpeta elegida no existe o no es un directorio: ${CANDIDATA}" >&2
    exit 2
fi

RESUELTA="$(cd "${CANDIDATA}" && pwd -P)"
USUARIO_HOME="${HOME:-}"

if [[ "${RESUELTA}" == "/" || ( -n "${USUARIO_HOME}" && "${RESUELTA}" == "${USUARIO_HOME}" ) ]]; then
    echo "No se permite montar la raíz ni tu carpeta personal completa." >&2
    exit 2
fi
if [[ -n "${USUARIO_HOME}" ]]; then
    case "${USUARIO_HOME}/" in
        "${RESUELTA}/"*)
            echo "La carpeta es demasiado amplia: contiene tu carpeta personal." >&2
            exit 2
            ;;
    esac
fi
if [[ -e "${RESUELTA}/.env" ]]; then
    echo "La carpeta contiene .env. Mueve los secretos fuera antes de montarla." >&2
    exit 2
fi

printf '%s\n' "${RESUELTA}"
