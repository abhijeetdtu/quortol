r"""Sync local `.agents` files into the Opencode agents directory.

Windows destination:
    %USERPROFILE%\.config\opencode\agents

Linux destination:
    ~/.config/opencode/agents
"""

from __future__ import annotations

import hashlib
import platform
import shutil
from pathlib import Path


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_source_dir(repo_root: Path) -> Path:
    return repo_root / ".agents"


def get_destination_dir() -> Path:
    system = platform.system().lower()

    if system in {"windows", "linux"}:
        return Path.home() / ".config" / "opencode" / "agents"

    raise RuntimeError(f"Unsupported operating system: {platform.system()}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def needs_copy(src: Path, dst: Path) -> bool:
    if not dst.exists():
        return True

    if src.stat().st_size != dst.stat().st_size:
        return True

    return sha256(src) != sha256(dst)


def sync_agents(source_dir: Path, destination_dir: Path) -> tuple[int, int]:
    copied = 0
    skipped = 0

    destination_dir.mkdir(parents=True, exist_ok=True)

    for src_path in source_dir.rglob("*"):
        if not src_path.is_file():
            continue

        relative_path = src_path.relative_to(source_dir)
        dst_path = destination_dir / relative_path
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        if needs_copy(src_path, dst_path):
            shutil.copy2(src_path, dst_path)
            copied += 1
        else:
            skipped += 1

    return copied, skipped


def main() -> None:
    repo_root = get_repo_root()
    source_dir = get_source_dir(repo_root)
    destination_dir = get_destination_dir()

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    copied, skipped = sync_agents(source_dir, destination_dir)
    print(f"Synced from: {source_dir}")
    print(f"Synced to:   {destination_dir}")
    print(f"Copied: {copied}, Skipped: {skipped}")


if __name__ == "__main__":
    """python scripts/agent._sync.py"""
    main()
