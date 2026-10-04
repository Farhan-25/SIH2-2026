"""
run.py — ForenShield project launcher
Starts both the Python backend and the React frontend concurrently.
Cross-platform: Windows, Linux, macOS.

Usage:
    python run.py
    python run.py --backend-only
    python run.py --frontend-only
    python run.py --port 9000
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).parent.resolve()
BACKEND_FILE = ROOT / "backend.py"
FRONTEND_DIR = ROOT / "frontend"
VENV_DIR     = ROOT / "venv"
REQS_FILE    = ROOT / "requirements.txt"

IS_WIN = platform.system() == "Windows"
PYTHON = (VENV_DIR / ("Scripts" if IS_WIN else "bin") / "python").resolve()
PIP    = (VENV_DIR / ("Scripts" if IS_WIN else "bin") / "pip").resolve()

# Fallback to system python if venv not set up yet
if not PYTHON.exists():
    PYTHON = Path(sys.executable)
    PIP    = PYTHON.parent / "pip"

BANNER = """
╔══════════════════════════════════════════════════════════╗
║          ForenShield v2.0 — Digital Forensics            ║
║          SIH 2026  |  Python + React Full Stack          ║
╚══════════════════════════════════════════════════════════╝
"""

# ── Colour helpers (no deps) ───────────────────────────────────────────────────
def _c(code: str, text: str) -> str:
    """ANSI colour wrap — disabled on Windows without ANSI support."""
    if IS_WIN and not os.environ.get("WT_SESSION"):  # works in Windows Terminal
        return text
    return f"\033[{code}m{text}\033[0m"

def ok(msg: str):     print(_c("92", f"[OK]  {msg}"))
def info(msg: str):   print(_c("96", f"[..] {msg}"))
def warn(msg: str):   print(_c("93", f"[!!] {msg}"))
def error(msg: str):  print(_c("91", f"[XX] {msg}"))
def head(msg: str):   print(_c("95", f"\n  {msg}"))


# ── Dependency setup ───────────────────────────────────────────────────────────
def ensure_venv():
    if VENV_DIR.exists():
        return
    info("No virtual environment found. Creating venv...")
    subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    ok("Virtual environment created")


def ensure_python_deps():
    ensure_venv()
    try:
        result = subprocess.run(
            [str(PYTHON), "-c", "import fastapi, psutil, pydantic"],
            capture_output=True,
        )
        if result.returncode == 0:
            ok("Python dependencies already satisfied")
            return
    except Exception:
        pass
    info("Installing Python dependencies from requirements.txt ...")
    subprocess.check_call([str(PIP), "install", "-r", str(REQS_FILE), "--quiet"])
    ok("Python dependencies installed")


# (Node.js dependencies removed since we use Streamlit)
def ensure_node_deps():
    pass


# ── Process runners ────────────────────────────────────────────────────────────
_procs = []

def _stream(proc, label: str, colour: str):
    """Read lines from a subprocess and prefix them with a label."""
    try:
        for line in iter(proc.stdout.readline, b""):
            print(_c(colour, f"[{label}]") + " " + line.decode("utf-8", errors="replace").rstrip())
    except Exception:
        pass


def start_backend(port: int) -> subprocess.Popen:
    head("Starting backend  →  http://127.0.0.1:{port}".format(port=port))
    env = {**os.environ, "PORT": str(port)}
    proc = subprocess.Popen(
        [str(PYTHON), str(BACKEND_FILE)],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    _procs.append(proc)
    t = threading.Thread(target=_stream, args=(proc, "BACKEND", "94"), daemon=True)
    t.start()
    return proc


def start_frontend() -> subprocess.Popen:
    head("Starting frontend  →  http://localhost:8501")
    proc = subprocess.Popen(
        [str(PYTHON), "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"],
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    _procs.append(proc)
    t = threading.Thread(target=_stream, args=(proc, "FRONTEND", "92"), daemon=True)
    t.start()
    return proc


def wait_for_server(host: str, port: int, timeout: int = 30) -> bool:
    import socket
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def open_browser(url: str):
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="ForenShield project runner")
    parser.add_argument("--backend-only",  action="store_true", help="Start only the Python backend")
    parser.add_argument("--frontend-only", action="store_true", help="Start only the React frontend")
    parser.add_argument("--port",          type=int, default=8000, help="Backend port (default: 8000)")
    parser.add_argument("--no-browser",    action="store_true", help="Do not auto-open the browser")
    args = parser.parse_args()

    print(BANNER)

    # ── Install dependencies ──
    head("Checking dependencies")
    if not args.frontend_only:
        ensure_python_deps()
    if not args.backend_only:
        ensure_node_deps()

    print()
    info(f"Root:     {ROOT}")
    info(f"Backend:  {'enabled' if not args.frontend_only else 'skipped'}")
    info(f"Frontend: {'enabled' if not args.backend_only else 'skipped'}")
    print()

    # ── Start services ──
    backend_proc  = None
    frontend_proc = None

    try:
        if not args.frontend_only:
            backend_proc = start_backend(args.port)
            time.sleep(1.5)
            if wait_for_server("127.0.0.1", args.port, timeout=20):
                ok(f"Backend ready at http://127.0.0.1:{args.port}")
                ok(f"API docs:        http://127.0.0.1:{args.port}/docs")
            else:
                warn("Backend did not respond in 20s — check for errors above")

        if not args.backend_only:
            frontend_proc = start_frontend()
            time.sleep(2)
            if wait_for_server("127.0.0.1", 8501, timeout=20):
                ok("Frontend ready at http://localhost:8501")
                if not args.no_browser:
                    open_browser("http://localhost:8501")
            else:
                warn("Frontend did not respond in 20s — check for errors above")

        print()
        print(_c("95", "  Press Ctrl+C to stop all services"))
        print()

        # ── Keep alive ──
        while True:
            if backend_proc  and backend_proc.poll()  is not None:
                warn(f"Backend exited with code {backend_proc.returncode}")
                break
            if frontend_proc and frontend_proc.poll() is not None:
                warn(f"Frontend exited with code {frontend_proc.returncode}")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print()
        info("Shutting down ForenShield...")
    finally:
        for proc in _procs:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        ok("All services stopped. Goodbye!")


if __name__ == "__main__":
    main()
