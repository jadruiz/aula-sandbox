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


def test_compose_langflow_escribe_en_ruta_propia_y_sin_login() -> None:
    content = COMPOSE.read_text(encoding="utf-8")
    # La imagen corre como UID 1000; /app/langflow es su directorio de datos.
    assert "LANGFLOW_CONFIG_DIR: /app/langflow" in content
    assert "langflow-datos:/app/langflow" in content
    assert "chown -R 1000:0 /app/langflow" in content
    assert "condition: service_completed_successfully" in content
    assert 'LANGFLOW_AUTO_LOGIN: "true"' in content
    # El puerto sigue en loopback: sin login sólo es aceptable si nadie más puede entrar.
    assert '"127.0.0.1:7860:7860"' in content


def test_scripts_windows_existen_y_no_montan_home() -> None:
    scripts = ROOT / "scripts"
    for name in ("arrancar.bat", "arrancar.ps1", "detener.bat", "detener.ps1",
                 "montar_carpeta.bat", "montar_carpeta.ps1", "validar_carpeta.ps1"):
        assert (scripts / name).is_file(), name
    validador = (scripts / "validar_carpeta.ps1").read_text(encoding="utf-8")
    assert "USERPROFILE" in validador
    assert "ReparsePoint" in validador
    assert ".env" in validador


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
