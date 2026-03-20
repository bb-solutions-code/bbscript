"""BBScript CLI entry points."""

from __future__ import annotations

from pathlib import Path

import typer

from bbscript.core.loader import load_bbs_document
from bbscript.core.executor import execute_bbs_document
from bbscript import blocks as _builtin_blocks  # noqa: F401

app = typer.Typer(help="BBScript CLI.")


def _require_exists(path: str) -> Path:
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise typer.BadParameter(f"File not found: {path}")
    return p


@app.command()
def validate(path: str) -> None:
    """Validate a `.bbs` document schema and graph correctness."""
    p = _require_exists(path)
    doc = load_bbs_document(p)
    typer.echo(
        f"OK: validated BBScript document version={doc.version} blocks={len(doc.blocks)} links={len(doc.links)}"
    )


@app.command()
def inspect(path: str) -> None:
    """Print normalized BBScript graph information."""
    p = _require_exists(path)
    doc = load_bbs_document(p)

    typer.echo(f"version: {doc.version}")
    typer.echo(f"kind: {doc.kind}")
    typer.echo(f"entry_blocks: {doc.entry_blocks}")
    typer.echo("")
    typer.echo("blocks:")
    for b in doc.blocks:
        typer.echo(f"- id={b.id} block={b.block} output={b.output} args_keys={sorted(list(b.args.keys()))}")
    typer.echo("")
    typer.echo("links:")
    for l in doc.links:
        typer.echo(f"- {l.source} -> {l.target}")


@app.command()
def run(
    path: str,
    execution_id: str = typer.Option(None, help="Optional execution id for event correlation."),
    max_workers: int = typer.Option(8, help="Max parallel worker threads."),
) -> None:
    """Execute a `.bbs` document."""
    p = _require_exists(path)
    doc = load_bbs_document(p)
    result = execute_bbs_document(doc, execution_id=execution_id, max_workers=max_workers)
    typer.echo(f"execution_status: {result.state.status.value}")
    if result.state.errors.get("__execution__"):
        typer.echo(f"error: {result.state.errors['__execution__']}")
    typer.echo("")
    typer.echo("final_context:")
    for k, v in result.context.items():
        if isinstance(v, str) and len(v) > 300:
            typer.echo(f"- {k}: {v[:300]}...")
        else:
            typer.echo(f"- {k}: {v}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()

