<p align="center">
  <img src="Assets/logo.svg" alt="BBScript logo" width="160" height="160" />
</p>

# BBScript

BBScript is a lightweight graph runtime and CLI for executing `.bbs` documents.
It focuses on core execution semantics (blocks, links, validation, and parallel DAG execution) without editor or API server dependencies.

## Related projects

- **[bbpm](https://github.com/bb-solutions-code/bbpm)** (BBScript Package Manager) — installs third-party `.bbpackage` repos under `.bbpm/`; with `bbpm` installed, `bbscript run` loads those packages alongside built-ins and any bundled foundation.
- **[foblox](https://github.com/bb-solutions-code/foblox)** — foundation blocks (`variable`, `calculate`, `say`, …); the minimal example below uses these block types when Foblox is available (bundled path, `BBSCRIPT_BUNDLED_PACKAGES`, or a project installed via bbpm).

## Project Layout

```text
bbscript/
  __init__.py
  cli.py
  core/
    __init__.py
    block_base.py
    runner.py
    events.py
    loader.py
    models.py
    registry.py
    serializer.py
    state.py
  blocks/
    __init__.py
    builtin_blocks.py
  tests/
    test_bbs_schema.py
    test_bbs_runner.py
  pyproject.toml
  pytest.ini
  setup_dev.ps1
  setup_dev.sh
```

## Requirements

- Python 3.10+
- `pip` for dependency installation

## Installation

From the `bbscript` directory:

```bash
python -m pip install -e .
```

For development dependencies:

```bash
python -m pip install -e .[dev]
```

### Development environment (venv, bbscript + bbpm)

To create a local `.venv`, install this package in editable mode, and install **[bbpm](https://github.com/bb-solutions-code/bbpm)** when a checkout exists next to this repo (`../bbpm`) or under `bbscript/bbpm`, use one of:

**Windows (PowerShell)** — from the `bbscript` directory:

```powershell
.\setup_dev.ps1
```

Optional: `.\setup_dev.ps1 -NoDev` to skip optional `dev` dependencies for both packages.

**Linux / macOS** — from the `bbscript` directory:

```bash
chmod +x setup_dev.sh
./setup_dev.sh
```

Optional: `./setup_dev.sh --no-dev`, or `SETUP_DEV_NO_DEV=1 ./setup_dev.sh`.

If no local `bbpm` tree is found, the script installs `bbpm` from PyPI (which also pulls a release build of `bbscript` as a dependency; for working on both codebases side by side, clone `bbpm` next to this repository).

Activate the venv before running the CLIs:

- Windows: `.\.venv\Scripts\Activate.ps1`
- Unix: `source .venv/bin/activate`

## CLI Usage

The project exposes the `bbscript` CLI entrypoint.

### Validate

```bash
bbscript validate path/to/script.bbs
```

Validates `.bbs` schema and graph correctness.

### Inspect

```bash
bbscript inspect path/to/script.bbs
```

Prints normalized graph metadata (version, kind, entry blocks, blocks, links).

### Run

```bash
bbscript run path/to/script.bbs
bbscript run path/to/script.bbs --path /path/to/project
```

Executes reachable blocks from entry points with bounded parallelism and prints final context.

`bbscript run` always loads built-in blocks and, when present, bundled foundation from a frozen app layout or **`BBSCRIPT_BUNDLED_PACKAGES`**. If **[bbpm](https://github.com/bb-solutions-code/bbpm)** is installed, packages under `.bbpm/` are loaded too; if not, a short notice is printed to stderr and `.bbpm` packages are skipped.

## Minimal `.bbs` Example

```json
{
  "version": "2.0",
  "kind": "bbscript",
  "blocks": [
    {
      "id": "num_1",
      "block": "variable",
      "args": { "value": 3 },
      "output": "a"
    },
    {
      "id": "num_2",
      "block": "variable",
      "args": { "value": 4 },
      "output": "b"
    },
    {
      "id": "sum",
      "block": "calculate",
      "args": { "a": "{{ a }}", "b": "{{ b }}", "operation": "+" },
      "output": "result"
    }
  ],
  "links": [
    { "source": "const_1", "target": "sum" },
    { "source": "const_2", "target": "sum" }
  ]
}
```

Typical flow:
- `validate` confirms schema and graph.
- `inspect` displays normalized blocks and links.
- `run` returns `execution_status: completed` and includes `result: 7.0` in final context.

## Testing

Run tests from the `bbscript` directory:

```bash
python -m pytest -q
```

## Development Notes

- Runtime semantics live in `core/`.
- Built-in block implementations live in `blocks/`.
- A Python `Block` subclass registers with `@register_block("<block_type>")`, where `<block_type>` matches the document’s `"block"` string for that block type. Alternatively, you can use `@register_block` with no arguments and set a class attribute `id` (legacy style).
- The base `Block` class does not define UI-oriented fields such as `display_name` or `category`; add them on subclasses if you need them.
- Documents are strict `.bbs` JSON with `kind = "bbscript"` and `version = "2.0"`.
- Keep comments and documentation in English.
- Add tests for any behavior changes, especially loader validation and runner scheduling.

## Packaging

Frozen CLI bundles (`bbscript` + `bbpm` + embedded Foblox) and installers are documented in [`packaging/README.md`](packaging/README.md).

## Contributing

1. Create a branch for your change.
2. Add or update tests.
3. Run `python -m pytest -q`.
4. Keep public behavior and terminology consistent with BBScript (`block`, `link`, `.bbs`).
