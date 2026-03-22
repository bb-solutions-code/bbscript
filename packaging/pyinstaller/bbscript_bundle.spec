# -*- mode: python ; coding: utf-8 -*-
"""Frozen bundle: bbscript + bbpm + embedded Foblox; build bbpm.exe by copying bbscript.exe (see build_release.py)."""

from pathlib import Path

SPECDIR = Path(SPEC).resolve().parent
ROOT = SPECDIR.parent.parent


def _bbpm_src(root: Path) -> Path:
    nested = root / "bbpm"
    if nested.is_dir():
        return nested
    return root.parent / "bbpm"


def _foblox_src(root: Path) -> Path:
    nested = root / "foblox"
    if nested.is_dir():
        return nested
    return root.parent / "foblox"


FOBLOX = _foblox_src(ROOT)
REF_FILE = ROOT / "packaging" / "BUNDLED_FOBLOX_REF"

block_cipher = None

datas = []
if FOBLOX.is_dir():
    datas.append((str(FOBLOX), "foblox"))
if REF_FILE.is_file():
    datas.append((str(REF_FILE), "."))

# Primary graph: run_cli -> bbscript.cli / bbpm.cli -> bbpm.load -> bbscript.runtime.
# Also pin modules used only on the no-bbpm path (except ImportError in bbscript.cli.run),
# so Analysis does not omit them depending on PyInstaller version.
hiddenimports: list[str] = [
    "bbscript.runtime",
    "bbscript.bundled",
    "bbscript.package_load",
    "bbscript.bbpackage",
    "bbscript.errors",
]

a = Analysis(
    [str(SPECDIR / "run_cli.py")],
    pathex=[str(ROOT), str(_bbpm_src(ROOT))],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="bbscript",  # primary CLI name; copy to bbpm post-build
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="bbscript-bundle",
)
