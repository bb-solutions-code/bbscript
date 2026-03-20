"""BBScript runtime core."""

from .models import BBScriptDocument, BlockInstance, Link
from .loader import load_bbs_document, validate_bbs_document, BBScriptValidationError
from .executor import execute_bbs_document, ExecutionResult
from .registry import BlockRegistry, register_block, get_block, BLOCK_REGISTRY

__all__ = [
    "BBScriptDocument",
    "BlockInstance",
    "Link",
    "BBScriptValidationError",
    "load_bbs_document",
    "validate_bbs_document",
    "execute_bbs_document",
    "ExecutionResult",
    "BlockRegistry",
    "register_block",
    "get_block",
    "BLOCK_REGISTRY",
]

