# Packaging (frozen CLI + installers)

This directory contains scripts to build a **single PyInstaller onedir** with `bbscript` and `bbpm` (same bootloader; `bbpm` is a copy of `bbscript.exe` / `bbscript` with a different name — see `run_cli.py`), plus **embedded Foblox** from a sibling `foblox/` checkout or `./foblox` next to this repo.

## Prerequisites

- Python 3.10+
- Git (optional, for `BUNDLED_FOBLOX_REF` / `FOBLOX_REF`)
- **bbpm** and **foblox** repositories checked out next to this repo (`../bbpm`, `../foblox`) or as `bbpm/` and `foblox/` inside the workspace (as in CI).

## Build (all platforms)

From the **bbscript** repository root (the directory that contains `pyproject.toml` and this `packaging/` folder):

```bash
python packaging/scripts/build_release.py
```

This creates a venv under `packaging/.venv-build/`, installs `bbscript` and `bbpm` wheels, runs PyInstaller, and copies the primary binary to `bbpm` next to `bbscript`.

Output: `packaging/pyinstaller/dist/bbscript-bundle/` (`bbscript`, `bbpm`, `_internal/`, `foblox/`).

### Environment

- `FOBLOX_REF` — written to `packaging/BUNDLED_FOBLOX_REF` and bundled (optional file; omitted if absent).
- `BBSCRIPT_BUNDLED_PACKAGES` — at **runtime**, extra package roots for development (documented in the main `bbscript` / `bbpm` README).

## Tarball (macOS / Linux / Homebrew)

After `build_release.py`:

```bash
export BBSCRIPT_VERSION=0.2.0
python packaging/scripts/archive_bundle.py linux-x86_64
python packaging/scripts/archive_bundle.py darwin-arm64
python packaging/scripts/archive_bundle.py darwin-x64
```

Produces `dist/bbscript-<version>-<suffix>.tar.gz` with top-level folder `bbscript-bundle/`.

## Windows installer (Inno Setup)

Install [Inno Setup 6](https://jrsoftware.org/isinfo.php), then:

```powershell
packaging/windows/build_installer.ps1 -Version 0.2.0
```

Or compile manually after `build_release.py`:

```text
"%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" /DMyAppVersion=0.2.0 packaging\windows\BBScript.iss
```

Output: `packaging/windows/dist/BBScript-<version>-Setup.exe` (adds install directory to the **user** `PATH`).

## Homebrew

See [homebrew/Formula/bbscript.rb](homebrew/Formula/bbscript.rb). Copy into a tap repository (e.g. `bb-solutions-code/homebrew-bbscript`), update `url`/`sha256` from GitHub Release assets after publishing.

## CI

[`.github/workflows/release.yml`](../.github/workflows/release.yml) checks out **bbpm** and **foblox**, builds all targets on tag `v*`, and attaches `*.tar.gz` and the Windows Setup `.exe` to the GitHub release.
