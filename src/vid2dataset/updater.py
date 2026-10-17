"""Update checker and one-click installer for vid2dataset.

Queries the GitHub releases API to detect newer versions, downloads
the new .exe, verifies its SHA256 against the release, and writes a small
batch script that swaps it on next launch (you can't replace a running
.exe on Windows directly).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from vid2dataset import __version__

log = logging.getLogger(__name__)

GITHUB_OWNER = "Rinne414"
GITHUB_REPO = "vid2dataset"
RELEASES_API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases"
SHA256SUMS_NAME = "SHA256SUMS.txt"


class UpdateVerificationError(Exception):
    """The downloaded update could not be proven to match the release."""


@dataclass(frozen=True)
class ReleaseInfo:
    tag: str            # e.g. "v0.2.0"
    version: str        # e.g. "0.2.0"
    name: str           # release title
    notes: str          # markdown body
    exe_url: str | None # download URL of vid2dataset.exe asset
    exe_size: int       # bytes
    exe_name: str = "vid2dataset.exe"
    exe_digest: str | None = None   # lowercase sha256 hex from the API ``digest`` field
    sums_url: str | None = None     # SHA256SUMS.txt asset, fallback when no digest


def _parse_version(s: str) -> tuple[int, ...]:
    """'v0.2.0' -> (0, 2, 0). Returns (0,) on parse failure."""
    s = s.lstrip("v")
    parts = s.split(".")
    out: list[int] = []
    for p in parts:
        try:
            out.append(int(p.split("-")[0]))  # strip pre-release suffixes
        except ValueError:
            break
    return tuple(out) if out else (0,)


def fetch_latest_release(timeout: float = 10.0) -> ReleaseInfo | None:
    """Query GitHub for the latest release. Returns None on network failure."""
    try:
        req = urllib.request.Request(
            RELEASES_API,
            headers={"User-Agent": f"vid2dataset/{__version__}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        log.warning("Update check failed: %s", e)
        return None

    return parse_release(data)


def _sha256_from_digest(digest: str | None) -> str | None:
    """'sha256:ABC...' -> 'abc...'. None for missing or non-sha256 values."""
    if not digest or not digest.lower().startswith("sha256:"):
        return None
    hex_part = digest.split(":", 1)[1].strip().lower()
    return hex_part if len(hex_part) == 64 else None


def parse_release(data: dict) -> ReleaseInfo:
    """Build a ReleaseInfo from a GitHub releases API payload."""
    tag = data.get("tag_name", "")
    version = tag.lstrip("v")
    exe: dict = {}
    sums_url = None
    for asset in data.get("assets", []):
        name = asset.get("name", "")
        if not exe and name.lower().endswith(".exe"):
            exe = asset
        elif name.lower() == SHA256SUMS_NAME.lower():
            sums_url = asset.get("browser_download_url")

    return ReleaseInfo(
        tag=tag,
        version=version,
        name=data.get("name", tag),
        notes=data.get("body", ""),
        exe_url=exe.get("browser_download_url"),
        exe_size=int(exe.get("size", 0)),
        exe_name=exe.get("name", "vid2dataset.exe"),
        exe_digest=_sha256_from_digest(exe.get("digest")),
        sums_url=sums_url,
    )


def is_newer(remote_version: str, local_version: str = __version__) -> bool:
    """Return True if remote_version is newer than local_version."""
    return _parse_version(remote_version) > _parse_version(local_version)


def is_running_as_exe() -> bool:
    """True if we are running from a PyInstaller bundle."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def download_exe(
    url: str,
    dest: Path,
    progress_cb: callable | None = None,
    timeout: float = 60.0,
) -> Path:
    """Download an .exe to ``dest``. Calls ``progress_cb(bytes_done, total)``."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": f"vid2dataset/{__version__}"})

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        done = 0
        with tmp.open("wb") as f:
            while True:
                chunk = resp.read(64 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                if progress_cb:
                    progress_cb(done, total)

    tmp.replace(dest)
    return dest


def _fetch_text(url: str, timeout: float = 15.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": f"vid2dataset/{__version__}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _sha256_from_sums(text: str, filename: str) -> str | None:
    """Find ``filename`` in ``<hex>  <name>`` lines (``*`` binary marker allowed)."""
    for line in text.splitlines():
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        digest, name = parts[0].lower(), parts[1].strip().lstrip("*")
        if name == filename and len(digest) == 64:
            return digest
    return None


def resolve_expected_sha256(release: ReleaseInfo) -> str | None:
    """API ``digest`` first, then the release's SHA256SUMS.txt. None if neither."""
    if release.exe_digest:
        return release.exe_digest
    if release.sums_url:
        try:
            return _sha256_from_sums(_fetch_text(release.sums_url), release.exe_name)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            log.warning("Could not read %s: %s", SHA256SUMS_NAME, e)
    return None


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def download_verified_exe(
    release: ReleaseInfo,
    dest: Path,
    progress_cb: callable | None = None,
) -> Path:
    """Download the release exe and prove it matches the release before use.

    Raises ``UpdateVerificationError`` (and leaves no file at ``dest``) when
    the expected hash cannot be found, the size differs, or the SHA256 differs.
    """
    dest.unlink(missing_ok=True)
    expected = resolve_expected_sha256(release)
    if expected is None:
        raise UpdateVerificationError("no checksum published for this release")

    download_exe(release.exe_url, dest, progress_cb=progress_cb)
    try:
        actual_size = dest.stat().st_size
        if release.exe_size and actual_size != release.exe_size:
            raise UpdateVerificationError(
                f"size {actual_size} does not match release size {release.exe_size}"
            )
        if _sha256_of_file(dest) != expected:
            raise UpdateVerificationError("SHA256 does not match the release")
    except BaseException:
        dest.unlink(missing_ok=True)
        raise
    return dest


def install_update(new_exe: Path) -> None:
    """Stage an update for the currently-running .exe.

    On Windows you can't replace a running .exe. We write a small .bat that:
      1) waits for our process to exit
      2) replaces the old .exe with the new one
      3) starts the new .exe
      4) deletes itself

    The .bat is started detached, then this process should exit.
    """
    if not is_running_as_exe():
        raise RuntimeError("install_update only works when running from a .exe")

    current_exe = Path(sys.executable).resolve()
    bat_path = current_exe.parent / "vid2dataset_update.bat"
    pid = os.getpid()

    bat = f"""@echo off
:wait
tasklist /FI "PID eq {pid}" 2>NUL | find "{pid}" >NUL
if not errorlevel 1 (
    timeout /t 1 /nobreak >NUL
    goto wait
)
move /Y "{new_exe}" "{current_exe}" >NUL
start "" "{current_exe}"
del "%~f0"
"""
    bat_path.write_text(bat, encoding="utf-8")

    # Launch the updater detached and exit our process
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    import subprocess
    subprocess.Popen(
        ["cmd", "/c", str(bat_path)],
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True,
    )
