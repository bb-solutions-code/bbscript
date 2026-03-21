"""BBScript DAG runner with bounded parallelism and structured events."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, Future, wait, FIRST_COMPLETED
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set, List
import threading

from jinja2 import Template, UndefinedError

from .block_base import Block
from .events import EventSink, ExecutionEvent
from .loader import BBScriptValidationError
from .models import BBScriptDocument
from .registry import get_block
from .state import BlockExecutionStatus, BlockResult, ExecutionContext, ExecutionState, ExecutionStatus


def _render_templates(value: Any, context_vars: Dict[str, Any]) -> Any:
    if isinstance(value, str):
        template = Template(value)
        try:
            return template.render(**context_vars)
        except UndefinedError as e:
            var_name = getattr(e, "name", None) or getattr(e, "undefined_name", None) or "unknown"
            raise ValueError(
                f"Variable '{var_name}' not found in execution context when rendering '{value}'."
            ) from e
    if isinstance(value, dict):
        return {k: _render_templates(v, context_vars) for k, v in value.items()}
    if isinstance(value, list):
        return [_render_templates(v, context_vars) for v in value]
    return value


@dataclass(frozen=True)
class ExecutionResult:
    execution_id: Optional[str]
    context: Dict[str, Any]
    state: ExecutionState
    events: List[ExecutionEvent]


def run_bbs_document(
    document: BBScriptDocument,
    *,
    execution_id: Optional[str] = None,
    initial_context: Optional[Dict[str, Any]] = None,
    max_workers: int = 8,
    event_sink: Optional[EventSink] = None,
) -> ExecutionResult:
    if document.kind != "bbscript":
        raise BBScriptValidationError("Invalid document kind; expected 'bbscript'.")

    block_by_id = {b.id: b for b in document.blocks}
    reachable: Set[str] = set()
    outgoing: Dict[str, Set[str]] = {bid: set() for bid in block_by_id.keys()}
    incoming_sources: Dict[str, Set[str]] = {bid: set() for bid in block_by_id.keys()}
    for l in document.links:
        outgoing[l.source].add(l.target)
        incoming_sources[l.target].add(l.source)

    queue = list(document.entry_blocks or [])
    reachable.update(queue)
    while queue:
        current = queue.pop(0)
        for dep in outgoing.get(current, set()):
            if dep in block_by_id and dep not in reachable:
                reachable.add(dep)
                queue.append(dep)
    if not reachable:
        raise BBScriptValidationError("No reachable blocks found from entry_blocks.")

    entry_set = set(document.entry_blocks or [])
    remaining_deps: Dict[str, int] = {}
    dependents: Dict[str, Set[str]] = {bid: set() for bid in reachable}
    for bid in reachable:
        deps_in_reachable = incoming_sources.get(bid, set()) & reachable
        remaining_deps[bid] = len(deps_in_reachable)
        dependents[bid] = outgoing.get(bid, set()) & reachable
    for bid in entry_set & reachable:
        remaining_deps[bid] = 0

    state = ExecutionState(status=ExecutionStatus.RUNNING)
    for bid in reachable:
        state.block_statuses[bid] = BlockExecutionStatus.PENDING

    exec_context = ExecutionContext(variables=dict(initial_context or {}))
    events: List[ExecutionEvent] = []
    events_lock = threading.Lock()

    def emit(event: ExecutionEvent) -> None:
        if event_sink:
            event_sink(event)
        with events_lock:
            events.append(event)

    started: Set[str] = set()
    started_lock = threading.Lock()

    def run_block(block_id: str) -> BlockResult:
        block_instance = block_by_id[block_id]
        block_cls = get_block(block_instance.block)
        block_obj: Block = block_cls()  # type: ignore[call-arg]
        context_vars = exec_context.snapshot()
        rendered_args = _render_templates(block_instance.args, context_vars)
        result_value = block_obj.execute(args=rendered_args, context=context_vars)
        exec_context.set_var(block_instance.output, result_value)
        return BlockResult(block_id=block_id, output=block_instance.output, value=result_value)

    running: Dict[Future[BlockResult], str] = {}
    stop_scheduling = False

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for bid in [bid for bid in reachable if remaining_deps[bid] == 0]:
            with started_lock:
                if bid in started:
                    continue
                started.add(bid)
            state.set_block_status(bid, BlockExecutionStatus.RUNNING)
            emit(ExecutionEvent.now("block_started", execution_id=execution_id, block_id=bid, data={}))
            running[pool.submit(run_block, bid)] = bid

        while running:
            done, _pending = wait(list(running.keys()), return_when=FIRST_COMPLETED)
            for fut in done:
                bid = running.pop(fut)
                try:
                    block_result = fut.result()
                except Exception as e:
                    err_msg = str(e)
                    state.set_block_error(bid, err_msg)
                    emit(ExecutionEvent.now("block_failed", execution_id=execution_id, block_id=bid, data={"error": err_msg}))
                    state.set_failed(err_msg)
                    stop_scheduling = True
                    continue

                state.set_block_result(block_result)
                emit(ExecutionEvent.now("block_completed", execution_id=execution_id, block_id=bid, data={"output": block_result.output}))
                if stop_scheduling:
                    continue
                for dep_id in dependents.get(bid, set()):
                    if dep_id not in reachable:
                        continue
                    remaining_deps[dep_id] -= 1
                    if remaining_deps[dep_id] == 0:
                        with started_lock:
                            if dep_id in started:
                                continue
                            started.add(dep_id)
                        state.set_block_status(dep_id, BlockExecutionStatus.RUNNING)
                        emit(ExecutionEvent.now("block_started", execution_id=execution_id, block_id=dep_id, data={}))
                        running[pool.submit(run_block, dep_id)] = dep_id

    if state.status == ExecutionStatus.FAILED:
        emit(ExecutionEvent.now("execution_failed", execution_id=execution_id, data=state.errors))
    else:
        state.status = ExecutionStatus.COMPLETED
        emit(ExecutionEvent.now("execution_completed", execution_id=execution_id, data={}))

    return ExecutionResult(execution_id=execution_id, context=exec_context.variables, state=state, events=events)
