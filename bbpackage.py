"""Discover and parse root `.bbpackage` manifests (shared with bbpm)."""

from __future__ import annotations

import json
from pathlib import Path

from bbscript.errors import PackageLoadError


def find_root_bbpackage_file(package_root: Path) -> Path:
    """Root aggregate package: `*.bbpackage` in `package_root` with a `blocks` list."""
    if not package_root.is_dir():
        raise PackageLoadError(f"Not a directory: {package_root}")
    candidates = sorted(package_root.glob("*.bbpackage"))
    if not candidates:
        raise PackageLoadError(f"No .bbpackage file found in {package_root}")
    for c in candidates:
        if c.parent != package_root:
            continue
        try:
            data = json.loads(c.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            raise PackageLoadError(f"Invalid JSON in {c}: {e}") from e
        if isinstance(data.get("blocks"), list):
            return c
    return candidates[0]


def read_root_manifest(package_root: Path) -> dict:
    root_file = find_root_bbpackage_file(package_root)
    try:
        data = json.loads(root_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise PackageLoadError(f"Invalid JSON in {root_file}: {e}") from e
    if not isinstance(data, dict):
        raise PackageLoadError(f"{root_file} must contain a JSON object.")
    return data


def read_package_name(package_root: Path) -> str:
    data = read_root_manifest(package_root)
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise PackageLoadError(f"Root .bbpackage in {package_root} must define non-empty `name`.")
    return name.strip()
