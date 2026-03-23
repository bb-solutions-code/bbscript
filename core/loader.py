"""BBScript `.bbs` loader and strict schema validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .models import BBScriptDocument, BlockInstance, Link


class BBScriptValidationError(ValueError):
    pass


def _is_non_empty_str(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _is_case_scalar(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) or value is None


def _validate_entry_blocks(entry_blocks: Any) -> Optional[List[str]]:
    if entry_blocks is None:
        return None
    if not isinstance(entry_blocks, list) or not all(isinstance(x, str) for x in entry_blocks):
        raise BBScriptValidationError("`entry_blocks` must be a list of strings.")
    cleaned = [x for x in entry_blocks if x.strip()]
    if not cleaned:
        raise BBScriptValidationError("`entry_blocks` must not be empty if provided.")
    return cleaned


def _validate_block_instance(raw: Any) -> BlockInstance:
    if not isinstance(raw, dict):
        raise BBScriptValidationError("Each item in `blocks` must be an object.")
    allowed_keys = {"id", "block", "args", "output"}
    extra_keys = set(raw.keys()) - allowed_keys
    if extra_keys:
        raise BBScriptValidationError(f"Unknown block field(s): {sorted(extra_keys)}")
    if "plugin" in raw:
        raise BBScriptValidationError("Legacy field `plugin` is not allowed in BBScript documents.")
    block_id = raw.get("id")
    block_type = raw.get("block")
    args = raw.get("args", {}) or {}
    output = raw.get("output", "")
    if not _is_non_empty_str(block_id):
        raise BBScriptValidationError("Each block must have non-empty string `id`.")
    if not _is_non_empty_str(block_type):
        raise BBScriptValidationError("Each block must have non-empty string `block`.")
    if not isinstance(args, dict):
        raise BBScriptValidationError("Block `args` must be an object.")
    if not _is_non_empty_str(output):
        raise BBScriptValidationError("Each block must have non-empty string `output`.")
    return BlockInstance(id=str(block_id), block=str(block_type), args=args, output=str(output))


def _validate_link(raw: Any, known_block_ids: Set[str]) -> Link:
    if not isinstance(raw, dict):
        raise BBScriptValidationError("Each item in `links` must be an object.")
    allowed_keys = {"source", "target", "link_type", "case", "default"}
    extra_keys = set(raw.keys()) - allowed_keys
    if extra_keys:
        raise BBScriptValidationError(f"Unknown link field(s): {sorted(extra_keys)}")
    source = raw.get("source")
    target = raw.get("target")
    if not _is_non_empty_str(source) or not _is_non_empty_str(target):
        raise BBScriptValidationError("Each link must have non-empty string `source` and `target`.")
    source = str(source)
    target = str(target)
    if source == target:
        raise BBScriptValidationError(f"Self-links are invalid: source == target == '{source}'.")
    if source not in known_block_ids or target not in known_block_ids:
        raise BBScriptValidationError(f"Link references unknown block id(s): '{source}' -> '{target}'.")
    link_type = raw.get("link_type", "data")
    if link_type not in {"data", "control"}:
        raise BBScriptValidationError("Link `link_type` must be either 'data' or 'control'.")
    case = raw.get("case")
    default = raw.get("default", False)
    if not isinstance(default, bool):
        raise BBScriptValidationError("Link `default` must be a boolean when provided.")
    if link_type == "data":
        if "case" in raw or "default" in raw:
            raise BBScriptValidationError("Link fields `case`/`default` are only allowed for control links.")
    else:
        if "case" in raw and not _is_case_scalar(case):
            raise BBScriptValidationError("Control link `case` must be a scalar value.")
    return Link(source=source, target=target, link_type=link_type, case=case, default=default)


def _validate_control_link_semantics(block_by_id: Dict[str, BlockInstance], links: List[Link]) -> None:
    grouped: Dict[str, List[Link]] = {}
    for l in links:
        if l.link_type != "control":
            continue
        grouped.setdefault(l.source, []).append(l)

    for source, control_links in grouped.items():
        source_block_type = block_by_id[source].block
        if source_block_type not in {"if", "switch"}:
            raise BBScriptValidationError(
                f"Control links are only supported from 'if' or 'switch' blocks, got '{source_block_type}' for '{source}'."
            )

        defaults = [l for l in control_links if l.default]
        if len(defaults) > 1:
            raise BBScriptValidationError(f"Control links from '{source}' define more than one default branch.")

        case_values = [l.case for l in control_links if l.case is not None]
        if len(case_values) != len(set(case_values)):
            raise BBScriptValidationError(f"Control links from '{source}' contain duplicate case values.")

        if source_block_type == "if":
            for l in control_links:
                if l.case is None and not l.default:
                    raise BBScriptValidationError(
                        f"Control link '{l.source}' -> '{l.target}' must define `case` or `default`."
                    )
                if l.case is not None and not isinstance(l.case, bool):
                    raise BBScriptValidationError("Control links from `if` blocks only allow boolean case values.")

            true_count = sum(1 for l in control_links if l.case is True)
            false_count = sum(1 for l in control_links if l.case is False)
            if true_count > 1 or false_count > 1:
                raise BBScriptValidationError("`if` block control links cannot define duplicate true/false branches.")


def _compute_incoming_edges(links: List[Link]) -> Dict[str, Set[str]]:
    incoming: Dict[str, Set[str]] = {}
    for l in links:
        incoming.setdefault(l.target, set()).add(l.source)
    return incoming


def _infer_entry_blocks(block_ids: Set[str], links: List[Link]) -> Set[str]:
    incoming = _compute_incoming_edges(links)
    return {bid for bid in block_ids if bid not in incoming}


def _detect_cycle(block_ids: Set[str], links: List[Link]) -> None:
    incoming = {bid: 0 for bid in block_ids}
    outgoing: Dict[str, List[str]] = {bid: [] for bid in block_ids}
    for l in links:
        outgoing[l.source].append(l.target)
        incoming[l.target] += 1
    ready = [bid for bid, deg in incoming.items() if deg == 0]
    processed = 0
    while ready:
        n = ready.pop()
        processed += 1
        for m in outgoing.get(n, []):
            incoming[m] -= 1
            if incoming[m] == 0:
                ready.append(m)
    if processed != len(block_ids):
        raise BBScriptValidationError("Graph contains a cycle; cyclic links are invalid.")


def validate_bbs_document(raw_doc: Dict[str, Any]) -> BBScriptDocument:
    if not isinstance(raw_doc, dict):
        raise BBScriptValidationError("Top-level JSON must be an object.")
    allowed_top_keys = {"version", "kind", "entry_blocks", "blocks", "links"}
    extra_keys = set(raw_doc.keys()) - allowed_top_keys
    if extra_keys:
        raise BBScriptValidationError(f"Unknown top-level field(s): {sorted(extra_keys)}")
    if "steps" in raw_doc or "connections" in raw_doc or "plugin" in raw_doc:
        raise BBScriptValidationError("Legacy workflow/WFUI shapes (`steps`/`connections`) are not allowed.")
    version = raw_doc.get("version")
    kind = raw_doc.get("kind")
    if not _is_non_empty_str(version):
        raise BBScriptValidationError("Top-level field `version` must be a non-empty string.")
    if version != "2.0":
        raise BBScriptValidationError("Only BBScript version '2.0' is supported.")
    if not _is_non_empty_str(kind) or kind != "bbscript":
        raise BBScriptValidationError("Top-level field `kind` must be exactly 'bbscript'.")
    entry_blocks = _validate_entry_blocks(raw_doc.get("entry_blocks"))
    raw_blocks = raw_doc.get("blocks")
    if not isinstance(raw_blocks, list) or not raw_blocks:
        raise BBScriptValidationError("Top-level field `blocks` must be a non-empty array.")
    blocks = [_validate_block_instance(b) for b in raw_blocks]
    block_ids = {b.id for b in blocks}
    block_by_id = {b.id: b for b in blocks}
    if len(block_ids) != len(blocks):
        raise BBScriptValidationError("Duplicate block `id` values are not allowed.")
    output_vars = [b.output for b in blocks]
    if len(output_vars) != len(set(output_vars)):
        raise BBScriptValidationError("Duplicate block `output` variable names are not allowed.")
    raw_links = raw_doc.get("links", [])
    if raw_links is None:
        raw_links = []
    if not isinstance(raw_links, list):
        raise BBScriptValidationError("Top-level field `links` must be an array.")
    links = [_validate_link(l, block_ids) for l in raw_links]
    _validate_control_link_semantics(block_by_id, links)
    _detect_cycle(block_ids, links)
    if entry_blocks is None:
        inferred = _infer_entry_blocks(block_ids, links)
        if not inferred:
            raise BBScriptValidationError("Could not infer entry blocks (no nodes with zero in-degree).")
        entry_blocks = sorted(inferred)
    else:
        unknown = set(entry_blocks) - block_ids
        if unknown:
            raise BBScriptValidationError(f"`entry_blocks` contains unknown block id(s): {sorted(unknown)}")
        entry_blocks = list(dict.fromkeys(entry_blocks))
    return BBScriptDocument(
        version=str(version),
        kind=str(kind),
        entry_blocks=entry_blocks,
        blocks=blocks,
        links=links,
    )


def load_bbs_document(path: str | Path) -> BBScriptDocument:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return validate_bbs_document(raw)

