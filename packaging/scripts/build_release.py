#!/usr/bin/env python3
"""Build frozen bbscript + bbpm bundle (PyInstaller) and duplicate primary exe as bbpm."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    """Root of the bbscript repository (directory containing this `packaging/` tree)."""
    return Path(__file__).resolve().parents[2]


def _bbpm_src(root: Path) -> Path:
    """`./bbpm` (CI: multi-checkout next to bbscript) or `../bbpm` (local sibling clone)."""
    nested = root / "bbpm"
    if nested.is_dir():
        return nested
    return root.parent / "bbpm"


def _foblox_src(root: Path) -> Path:
    """`./foblox` or `../foblox` (same rule as bbpm)."""
    nested = root / "foblox"
    if nested.is_dir():
        return nested
    return root.parent / "foblox"


def venv_python(root: Path) -> Path:
    if sys.platform == "win32":
        return root / "Scripts" / "python.exe"
    return root / "bin" / "python"


def ensure_venv(venv_dir: Path) -> Path:
    py = venv_python(venv_dir)
    if not py.is_file():
        venv_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    return py


def write_foblox_ref(root: Path) -> None:
    ref = os.environ.get("FOBLOX_REF", "").strip()
    out = root / "packaging" / "BUNDLED_FOBLOX_REF"
    foblox = _foblox_src(root)
    if not ref:
        try:
            r = subprocess.run(
                ["git", "-C", str(foblox), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
            )
            if r.returncode == 0:
                ref = r.stdout.strip()
        except OSError:
            ref = ""
    if not ref:
        ref = "unknown"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(ref + "\n", encoding="utf-8")


def main() -> int:
    root = repo_root()
    spec = root / "packaging" / "pyinstaller" / "bbscript_bundle.spec"
    req_build = root / "packaging" / "requirements-build.txt"
    if not spec.is_file():
        print(f"Missing spec: {spec}", file=sys.stderr)
        return 1

    bbpm = _bbpm_src(root)
    if not bbpm.is_dir():
        print(
            f"Expected bbpm checkout at {root / 'bbpm'} or {root.parent / 'bbpm'}",
            file=sys.stderr,
        )
        return 1

    write_foblox_ref(root)

    venv_dir = root / "packaging" / ".venv-build"
    py = ensure_venv(venv_dir)
    subprocess.run(
        [str(py), "-m", "pip", "install", "--upgrade", "pip", "-q"],
        check=True,
    )
    subprocess.run(
        [str(py), "-m", "pip", "install", "-q", "-r", str(req_build)],
        check=True,
    )
    subprocess.run(
        [str(py), "-m", "pip", "install", "-q", str(root), str(bbpm)],
        check=True,
    )

    pyinstaller = [str(py), "-m", "PyInstaller", "--noconfirm", "--clean", str(spec)]
    cwd = root / "packaging" / "pyinstaller"
    print("Running:", " ".join(pyinstaller), file=sys.stderr)
    subprocess.run(pyinstaller, cwd=cwd, check=True)

    bundle_dir = cwd / "dist" / "bbscript-bundle"
    if sys.platform == "win32":
        primary = bundle_dir / "bbscript.exe"
        secondary = bundle_dir / "bbpm.exe"
    else:
        primary = bundle_dir / "bbscript"
        secondary = bundle_dir / "bbpm"

    if not primary.is_file():
        print(f"Expected {primary} after build", file=sys.stderr)
        return 1

    shutil.copy2(primary, secondary)
    if sys.platform != "win32":
        mode = secondary.stat().st_mode
        secondary.chmod(mode | 0o111)

    print(f"Wrote {secondary}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
