import threading

from bbscript.core.block_base import Block
from bbscript.core.runner import run_bbs_document
from bbscript.core.loader import validate_bbs_document
from bbscript.core.registry import register_block


@register_block("test_const")
class TestConst(Block):
    def run(self, args, context):
        return args["value"]


@register_block("test_add")
class TestAdd(Block):
    def run(self, args, context):
        return context[args["a_var"]] + context[args["b_var"]]


@register_block("switch")
class TestSwitch(Block):
    def run(self, args, context):
        return args["value"]


@register_block("if")
class TestIf(Block):
    def run(self, args, context):
        return bool(args["condition"])


def test_dag_execution_fan_in():
    doc = validate_bbs_document(
        {
            "version": "2.0",
            "kind": "bbscript",
            "blocks": [
                {"id": "a", "block": "test_const", "args": {"value": 1}, "output": "a_out"},
                {"id": "b", "block": "test_const", "args": {"value": 2}, "output": "b_out"},
                {"id": "c", "block": "test_add", "args": {"a_var": "a_out", "b_var": "b_out"}, "output": "c_out"},
            ],
            "links": [{"source": "a", "target": "c"}, {"source": "b", "target": "c"}],
        }
    )
    result = run_bbs_document(doc, max_workers=3)
    assert result.state.status.value == "completed"
    assert result.context["c_out"] == 3


_started_a = threading.Event()
_started_b = threading.Event()
_release = threading.Event()


@register_block("test_wait")
class TestWait(Block):
    def run(self, args, context):
        if args["id"] == "a":
            _started_a.set()
        else:
            _started_b.set()
        _release.wait(timeout=3)
        return args["id"]


def test_parallel_branches():
    _started_a.clear()
    _started_b.clear()
    _release.clear()
    doc = validate_bbs_document(
        {
            "version": "2.0",
            "kind": "bbscript",
            "blocks": [
                {"id": "a", "block": "test_wait", "args": {"id": "a"}, "output": "a_out"},
                {"id": "b", "block": "test_wait", "args": {"id": "b"}, "output": "b_out"},
            ],
            "links": [],
        }
    )
    result_holder = {}

    def _run():
        result_holder["r"] = run_bbs_document(doc, max_workers=2)

    t = threading.Thread(target=_run)
    t.start()
    assert _started_a.wait(timeout=1.5)
    assert _started_b.wait(timeout=1.5)
    _release.set()
    t.join(timeout=5)
    assert result_holder["r"].state.status.value == "completed"


def test_switch_routes_single_branch_and_skips_others():
    doc = validate_bbs_document(
        {
            "version": "2.0",
            "kind": "bbscript",
            "blocks": [
                {"id": "selector", "block": "test_const", "args": {"value": "pro"}, "output": "plan"},
                {"id": "sw", "block": "switch", "args": {"value": "{{ plan }}"}, "output": "selected"},
                {"id": "pro", "block": "test_const", "args": {"value": "PRO"}, "output": "pro_out"},
                {"id": "free", "block": "test_const", "args": {"value": "FREE"}, "output": "free_out"},
                {"id": "fallback", "block": "test_const", "args": {"value": "DEF"}, "output": "def_out"},
            ],
            "links": [
                {"source": "selector", "target": "sw"},
                {"source": "sw", "target": "pro", "link_type": "control", "case": "pro"},
                {"source": "sw", "target": "free", "link_type": "control", "case": "free"},
                {"source": "sw", "target": "fallback", "link_type": "control", "default": True},
            ],
        }
    )
    result = run_bbs_document(doc, max_workers=2)
    assert result.state.status.value == "completed"
    assert result.context["pro_out"] == "PRO"
    assert "free_out" not in result.context
    assert "def_out" not in result.context
    assert result.state.block_statuses["free"].value == "skipped"
    assert result.state.block_statuses["fallback"].value == "skipped"


def test_if_routes_true_branch():
    doc = validate_bbs_document(
        {
            "version": "2.0",
            "kind": "bbscript",
            "blocks": [
                {"id": "cond", "block": "if", "args": {"condition": True}, "output": "cond_out"},
                {"id": "then", "block": "test_const", "args": {"value": "THEN"}, "output": "then_out"},
                {"id": "else", "block": "test_const", "args": {"value": "ELSE"}, "output": "else_out"},
            ],
            "links": [
                {"source": "cond", "target": "then", "link_type": "control", "case": True},
                {"source": "cond", "target": "else", "link_type": "control", "case": False},
            ],
        }
    )
    result = run_bbs_document(doc)
    assert result.state.status.value == "completed"
    assert result.context["then_out"] == "THEN"
    assert "else_out" not in result.context
    assert result.state.block_statuses["else"].value == "skipped"


def test_switch_fails_when_no_match_and_no_default():
    doc = validate_bbs_document(
        {
            "version": "2.0",
            "kind": "bbscript",
            "blocks": [
                {"id": "selector", "block": "test_const", "args": {"value": "enterprise"}, "output": "plan"},
                {"id": "sw", "block": "switch", "args": {"value": "{{ plan }}"}, "output": "selected"},
                {"id": "pro", "block": "test_const", "args": {"value": "PRO"}, "output": "pro_out"},
            ],
            "links": [
                {"source": "selector", "target": "sw"},
                {"source": "sw", "target": "pro", "link_type": "control", "case": "pro"},
            ],
        }
    )
    result = run_bbs_document(doc)
    assert result.state.status.value == "failed"
    assert "No control branch matched" in result.state.errors["__execution__"]
