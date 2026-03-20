"""Built-in blocks with no legacy workflow dependency."""

from __future__ import annotations

from typing import Any, Dict

from bbscript.core.block_base import Block
from bbscript.core.registry import register_block


@register_block
class ConstBlock(Block):
    name = "const"
    display_name = "Const"
    category = "Utilities"

    def run(self, args: Dict[str, Any], context: Dict[str, Any]) -> Any:
        return args.get("value")


@register_block
class AddBlock(Block):
    name = "add"
    display_name = "Add"
    category = "Math"

    def run(self, args: Dict[str, Any], context: Dict[str, Any]) -> Any:
        a = float(args.get("a", 0))
        b = float(args.get("b", 0))
        return a + b


@register_block
class TemplateBlock(Block):
    name = "template_echo"
    display_name = "Template Echo"
    category = "Text"

    def run(self, args: Dict[str, Any], context: Dict[str, Any]) -> Any:
        return args.get("text", "")

