"""Structured execution events for BBScript."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional, Callable
import time

EventType = Literal[
    "block_started",
    "block_completed",
    "block_failed",
    "execution_completed",
    "execution_failed",
]


@dataclass(frozen=True)
class ExecutionEvent:
    event_type: EventType
    ts: float
    execution_id: Optional[str]
    block_id: Optional[str]
    data: Dict[str, Any]

    @staticmethod
    def now(
        event_type: EventType,
        *,
        execution_id: Optional[str] = None,
        block_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> "ExecutionEvent":
        return ExecutionEvent(
            event_type=event_type,
            ts=time.time(),
            execution_id=execution_id,
            block_id=block_id,
            data=data or {},
        )


EventSink = Callable[[ExecutionEvent], None]

