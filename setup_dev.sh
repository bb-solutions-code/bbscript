#!/usr/bin/env bash
# Create .venv in this repo, install bbscript and bbpm in editable mode.
# Default: include dev extras. Use --no-dev to skip dev optional dependencies.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT/.venv"
NO_DEV=false

for arg in "$@"; do
  case "$arg" in
    --no-dev) NO_DEV=true ;;
    -h|--help)
      echo "Usage: $0 [--no-dev]"
      echo "  Creates .venv, pip install -e bbscript and local bbpm (or bbpm from PyPI)."
      exit 0
      ;;
  esac
done

if [[ "${SETUP_DEV_NO_DEV:-}" == "1" ]]; then
  NO_DEV=true
fi

if [[ -x "$VENV/bin/python" ]]; then
  :
else
  echo "Creating venv at $VENV"
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv "$VENV"
  else
    python -m venv "$VENV"
  fi
fi

PY="$VENV/bin/python"
"$PY" -m pip install --upgrade pip

if [[ "$NO_DEV" == true ]]; then
  echo "Installing bbscript (editable, no dev extras)..."
  "$PY" -m pip install -e "$ROOT"
else
  echo "Installing bbscript (editable, with dev extras)..."
  "$PY" -m pip install -e "${ROOT}[dev]"
fi

NESTED="$ROOT/bbpm"
PARENT_BBPM="$(dirname "$ROOT")/bbpm"
BBPM_PATH=""
if [[ -f "$NESTED/pyproject.toml" ]]; then
  BBPM_PATH="$NESTED"
elif [[ -f "$PARENT_BBPM/pyproject.toml" ]]; then
  BBPM_PATH="$PARENT_BBPM"
fi

if [[ -n "$BBPM_PATH" ]]; then
  if [[ "$NO_DEV" == true ]]; then
    echo "Installing local bbpm from $BBPM_PATH (editable)..."
    "$PY" -m pip install -e "$BBPM_PATH"
  else
    echo "Installing local bbpm from $BBPM_PATH (editable, with dev extras)..."
    "$PY" -m pip install -e "${BBPM_PATH}[dev]"
  fi
else
  echo "Warning: no local bbpm at $NESTED or $PARENT_BBPM; installing bbpm from PyPI." >&2
  "$PY" -m pip install bbpm
fi

echo ""
echo "Done. Activate the environment:"
echo "  source .venv/bin/activate"
echo "Then run: bbscript --help   and   bbpm --help"
