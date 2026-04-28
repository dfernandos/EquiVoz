"""Fixtures E2E Playwright + subida automática de Flask (8000) e Vite (5173) se estiverem parados."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest
from pytest import Config

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"


@pytest.fixture
def email_unico() -> str:
    """E-mail único por execução; use domínio aceito por <input type=\"email\"> (ex. example.com)."""
    return f"e2e_{int(time.time() * 1000)}@example.com"


def _tcp_listening(host: str, port: int, timeout: float = 0.3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _wait_http(url: str, timeout_s: float = 120) -> None:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=3)
            return
        except (urllib.error.URLError, OSError) as e:
            last_err = e
            time.sleep(0.4)
    raise RuntimeError(f"Timeout aguardando {url} (último erro: {last_err})")


def _backend_python() -> Path:
    unix = BACKEND / ".venv" / "bin" / "python"
    if unix.exists():
        return unix
    win = BACKEND / ".venv" / "Scripts" / "python.exe"
    if win.exists():
        return win
    return Path(sys.executable)


@pytest.fixture(scope="session", autouse=True)
def _ensure_dev_servers():
    """Se 8000/5173 estiverem livres, sobe API e UI; no fim da sessão encerra só o que foi iniciado aqui."""
    if os.environ.get("E2E_SKIP_SERVERS") == "1":
        yield
        return

    procs: list[subprocess.Popen] = []

    need_api = not _tcp_listening("127.0.0.1", 8000)
    need_ui = not _tcp_listening("127.0.0.1", 5173)

    if need_api:
        py = _backend_python()
        if not (BACKEND / "app").is_dir():
            pytest.fail("Pasta backend/app não encontrada; não é possível subir o Flask.")
        proc = subprocess.Popen(
            [
                str(py),
                "-m",
                "flask",
                "--app",
                "app.main:create_app",
                "run",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            cwd=BACKEND,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={**os.environ},
        )
        procs.append(proc)
        try:
            _wait_http("http://127.0.0.1:8000/api/health")
        except RuntimeError:
            proc.kill()
            pytest.fail(
                "Flask não respondeu em :8000. Confira o venv do backend (pip install -r requirements.txt) "
                "ou suba manualmente: flask --app app.main:create_app run --port 8000"
            )

    if need_ui:
        if not (FRONTEND / "package.json").exists():
            pytest.fail("Pasta frontend/ não encontrada; não é possível subir o Vite.")
        proc = subprocess.Popen(
            ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173", "--strictPort"],
            cwd=FRONTEND,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={**os.environ},
        )
        procs.append(proc)
        try:
            _wait_http("http://127.0.0.1:5173/")
        except RuntimeError:
            for p in procs:
                p.kill()
            pytest.fail(
                "Vite não respondeu em :5173. Rode `npm install` em frontend/ ou suba manualmente: npm run dev"
            )

    yield

    for p in reversed(procs):
        p.terminate()
        try:
            p.wait(timeout=15)
        except subprocess.TimeoutExpired:
            p.kill()


@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig: Config) -> dict:
    """Sobrescreve o do pytest-playwright: janela visível por padrão (o --headed no ini às vezes não é lido)."""
    opts: dict = {}
    env_headless = os.environ.get("E2E_HEADLESS", "").lower() in ("1", "true", "yes")
    cli_headed = bool(pytestconfig.getoption("--headed"))
    # Abre o browser salvo se --headed OU se não pedimos headless por env
    mostrar_janela = cli_headed or not env_headless
    opts["headless"] = not mostrar_janela

    ch = pytestconfig.getoption("--browser-channel")
    if ch:
        opts["channel"] = ch
    sm = pytestconfig.getoption("--slowmo")
    if sm:
        opts["slow_mo"] = sm
    return opts


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "locale": "pt-BR",
        "timezone_id": "America/Sao_Paulo",
    }
