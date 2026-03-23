"""Canonical BBScript document models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


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
    link_type: Literal["data", "control"] = "data"
    case: Optional[Any] = None
    default: bool = False


@dataclass(frozen=True)
class BBScriptDocument:
    version: str
    kind: str
    entry_blocks: Optional[List[str]]
    blocks: List[BlockInstance]
    links: List[Link]

