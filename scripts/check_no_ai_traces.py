#!/usr/bin/env python3
"""Bloquea rastros de autoría por IA antes de que entren al repositorio.

Revisa tres superficies distintas, porque un rastro puede entrar por cualquiera:

1. **Rutas** — archivos de contexto o config de herramientas de agente (`CLAUDE.md`,
   `.claude/`, `.cursor/`…). El núcleo invariante declara un único `AGENTS.md`: ver
   ADR-005 en `milpa-sdk`.
2. **Contenido** — nombres comerciales, IDs de modelo y frases de atribución dentro de
   los archivos que se están confirmando.
3. **Metadatos del commit** — `Co-Authored-By`, footers de generación e identidad del
   autor o committer en un dominio de proveedor.

Sólo mira lo que **entra al commit** (el índice), no el árbol de trabajo: un archivo sin
`git add` no puede contaminar la historia.

Las excepciones legítimas se declaran en `governance/ai-trace-allowlist.txt`. Una excepción
sin razón escrita no es una excepción: es un agujero.

Uso:
    check_no_ai_traces.py                 # contenido y rutas en el índice (pre-commit)
    check_no_ai_traces.py --message F     # metadatos del commit (commit-msg)
    check_no_ai_traces.py --all           # árbol completo rastreado (CI)

Compatible con Python 3.9+ a propósito: el hook corre con el `python3` del sistema, que no
tiene por qué ser el del venv del proyecto.

Fuente canónica: `asilo-core/scripts/check_no_ai_traces.py`. Las copias en `milpa-sdk` y
`asilo-sandbox` deben mantenerse sincronizadas; su divergencia bloquea una release.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from typing import NamedTuple

SPEC_VERSION = "1.0.0"
ALLOWLIST = "governance/ai-trace-allowlist.txt"

# Extensiones que nunca se inspeccionan por contenido.
BINARY_SUFFIXES = (
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".tar",
    ".whl", ".so", ".dylib", ".pyc", ".woff", ".woff2", ".ttf", ".mp4", ".mov",
)

# --- Reglas de ruta ----------------------------------------------------------------
# Un archivo de contexto por proveedor reintroduce el acoplamiento que ADR-005 retiró.
PATH_RULES = (
    ("agent-context-file", ("CLAUDE.md", "GEMINI.md", "COPILOT.md", ".cursorrules",
                            ".aider.conf.yml", ".windsurfrules"),
     "el núcleo invariante declara un único AGENTS.md (ADR-005)"),
    ("agent-tool-config", (".claude/*", ".cursor/*", ".aider*", ".codeium/*",
                           ".github/copilot-*", ".continue/*"),
     "la config local de herramientas de agente no se versiona"),
)

# --- Reglas de contenido -----------------------------------------------------------
# `\b` no sirve como frontera aquí: `_` es carácter de palabra, así que `\banthropic\b`
# NO matchea `ANTHROPIC_API_KEY` ni `claude_client`. Se usa una frontera explícita que
# sólo considera letras y dígitos, para que el guion bajo separe.
_B = r"(?<![A-Za-z0-9])"
_E = r"(?![A-Za-z0-9])"

# Para los nombres que también son palabras comunes (sonnet, opus, haiku, fable) se exige
# el prefijo del proveedor o un número de versión; sueltos no disparan.
CONTENT_RULES = (
    ("attribution",
     re.compile(r"co-?authored-by\s*:.*|generated\s+with\s+\[?|"
                r"\bwritten\s+by\s+(an?\s+)?(ai|assistant)\b|"
                r"\b(escrito|generado|redactado)\s+por\s+(una?\s+)?(ia|inteligencia artificial)\b|"
                r"🤖", re.IGNORECASE),
     "atribución de autoría a una IA"),
    ("vendor",
     re.compile(_B + r"(anthropic|openai|chatgpt|copilot|deepseek|perplexity)" + _E,
                re.IGNORECASE),
     "nombre comercial de proveedor de IA"),
    ("model-id",
     re.compile(_B + r"(claude|gpt|gemini|codex|llama|mistral|grok)[-._ ]?\d|"
                + _B + r"claude[-._ ](opus|sonnet|haiku|fable)" + _E + r"|"
                + _B + r"(claude|gemini)" + _E,
                re.IGNORECASE),
     "identificador de modelo comercial"),
)

MESSAGE_RULES = CONTENT_RULES

IDENT_RULE = re.compile(
    r"@(anthropic|openai|users\.noreply\.github)\.com|noreply@anthropic", re.IGNORECASE
)


class Finding(NamedTuple):
    path: str
    line: int
    rule: str
    reason: str
    excerpt: str


class Exception_(NamedTuple):
    glob: str
    pattern: str
    reason: str


# --- git ---------------------------------------------------------------------------

def git(*args: str) -> str:
    out = subprocess.run(("git", *args), capture_output=True, check=False)
    if out.returncode != 0:
        return ""
    return out.stdout.decode("utf-8", errors="replace")


def repo_root() -> str:
    return git("rev-parse", "--show-toplevel").strip()


def staged_paths() -> list[str]:
    raw = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    return [p for p in raw.split("\0") if p]


def tracked_paths() -> list[str]:
    raw = git("ls-files", "-z")
    return [p for p in raw.split("\0") if p]


def blob(path: str, staged: bool) -> str | None:
    if path.lower().endswith(BINARY_SUFFIXES):
        return None
    data = subprocess.run(
        ("git", "show", (":" + path) if staged else ("HEAD:" + path)),
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
    )
    if data.returncode != 0:
        return None
    if b"\0" in data.stdout[:8000]:
        return None
    return data.stdout.decode("utf-8", errors="replace")


# --- allowlist ---------------------------------------------------------------------

def load_exceptions(root: str) -> list[Exception_]:
    import os

    path = os.path.join(root, ALLOWLIST)
    if not os.path.exists(path):
        return []
    out: list[Exception_] = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            # El patrón es una regex y puede contener '|' (alternancia): se recorta el
            # primer campo por la izquierda y la razón por la derecha; lo de en medio,
            # tal cual, es el patrón.
            if line.count("|") < 2:
                print("allowlist: línea inválida (se requiere glob | patrón | razón): "
                      + line, file=sys.stderr)
                continue
            glob, rest = line.split("|", 1)
            pattern, reason = rest.rsplit("|", 1)
            glob, pattern, reason = glob.strip(), pattern.strip(), reason.strip()
            if not glob or not pattern or not reason:
                print("allowlist: campo vacío (glob, patrón y razón son obligatorios): "
                      + line, file=sys.stderr)
                continue
            out.append(Exception_(glob, pattern, reason))
    return out


def allowed(path: str, text: str, excs: Sequence[Exception_]) -> bool:
    for e in excs:
        if not fnmatch.fnmatch(path, e.glob):
            continue
        try:
            if re.search(e.pattern, text, re.IGNORECASE):
                return True
        except re.error:
            continue
    return False


# --- escaneo -----------------------------------------------------------------------

def scan_path(path: str, excs: Sequence[Exception_]) -> list[Finding]:
    import os

    base = os.path.basename(path)
    found: list[Finding] = []
    for rule, globs, reason in PATH_RULES:
        for g in globs:
            if fnmatch.fnmatch(base, g) or fnmatch.fnmatch(path, g):
                if allowed(path, path, excs):
                    return []
                found.append(Finding(path, 0, rule, reason, path))
                return found
    return found


def scan_content(path: str, text: str, excs: Sequence[Exception_]) -> list[Finding]:
    found: list[Finding] = []
    for n, line in enumerate(text.splitlines(), start=1):
        for rule, rx, reason in CONTENT_RULES:
            m = rx.search(line)
            if not m:
                continue
            if allowed(path, line, excs):
                continue
            found.append(Finding(path, n, rule, reason, line.strip()[:100]))
            break
    return found


def report(findings: Iterable[Finding], root: str) -> int:
    findings = list(findings)
    if not findings:
        return 0
    print("\n\033[1;31mBLOQUEADO: rastro de IA en el commit\033[0m\n", file=sys.stderr)
    for f in findings:
        where = f.path if f.line == 0 else f"{f.path}:{f.line}"
        print(f"  {where}\n    [{f.rule}] {f.reason}\n    > {f.excerpt}\n",
              file=sys.stderr)
    print(f"{len(findings)} hallazgo(s).\n", file=sys.stderr)
    print(f"Si alguno es legítimo, decláralo con su razón en:\n  {ALLOWLIST}\n"
          "  formato:  glob | patrón | razón\n", file=sys.stderr)
    print("Para saltarlo una vez (queda en el reflog):  git commit --no-verify\n",
          file=sys.stderr)
    return 1


def check_message(path: str) -> list[Finding]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return []
    found: list[Finding] = []
    for n, line in enumerate(text.splitlines(), start=1):
        if line.startswith("#"):
            continue
        for rule, rx, reason in MESSAGE_RULES:
            if rx.search(line):
                found.append(Finding("<mensaje de commit>", n, rule, reason,
                                     line.strip()[:100]))
                break
    return found


def check_identity() -> list[Finding]:
    found: list[Finding] = []
    for var, label in (("GIT_AUTHOR_IDENT", "autor"), ("GIT_COMMITTER_IDENT", "committer")):
        ident = git("var", var).strip()
        if ident and IDENT_RULE.search(ident):
            found.append(Finding(f"<identidad: {label}>", 0, "identity",
                                 f"el {label} es una cuenta de proveedor de IA",
                                 ident))
    return found


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--message", metavar="ARCHIVO",
                    help="revisa el mensaje de commit y la identidad (hook commit-msg)")
    ap.add_argument("--all", action="store_true",
                    help="revisa todo el árbol rastreado en vez del índice (CI)")
    ap.add_argument("--version", action="store_true")
    args = ap.parse_args(argv)

    if args.version:
        print(SPEC_VERSION)
        return 0

    root = repo_root()
    if not root:
        print("no es un repositorio git", file=sys.stderr)
        return 1

    if args.message:
        return report(check_message(args.message) + check_identity(), root)

    excs = load_exceptions(root)
    paths = tracked_paths() if args.all else staged_paths()
    findings: list[Finding] = []
    for p in paths:
        findings.extend(scan_path(p, excs))
        text = blob(p, staged=not args.all)
        if text is not None:
            findings.extend(scan_content(p, text, excs))
    return report(findings, root)


if __name__ == "__main__":
    sys.exit(main())
