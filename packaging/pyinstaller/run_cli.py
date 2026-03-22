"""Single frozen entry: dispatches to bbscript or bbpm by executable basename (bbscript.exe vs bbpm.exe)."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    stem = Path(sys.executable).resolve().stem.lower()
    if stem == "bbpm":
        from bbpm.cli import main as _main

        _main()
    else:
        from bbscript.cli import main as _main

        _main()


if __name__ == "__main__":
    main()
