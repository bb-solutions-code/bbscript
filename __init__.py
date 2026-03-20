"""BBScript package entrypoint."""

from .core.loader import load_bbs_document, validate_bbs_document

__all__ = ["load_bbs_document", "validate_bbs_document"]

