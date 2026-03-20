"""BBScript `.bbs` serialization helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .models import BBScriptDocument


def to_bbs_json(document: BBScriptDocument) -> Dict[str, object]:
    return {
        "version": document.version,
        "kind": document.kind,
        "entry_blocks": document.entry_blocks,
        "blocks": [
            {"id": b.id, "block": b.block, "args": b.args, "output": b.output} for b in document.blocks
        ],
        "links": [{"source": l.source, "target": l.target} for l in document.links],
    }


def write_bbs_document(path: str | Path, document: BBScriptDocument, *, indent: int = 2) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(to_bbs_json(document), f, ensure_ascii=False, indent=indent)

