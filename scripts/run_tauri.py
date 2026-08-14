"""Run the local Tauri CLI with Linux bundle compatibility settings."""

from __future__ import annotations

import os
import subprocess
import sys
import sysconfig
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _tauri_cli() -> Path:
    """Resolve the platform-specific Tauri CLI shim under ui/node_modules."""
    bin_dir = REPO_ROOT / "ui" / "node_modules" / ".bin"
    if sys.platform == "win32":
        for name in ("tauri.cmd", "tauri.exe", "tauri.ps1"):
            candidate = bin_dir / name
            if candidate.is_file():
                return candidate
    candidate = bin_dir / "tauri"
    if candidate.is_file():
        return candidate
    raise SystemExit("Tauri CLI is not installed; run pnpm install in ui first")


def _dev_python() -> Path:
    """Resolve the repo venv interpreter on Windows and Unix."""
    if sys.platform == "win32":
        candidates = (
            REPO_ROOT / "venv" / "Scripts" / "python.exe",
            REPO_ROOT / "venv" / "Scripts" / "python",
        )
    else:
        candidates = (
            REPO_ROOT / "venv" / "bin" / "python",
            REPO_ROOT / "venv" / "bin" / "python3",
        )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise SystemExit(
        "Dev venv Python not found. Create it first:\n"
        "  python -m venv venv\n"
        "  venv/Scripts/python -m pip install -e \".[dev]\"   # Windows\n"
        "  venv/bin/python -m pip install -e \".[dev]\"       # Linux/macOS"
    )


def main() -> int:
    tauri_cli = _tauri_cli()

    env = os.environ.copy()
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        env["VID2DATASET_PYTHON"] = str(_dev_python())
        env["VID2DATASET_BRIDGE_SCRIPT"] = str(REPO_ROOT / "bridge" / "main.py")
    if sys.platform.startswith("linux"):
        site_packages = Path(sysconfig.get_paths()["purelib"])
        wheel_libs = [
            site_packages / "scipy.libs",
            site_packages / "opencv_python.libs",
            site_packages / "numpy.libs",
        ]
        existing = env.get("LD_LIBRARY_PATH")
        paths = [str(path) for path in wheel_libs if path.is_dir()]
        if existing:
            paths.append(existing)
        env["LD_LIBRARY_PATH"] = os.pathsep.join(paths)

        # Tauri's cached linuxdeploy currently embeds an older strip that does
        # not understand RELR sections emitted by rolling-release toolchains.
        env.setdefault("NO_STRIP", "1")

    args = list(sys.argv[1:])
    if sys.platform == "win32" and tauri_cli.suffix.lower() in {".cmd", ".bat"}:
        # npm/pnpm Windows shims are batch files; invoke via cmd.exe.
        cmd = ["cmd", "/c", str(tauri_cli), *args]
    else:
        cmd = [str(tauri_cli), *args]
    return subprocess.call(cmd, cwd=REPO_ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
