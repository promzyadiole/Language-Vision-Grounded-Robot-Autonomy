from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class YAMLRegistry:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(f"Registry file not found: {self.path}")

        with self.path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def reload(self) -> None:
        self.data = self._load()

    def resolve_place(self, name: str) -> Optional[Dict[str, Any]]:
        name = name.strip().lower()

        for place_key, place_data in self.data.get("places", {}).items():
            aliases = [place_key] + place_data.get("aliases", [])
            aliases = [a.lower() for a in aliases]

            if name in aliases:
                return {"key": place_key, **place_data}

        return None

    def resolve_route(self, route_name: str) -> Optional[Dict[str, Any]]:
        route_name = route_name.strip().lower()

        for route_key, route_data in self.data.get("routes", {}).items():
            aliases = [route_key] + route_data.get("aliases", [])
            aliases = [a.lower() for a in aliases]

            if route_name in aliases:
                return {"key": route_key, **route_data}

        return None

    def resolve_motion(self, motion_name: str) -> Optional[Dict[str, Any]]:
        motion_name = motion_name.strip().lower()

        motions = self.data.get("motions", {})
        for motion_key, motion_data in motions.items():
            aliases = [motion_key] + motion_data.get("aliases", [])
            aliases = [a.lower() for a in aliases]

            if motion_name in aliases:
                return {"key": motion_key, **motion_data}

        return None

    def get_vision_labels(self) -> list[str]:
        return self.data.get("vision_labels", [])


_yaml_registry: Optional[YAMLRegistry] = None


def get_yaml_registry() -> YAMLRegistry:
    global _yaml_registry

    if _yaml_registry is None:
        registry_path = (
            Path(__file__).resolve().parent.parent / "data" / "robot_actions.yaml"
        )
        _yaml_registry = YAMLRegistry(registry_path)

    return _yaml_registry