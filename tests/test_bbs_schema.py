import pytest

from bbscript.core.loader import validate_bbs_document, BBScriptValidationError


def test_valid_minimal_document():
    doc = validate_bbs_document(
        {
            "version": "2.0",
            "kind": "bbscript",
            "blocks": [{"id": "a", "block": "test_const", "args": {}, "output": "a_out"}],
            "links": [],
        }
    )
    assert doc.entry_blocks == ["a"]
    assert len(doc.blocks) == 1
    assert len(doc.links) == 0


def test_rejects_legacy_top_level_shape_steps():
    with pytest.raises(BBScriptValidationError):
        validate_bbs_document({"version": "2.0", "kind": "bbscript", "steps": [], "blocks": []})


def test_rejects_unknown_link_target():
    with pytest.raises(BBScriptValidationError):
        validate_bbs_document(
            {
                "version": "2.0",
                "kind": "bbscript",
                "blocks": [{"id": "a", "block": "test_const", "args": {}, "output": "a_out"}],
                "links": [{"source": "a", "target": "missing"}],
            }
        )

