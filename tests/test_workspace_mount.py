from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validar_carpeta.sh"
COMPOSE = ROOT / "infrastructure" / "docker-compose.yml"


def _validate(path: Path, *, home: Path) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment["HOME"] = str(home)
    return subprocess.run(
        ["bash", str(VALIDATOR), str(path)],
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )


def test_compose_usa_un_workspace_configurable() -> None:
    content = COMPOSE.read_text(encoding="utf-8")
    assert "${AULA_WORKSPACE:-../trabajo}" in content
    assert content.count("target: /workspace") == 1


def test_validador_acepta_subcarpeta_limpia(tmp_path: Path) -> None:
    home = tmp_path / "home"
    workspace = home / "proyectos" / "demo"
    workspace.mkdir(parents=True)
    result = _validate(workspace, home=home)
    assert result.returncode == 0
    assert Path(result.stdout.strip()) == workspace


def test_validador_rechaza_home_y_env(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    assert _validate(home, home=home).returncode != 0
    workspace = home / "demo"
    workspace.mkdir()
    (workspace / ".env").write_text("API_KEY=no-real\n", encoding="utf-8")
    result = _validate(workspace, home=home)
    assert result.returncode != 0
    assert "contiene .env" in result.stderr


def test_validador_rechaza_symlink(tmp_path: Path) -> None:
    home = tmp_path / "home"
    target = home / "target"
    target.mkdir(parents=True)
    link = home / "link"
    link.symlink_to(target, target_is_directory=True)
    assert _validate(link, home=home).returncode != 0
