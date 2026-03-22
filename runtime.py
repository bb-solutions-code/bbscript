"""Runtime preparation: built-ins + bundled foundation (no bbpm required)."""

from __future__ import annotations


def prepare_core() -> None:
    """Import built-in blocks and load bundled foundation (PyInstaller / env) if present."""
    import bbscript.blocks  # noqa: F401

    from bbscript.bundled import load_bundled_foundation

    load_bundled_foundation()
