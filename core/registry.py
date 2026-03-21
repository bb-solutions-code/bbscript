"""Block registry for BBScript runtime."""

from __future__ import annotations

from typing import Dict, Type

from .block_base import Block

BLOCK_REGISTRY: Dict[str, Type[Block]] = {}


class BlockRegistry:
    def __init__(self) -> None:
        self._registry = BLOCK_REGISTRY

    def register(self, block_cls: Type[Block]) -> Type[Block]:
        if not getattr(block_cls, "id", None):
            raise ValueError("Block class must define a non-empty `id` attribute")
        self._registry[block_cls.id] = block_cls
        return block_cls

    def get(self, block_id: str) -> Type[Block]:
        if block_id not in self._registry:
            raise KeyError(
                f"Block '{block_id}' not found. Available blocks: {list(self._registry.keys())}"
            )
        return self._registry[block_id]


def register_block(block_cls: Type[Block]) -> Type[Block]:
    BlockRegistry().register(block_cls)
    return block_cls


def get_block(block_id: str) -> Type[Block]:
    return BlockRegistry().get(block_id)
