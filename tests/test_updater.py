"""Update verification: a downloaded exe is only staged if its SHA256 matches."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from vid2dataset import updater
from vid2dataset.updater import UpdateVerificationError, parse_release

PAYLOAD = b"MZ fake vid2dataset.exe payload"
GOOD = hashlib.sha256(PAYLOAD).hexdigest()
BAD = "0" * 64


def _payload(digest: str | None = None, size: int = len(PAYLOAD), sums: bool = False) -> dict:
    exe = {
        "name": "vid2dataset.exe",
        "browser_download_url": "https://example.invalid/vid2dataset.exe",
        "size": size,
    }
    if digest is not None:
        exe["digest"] = digest
    assets = [exe]
    if sums:
        assets.append(
            {
                "name": "SHA256SUMS.txt",
                "browser_download_url": "https://example.invalid/SHA256SUMS.txt",
                "size": 100,
            }
        )
    return {"tag_name": "v9.9.9", "name": "v9.9.9", "body": "", "assets": assets}


def _stub_download(monkeypatch: pytest.MonkeyPatch, content: bytes = PAYLOAD) -> None:
    def fake(url: str, dest: Path, progress_cb=None, timeout: float = 60.0) -> Path:
        dest.write_bytes(content)
        return dest

    monkeypatch.setattr(updater, "download_exe", fake)


def test_digest_match_returns_downloaded_file(tmp_path, monkeypatch) -> None:
    _stub_download(monkeypatch)
    rel = parse_release(_payload(digest=f"sha256:{GOOD.upper()}"))
    dest = tmp_path / "vid2dataset_new.exe"
    assert updater.download_verified_exe(rel, dest) == dest
    assert dest.read_bytes() == PAYLOAD


def test_digest_mismatch_deletes_download(tmp_path, monkeypatch) -> None:
    _stub_download(monkeypatch)
    rel = parse_release(_payload(digest=f"sha256:{BAD}"))
    dest = tmp_path / "vid2dataset_new.exe"
    with pytest.raises(UpdateVerificationError):
        updater.download_verified_exe(rel, dest)
    assert not dest.exists()


def test_sha256sums_fallback_when_no_digest(tmp_path, monkeypatch) -> None:
    _stub_download(monkeypatch)
    sums = f"{BAD}  other.zip\n{GOOD}  vid2dataset.exe\n"
    monkeypatch.setattr(updater, "_fetch_text", lambda url, timeout=15.0: sums)
    rel = parse_release(_payload(sums=True))
    dest = tmp_path / "vid2dataset_new.exe"
    assert updater.download_verified_exe(rel, dest) == dest


def test_sha256sums_mismatch_is_refused(tmp_path, monkeypatch) -> None:
    _stub_download(monkeypatch)
    monkeypatch.setattr(
        updater, "_fetch_text", lambda url, timeout=15.0: f"{BAD}  vid2dataset.exe\n"
    )
    rel = parse_release(_payload(sums=True))
    dest = tmp_path / "vid2dataset_new.exe"
    with pytest.raises(UpdateVerificationError):
        updater.download_verified_exe(rel, dest)
    assert not dest.exists()


def test_no_hash_available_is_refused(tmp_path, monkeypatch) -> None:
    _stub_download(monkeypatch)
    rel = parse_release(_payload())
    dest = tmp_path / "vid2dataset_new.exe"
    with pytest.raises(UpdateVerificationError):
        updater.download_verified_exe(rel, dest)
    assert not dest.exists()


def test_size_mismatch_is_refused(tmp_path, monkeypatch) -> None:
    _stub_download(monkeypatch)
    rel = parse_release(_payload(digest=f"sha256:{GOOD}", size=len(PAYLOAD) + 1))
    dest = tmp_path / "vid2dataset_new.exe"
    with pytest.raises(UpdateVerificationError):
        updater.download_verified_exe(rel, dest)
    assert not dest.exists()
