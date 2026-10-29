"""Build the self-contained local API executable for the Tauri release bundle.

Run by the frontend's Tauri build command on Windows. The generated binary is
a build artifact and is intentionally not checked into Git.
"""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
RESOURCE_DIR = ROOT / "frontend" / "src-tauri" / "resources"


def run(*args: str, cwd: Path | None = None) -> None:
    subprocess.check_call(list(args), cwd=cwd)


def main() -> int:
    if sys.platform != "win32":
        print("The RITS release bundle currently targets Windows; skipping backend executable build.")
        return 0

    run(sys.executable, "-m", "pip", "install", "-e", str(BACKEND_DIR), "pyinstaller>=6.11,<7")
    run(
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile",
        "--name", "rits-backend",
        "--collect-all", "uvicorn",
        "--collect-all", "fastapi",
        "--collect-all", "pydantic",
        "--hidden-import", "rits.app",
        "--hidden-import", "rits.router",
        "--hidden-import", "rits.registry",
        "--hidden-import", "rits.models",
        "--paths", str(BACKEND_DIR),
        str(BACKEND_DIR / "rits" / "launcher.py"),
        cwd=BACKEND_DIR,
    )
    executable = BACKEND_DIR / "dist" / "rits-backend.exe"
    if not executable.is_file():
        raise FileNotFoundError(f"PyInstaller did not produce {executable}")
    RESOURCE_DIR.mkdir(parents=True, exist_ok=True)
    target = RESOURCE_DIR / "rits-backend.exe"
    shutil.copy2(executable, target)
    print(f"Bundled backend prepared at {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
