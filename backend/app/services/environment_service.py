from __future__ import annotations

from typing import Any

from app.core.environment_loader import load_environment_config, load_places_config


class EnvironmentService:
    def __init__(self) -> None:
        self._environment = load_environment_config()
        self._places = load_places_config(self._environment)

    @property
    def environment(self) -> dict[str, Any]:
        return self._environment

    @property
    def places(self) -> dict[str, Any]:
        return self._places

    def get_place(self, name: str) -> dict[str, Any]:
        places = self._places.get("places", {})
        key = name.strip().lower().replace(" ", "_")
        if key not in places:
            available = ", ".join(sorted(places.keys()))
            raise ValueError(f"Unknown place '{name}'. Available places: {available}")
        return places[key]

    def list_places(self) -> dict[str, Any]:
        return self._places.get("places", {})


_environment_service: EnvironmentService | None = None


def get_environment_service() -> EnvironmentService:
    global _environment_service
    if _environment_service is None:
        _environment_service = EnvironmentService()
    return _environment_service