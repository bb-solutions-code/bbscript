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


def test_accepts_control_link_fields():
    doc = validate_bbs_document(
        {
            "version": "2.0",
            "kind": "bbscript",
            "blocks": [
                {"id": "sw", "block": "switch", "args": {}, "output": "selected"},
                {"id": "pro", "block": "test_const", "args": {}, "output": "pro_out"},
                {"id": "default_node", "block": "test_const", "args": {}, "output": "def_out"},
            ],
            "links": [
                {"source": "sw", "target": "pro", "link_type": "control", "case": "pro"},
                {"source": "sw", "target": "default_node", "link_type": "control", "default": True},
            ],
        }
    )
    assert len(doc.links) == 2
    assert doc.links[0].link_type == "control"
    assert doc.links[0].case == "pro"
    assert doc.links[1].default is True


def test_rejects_case_on_data_link():
    with pytest.raises(BBScriptValidationError, match="only allowed for control links"):
        validate_bbs_document(
            {
                "version": "2.0",
                "kind": "bbscript",
                "blocks": [
                    {"id": "a", "block": "test_const", "args": {}, "output": "a_out"},
                    {"id": "b", "block": "test_const", "args": {}, "output": "b_out"},
                ],
                "links": [{"source": "a", "target": "b", "case": "x"}],
            }
        )


def test_rejects_duplicate_control_case_per_source():
    with pytest.raises(BBScriptValidationError, match="duplicate case values"):
        validate_bbs_document(
            {
                "version": "2.0",
                "kind": "bbscript",
                "blocks": [
                    {"id": "sw", "block": "switch", "args": {}, "output": "selected"},
                    {"id": "b1", "block": "test_const", "args": {}, "output": "o1"},
                    {"id": "b2", "block": "test_const", "args": {}, "output": "o2"},
                ],
                "links": [
                    {"source": "sw", "target": "b1", "link_type": "control", "case": "pro"},
                    {"source": "sw", "target": "b2", "link_type": "control", "case": "pro"},
                ],
            }
        )


def test_rejects_multiple_default_control_branches():
    with pytest.raises(BBScriptValidationError, match="more than one default"):
        validate_bbs_document(
            {
                "version": "2.0",
                "kind": "bbscript",
                "blocks": [
                    {"id": "sw", "block": "switch", "args": {}, "output": "selected"},
                    {"id": "b1", "block": "test_const", "args": {}, "output": "o1"},
                    {"id": "b2", "block": "test_const", "args": {}, "output": "o2"},
                ],
                "links": [
                    {"source": "sw", "target": "b1", "link_type": "control", "default": True},
                    {"source": "sw", "target": "b2", "link_type": "control", "default": True},
                ],
            }
        )


def test_rejects_control_links_from_non_control_block():
    with pytest.raises(BBScriptValidationError, match="only supported from 'if' or 'switch'"):
        validate_bbs_document(
            {
                "version": "2.0",
                "kind": "bbscript",
                "blocks": [
                    {"id": "a", "block": "test_const", "args": {}, "output": "a_out"},
                    {"id": "b", "block": "test_const", "args": {}, "output": "b_out"},
                ],
                "links": [{"source": "a", "target": "b", "link_type": "control", "case": "x"}],
            }
        )


def test_if_control_links_only_allow_boolean_case():
    with pytest.raises(BBScriptValidationError, match="only allow boolean case"):
        validate_bbs_document(
            {
                "version": "2.0",
                "kind": "bbscript",
                "blocks": [
                    {"id": "cond", "block": "if", "args": {}, "output": "cond_out"},
                    {"id": "yes", "block": "test_const", "args": {}, "output": "y_out"},
                ],
                "links": [{"source": "cond", "target": "yes", "link_type": "control", "case": "yes"}],
            }
        )

