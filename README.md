<p align="center">
  <img src="Assets/logo.svg" alt="BBScript logo" width="160" height="160" />
</p>

# BBScript

BBScript is a lightweight graph runtime and CLI for executing `.bbs` documents.
It focuses on core execution semantics (blocks, links, validation, and parallel DAG execution) without editor or API server dependencies.

## Related projects

- **[bbpm](https://github.com/bb-solutions-code/bbpm)** (BBScript Package Manager) — installs third-party `.bbpackage` repos and runs `.bbs` files with `bbpm run` so package blocks register alongside built-ins.
- **[foblox](https://github.com/bb-solutions-code/foblox)** — foundation blocks (`variable`, `calculate`, `say`, …); the minimal example below uses these block types when Foblox is available via bbpm or a local package path.

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
```

Executes reachable blocks from entry points with bounded parallelism and prints final context.

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

## Contributing

1. Create a branch for your change.
2. Add or update tests.
3. Run `python -m pytest -q`.
4. Keep public behavior and terminology consistent with BBScript (`block`, `link`, `.bbs`).
