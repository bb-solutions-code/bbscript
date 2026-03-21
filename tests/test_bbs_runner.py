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
