#!/bin/sh
# Activa los hooks versionados de este repo.
#
# `core.hooksPath` vive en .git/config, que no se versiona: cada clon lo ejecuta una vez.
# Los hooks en sí sí están versionados, en scripts/hooks/, para que no diverjan entre clones.
set -eu
root="$(git rev-parse --show-toplevel)"
chmod +x "$root/scripts/hooks/"* "$root/scripts/check_no_ai_traces.py"
git -C "$root" config core.hooksPath scripts/hooks
echo "hooks activos: $(git -C "$root" config core.hooksPath)"
echo "verificación completa del árbol:  python3 scripts/check_no_ai_traces.py --all"
