from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PoseSnapshot:
    x: float
    y: float
    yaw: float
    frame_id: str
    timestamp: str


@dataclass
class CommandEvent:
    timestamp: str
    command: str
    command_type: str
    status: str
    pose_before: PoseSnapshot | None
    pose_after: PoseSnapshot | None
    result: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class StateStore:
    def __init__(self, max_pose_history: int = 100, max_event_history: int = 200) -> None:
        self._lock = Lock()

        self._current_pose: PoseSnapshot | None = None
        self._previous_pose: PoseSnapshot | None = None

        self._last_command: str | None = None
        self._last_command_type: str | None = None
        self._last_result: dict[str, Any] | None = None

        self._pose_history: deque[PoseSnapshot] = deque(maxlen=max_pose_history)
        self._event_history: deque[CommandEvent] = deque(maxlen=max_event_history)

        self._store: dict[str, Any] = {}

    def update_pose(self, x: float, y: float, yaw: float, frame_id: str = "map") -> None:
        with self._lock:
            snapshot = PoseSnapshot(
                x=x,
                y=y,
                yaw=yaw,
                frame_id=frame_id,
                timestamp=utc_now_iso(),
            )

            if self._current_pose is not None:
                self._previous_pose = deepcopy(self._current_pose)

            self._current_pose = snapshot
            self._pose_history.append(deepcopy(snapshot))

            self._store["amcl_pose"] = {
                "x": snapshot.x,
                "y": snapshot.y,
                "yaw": snapshot.yaw,
                "frame_id": snapshot.frame_id,
                "timestamp": snapshot.timestamp,
            }

    def set_last_command(self, command: str, command_type: str) -> None:
        with self._lock:
            self._last_command = command
            self._last_command_type = command_type
            self._store["last_command"] = command
            self._store["last_command_type"] = command_type

    def set_last_result(self, result: dict[str, Any]) -> None:
        with self._lock:
            self._last_result = deepcopy(result)
            self._store["last_result"] = deepcopy(result)

    def add_event(
        self,
        command: str,
        command_type: str,
        status: str,
        pose_before: PoseSnapshot | None,
        pose_after: PoseSnapshot | None,
        result: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        with self._lock:
            event = CommandEvent(
                timestamp=utc_now_iso(),
                command=command,
                command_type=command_type,
                status=status,
                pose_before=deepcopy(pose_before),
                pose_after=deepcopy(pose_after),
                result=deepcopy(result) if result else None,
                metadata=deepcopy(metadata) if metadata else None,
            )
            self._event_history.append(event)

    def get_current_pose(self) -> dict[str, Any] | None:
        with self._lock:
            return asdict(self._current_pose) if self._current_pose else None

    def get_previous_pose(self) -> dict[str, Any] | None:
        with self._lock:
            return asdict(self._previous_pose) if self._previous_pose else None

    def get_last_command(self) -> dict[str, Any] | None:
        with self._lock:
            if self._last_command is None:
                return None
            return {
                "command": self._last_command,
                "command_type": self._last_command_type,
            }

    def get_last_result(self) -> dict[str, Any] | None:
        with self._lock:
            return deepcopy(self._last_result)

    def get_pose_history(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._lock:
            items = list(self._pose_history)[-limit:]
            return [asdict(x) for x in reversed(items)]

    def get_event_history(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._lock:
            items = list(self._event_history)[-limit:]
            return [asdict(x) for x in reversed(items)]

    def get_summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "current_pose": asdict(self._current_pose) if self._current_pose else None,
                "previous_pose": asdict(self._previous_pose) if self._previous_pose else None,
                "last_command": self._last_command,
                "last_command_type": self._last_command_type,
                "last_result": deepcopy(self._last_result),
                "pose_history_count": len(self._pose_history),
                "event_history_count": len(self._event_history),
            }

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = deepcopy(value)

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            value = self._store.get(key, default)
            return deepcopy(value)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            data = deepcopy(self._store)

            if self._current_pose is not None:
                data["amcl_pose"] = asdict(self._current_pose)

            if self._last_command is not None:
                data["last_command"] = self._last_command
                data["last_command_type"] = self._last_command_type

            if self._last_result is not None:
                data["last_result"] = deepcopy(self._last_result)

            return data


_state_store: StateStore | None = None


def get_state_store() -> StateStore:
    global _state_store
    if _state_store is None:
        _state_store = StateStore()
    return _state_store


state_store = get_state_store()