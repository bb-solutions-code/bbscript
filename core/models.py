"""Canonical BBScript document models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class BlockInstance:
    id: str
    block: str
    args: Dict[str, Any] = field(default_factory=dict)
    output: str = ""


@dataclass(frozen=True)
class Link:
    source: str
    target: str


@dataclass(frozen=True)
class BBScriptDocument:
    version: str
    kind: str
    entry_blocks: Optional[List[str]]
    blocks: List[BlockInstance]
    links: List[Link]

