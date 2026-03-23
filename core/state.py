"""Runtime state models for BBScript execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict
import threading


class BlockExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BlockResult:
    block_id: str
    output: str
    value: Any


@dataclass
class ExecutionContext:
    variables: Dict[str, Any] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self.variables)

    def set_var(self, name: str, value: Any) -> None:
        with self._lock:
            self.variables[name] = value


@dataclass
class ExecutionState:
    status: ExecutionStatus = ExecutionStatus.RUNNING
    block_statuses: Dict[str, BlockExecutionStatus] = field(default_factory=dict)
    results: Dict[str, BlockResult] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def set_block_status(self, block_id: str, new_status: BlockExecutionStatus) -> None:
        with self._lock:
            self.block_statuses[block_id] = new_status

    def set_block_error(self, block_id: str, error_message: str) -> None:
        with self._lock:
            self.errors[block_id] = error_message
            self.block_statuses[block_id] = BlockExecutionStatus.FAILED

    def set_block_result(self, block_result: BlockResult) -> None:
        with self._lock:
            self.results[block_result.block_id] = block_result
            self.block_statuses[block_result.block_id] = BlockExecutionStatus.COMPLETED

    def set_block_skipped(self, block_id: str) -> None:
        with self._lock:
            # Preserve terminal statuses for already processed blocks.
            if self.block_statuses.get(block_id) in {
                BlockExecutionStatus.COMPLETED,
                BlockExecutionStatus.FAILED,
            }:
                return
            self.block_statuses[block_id] = BlockExecutionStatus.SKIPPED

    def set_failed(self, error_message: str) -> None:
        with self._lock:
            self.status = ExecutionStatus.FAILED
            self.errors["__execution__"] = error_message

