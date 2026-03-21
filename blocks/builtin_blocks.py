"""Built-in blocks with no legacy workflow dependency."""

from __future__ import annotations

from typing import Any, Dict

from bbscript.core.block_base import Block
from bbscript.core.registry import register_block


@register_block("const")
class ConstBlock(Block):
    def run(self, args: Dict[str, Any], context: Dict[str, Any]) -> Any:
        return args.get("value")


@register_block("add")
class AddBlock(Block):
    def run(self, args: Dict[str, Any], context: Dict[str, Any]) -> Any:
        a = float(args.get("a", 0))
        b = float(args.get("b", 0))
        return a + b


@register_block("template_echo")
class TemplateBlock(Block):
    def run(self, args: Dict[str, Any], context: Dict[str, Any]) -> Any:
        return args.get("text", "")
