"""Package the release assets and write SHA256SUMS.txt.

Run after ``python build_exe.py``. Produces, in ``dist/``:

    vid2dataset-<ver>-windows.zip   exe + start scripts + HOW_TO_START.txt
    SHA256SUMS.txt                  checksums of vid2dataset.exe and the zip

Upload vid2dataset.exe, the zip and SHA256SUMS.txt to the GitHub release.
The in-app updater checks the exe against the release ``digest`` or, when
that is missing, against SHA256SUMS.txt.

Usage:
    python scripts/make_release_assets.py
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DIST = HERE / "dist"
BUNDLE_FILES = ["HOW_TO_START.txt", "START.bat", "start.sh", "双击启动.bat"]


def _version() -> str:
    ns: dict = {}
    init = (HERE / "src" / "vid2dataset" / "__init__.py").read_text(encoding="utf-8")
    exec(next(line for line in init.splitlines() if line.startswith("__version__")), ns)
    return ns["__version__"]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    exe = DIST / "vid2dataset.exe"
    if not exe.exists():
        sys.exit("dist/vid2dataset.exe not found - run `python build_exe.py` first.")

    version = _version()
    folder = DIST / f"vid2dataset-{version}-windows"
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir()
    shutil.copy2(exe, folder / exe.name)
    for name in BUNDLE_FILES:
        shutil.copy2(HERE / name, folder / name)

    zip_path = DIST / f"{folder.name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(folder.iterdir()):
            zf.write(f, f.name)

    sums = DIST / "SHA256SUMS.txt"
    sums.write_text(
        "".join(f"{_sha256(p)}  {p.name}\n" for p in (exe, zip_path)), encoding="utf-8"
    )
    print(f"Wrote {zip_path.name} and {sums.name}")
    print(sums.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
