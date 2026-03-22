#!/usr/bin/env python3
"""Create bbscript-{version}-{suffix}.tar.gz from packaging/pyinstaller/dist/bbscript-bundle."""

from __future__ import annotations

import argparse
import os
import tarfile
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("suffix", help="e.g. linux-x86_64, darwin-arm64, darwin-x64")
    p.add_argument("--version", default=os.environ.get("BBSCRIPT_VERSION", "0.2.0"))
    p.add_argument("--out-dir", type=Path, default=None)
    args = p.parse_args()

    root = Path(__file__).resolve().parents[2]
    bundle = root / "packaging" / "pyinstaller" / "dist" / "bbscript-bundle"
    if not bundle.is_dir():
        print(f"Missing bundle dir: {bundle}", flush=True)
        return 1

    out_dir = args.out_dir or (root / "dist")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"bbscript-{args.version}-{args.suffix}.tar.gz"

    with tarfile.open(out, "w:gz") as tf:
        tf.add(bundle, arcname="bbscript-bundle")

    print(f"Wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
