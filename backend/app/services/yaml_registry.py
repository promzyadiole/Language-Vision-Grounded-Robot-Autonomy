from __future__ import annotations

from typing import Any, Dict, Optional

import yaml


class YAMLRegistry:
    def __init__(self, path: str) -> None:
        self.path = path
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        with open(self.path, "r", encoding="utf-8") as f:
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
        return self.data.get("routes", {}).get(route_name)

    def resolve_motion(self, motion_name: str) -> Optional[Dict[str, Any]]:
        return self.data.get("motions", {}).get(motion_name)

    def get_vision_labels(self) -> list[str]:
        return self.data.get("vision_labels", [])