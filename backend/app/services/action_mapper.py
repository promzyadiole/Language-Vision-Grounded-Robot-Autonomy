from __future__ import annotations

from typing import Any, Dict, Optional

from app.models.schemas import ParsedIntent
from app.services.yaml_registry import YAMLRegistry, get_yaml_registry


class ActionMapper:
    def __init__(self, registry: YAMLRegistry) -> None:
        self.registry = registry

    def map_intent(self, parsed: ParsedIntent) -> Dict[str, Any]:
        if parsed.intent == "NAVIGATE_TO_PLACE":
            if not parsed.target_place:
                raise ValueError("Missing target_place for navigation intent.")
            place = self.registry.resolve_place(parsed.target_place)
            if not place:
                raise ValueError(f"Unknown place: {parsed.target_place}")
            return {
                "type": "nav_goal",
                "place_key": place["key"],
                "pose": place["pose"],
            }

        if parsed.intent == "FOLLOW_WAYPOINT_ROUTE":
            if not parsed.route_name:
                raise ValueError("Missing route_name for waypoint route.")
            route = self.registry.resolve_route(parsed.route_name)
            if not route:
                raise ValueError(f"Unknown route: {parsed.route_name}")
            return {
                "type": "waypoint_route",
                "route_name": parsed.route_name,
                "points": route["points"],
            }

        if parsed.intent in {
            "MOVE_FORWARD",
            "MOVE_BACKWARD",
            "TURN_LEFT",
            "TURN_RIGHT",
            "ROTATE",
            "STOP",
        }:
            motion_key_map = {
                "MOVE_FORWARD": "move_forward",
                "MOVE_BACKWARD": "move_backward",
                "TURN_LEFT": "turn_left",
                "TURN_RIGHT": "turn_right",
                "ROTATE": "rotate",
                "STOP": "stop",
            }
            motion_key = motion_key_map[parsed.intent]
            motion = self.registry.resolve_motion(motion_key)
            if not motion:
                raise ValueError(f"Unknown motion mapping: {motion_key}")
            return {
                "type": "motion",
                "motion_key": motion_key,
                "cmd_vel": motion["cmd_vel"],
            }

        if parsed.intent in {
            "GET_STATUS",
            "GET_POSE",
            "GET_SCAN_SUMMARY",
            "LIST_VISIBLE_OBJECTS",
            "SCENE_SUMMARY",
            "CAPTURE_FRAME",
        }:
            return {
                "type": "query",
                "query": parsed.intent,
            }

        return {
            "type": "unknown",
            "query": "UNKNOWN",
        }


_action_mapper: Optional[ActionMapper] = None


def get_action_mapper() -> ActionMapper:
    global _action_mapper
    if _action_mapper is None:
        registry = get_yaml_registry()
        _action_mapper = ActionMapper(registry)
    return _action_mapper