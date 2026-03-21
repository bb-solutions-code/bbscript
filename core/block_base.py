"""Core block contract for BBScript runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List


@dataclass(frozen=True)
class BlockArgument:
    name: str
    type: str
    description: str = ""
    required: bool = True
    default: Any = None


@dataclass(frozen=True)
class BlockOutput:
    name: str
    type: str = "any"


class Block(ABC):
    # Block type key (matches `block` in .bbs); set via @register_block("...") or legacy `id = "..."`.
    id: ClassVar[str] = ""

    @classmethod
    def arguments(cls) -> List[BlockArgument]:
        return []

    @classmethod
    def output(cls) -> BlockOutput:
        return BlockOutput(name="output", type="any")

    @abstractmethod
    def run(self, args: Dict[str, Any], context: Dict[str, Any]) -> Any:
        pass

    def execute(self, args: Dict[str, Any], context: Dict[str, Any]) -> Any:
        return self.run(args=args, context=context)
