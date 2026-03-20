"""Core block contract for BBScript runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, List


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
    name: str
    display_name: Optional[str] = None
    category: str = "Utilities"

    @classmethod
    def get_display_name(cls) -> str:
        return cls.display_name or cls.name

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

