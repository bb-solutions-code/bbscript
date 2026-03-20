"""Block registry for BBScript runtime."""

from __future__ import annotations

from typing import Dict, Type

from .block_base import Block

BLOCK_REGISTRY: Dict[str, Type[Block]] = {}


class BlockRegistry:
    def __init__(self) -> None:
        self._registry = BLOCK_REGISTRY

    def register(self, block_cls: Type[Block]) -> Type[Block]:
        if not getattr(block_cls, "name", None):
            raise ValueError("Block class must define a non-empty `name` attribute")
        self._registry[block_cls.name] = block_cls
        return block_cls

    def get(self, name: str) -> Type[Block]:
        if name not in self._registry:
            raise KeyError(f"Block '{name}' not found. Available blocks: {list(self._registry.keys())}")
        return self._registry[name]


def register_block(block_cls: Type[Block]) -> Type[Block]:
    BlockRegistry().register(block_cls)
    return block_cls


def get_block(name: str) -> Type[Block]:
    return BlockRegistry().get(name)

