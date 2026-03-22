"""Discover and load foundation packages shipped next to the executable or via env."""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

from bbscript.bbpackage import find_root_bbpackage_file
from bbscript.errors import PackageLoadError
from bbscript.package_load import load_package_blocks


def _pyinstaller_bundle_root() -> Path | None:
    """Directory where PyInstaller places the app and `datas` (e.g. `foblox/`)."""
    if not getattr(sys, "frozen", False):
        return None
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return Path(sys.executable).resolve().parent


def _env_bundled_roots() -> list[Path]:
    raw = os.environ.get("BBSCRIPT_BUNDLED_PACKAGES", "").strip()
    if not raw:
        return []
    return [Path(p.strip()) for p in raw.split(os.pathsep) if p.strip()]


def discover_bundled_package_roots() -> list[Path]:
    """Return unique package root directories to load as bundled foundation (Foblox layout)."""
    roots: list[Path] = []
    br = _pyinstaller_bundle_root()
    if br is not None:
        embedded = br / "foblox"
        if embedded.is_dir():
            roots.append(embedded)
    roots.extend(_env_bundled_roots())

    seen: set[Path] = set()
    out: list[Path] = []
    for r in roots:
        try:
            resolved = r.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        if not resolved.is_dir():
            continue
        try:
            find_root_bbpackage_file(resolved)
        except PackageLoadError:
            continue
        seen.add(resolved)
        out.append(resolved)
    return out


def load_bundled_foundation() -> None:
    """Load block packages from the embedded bundle and/or ``BBSCRIPT_BUNDLED_PACKAGES``."""
    for root in discover_bundled_package_roots():
        try:
            load_package_blocks(root, package_name="foblox")
        except PackageLoadError as e:
            warnings.warn(
                f"Bundled foundation at {root} could not be loaded: {e}",
                UserWarning,
                stacklevel=2,
            )
