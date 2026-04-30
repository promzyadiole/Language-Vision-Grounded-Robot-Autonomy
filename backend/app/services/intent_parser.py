from __future__ import annotations

import json

from app.models.schemas import ParsedIntent
from app.services.llm_service import LLMService


INTENT_SYSTEM_PROMPT = """
You are a robot command parser.

Return ONLY valid JSON with this schema:
{
  "intent": "...",
  "target_place": null or string,
  "route_name": null or string,
  "motion": null or string,
  "query": null or string,
  "response_text": "..."
}

Allowed intents:
- NAVIGATE_TO_PLACE
- FOLLOW_WAYPOINT_ROUTE
- MOVE_FORWARD
- MOVE_BACKWARD
- TURN_LEFT
- TURN_RIGHT
- ROTATE
- STOP
- GET_STATUS
- GET_POSE
- GET_PREVIOUS_POSE
- GET_LAST_COMMAND
- GET_SCAN_SUMMARY
- LIST_VISIBLE_OBJECTS
- SCENE_SUMMARY
- CAPTURE_FRAME
- UNKNOWN

Rules:
- Use NAVIGATE_TO_PLACE for commands like "go to the kitchen"
- Use FOLLOW_WAYPOINT_ROUTE for commands like "start patrol"
- Use direct motion intents for short relative motion
- Use GET_STATUS for robot state questions like:
  "what is your status", "are you moving", "what are you doing"
- Use GET_POSE for location/pose questions like:
  "where are you", "what is your position", "where am i"
- Use GET_PREVIOUS_POSE for questions like:
  "previous position", "previous pose", "last position", "where were you last time"
- Use GET_LAST_COMMAND for questions like:
  "last command", "what did i ask last", "what was my last command"
- Use GET_SCAN_SUMMARY for obstacle/proximity questions like:
  "is there an obstacle ahead", "what is in front of you"
- Use LIST_VISIBLE_OBJECTS for:
  "what objects do you see", "list visible objects"
- Use SCENE_SUMMARY for:
  "what do you see", "describe the scene", "describe your surroundings"
- Use CAPTURE_FRAME for:
  "capture image", "take a picture", "capture frame"
- Never invent coordinates
- Never invent place names beyond the user message
- If unclear, use UNKNOWN
"""


class IntentParser:
    def __init__(self) -> None:
        self.llm = LLMService()

    def parse(self, user_message: str) -> ParsedIntent:
        msg = user_message.lower().strip()

        if any(phrase in msg for phrase in [
            "where am i",
            "where are you",
            "current position",
            "current pose",
            "where is the robot",
        ]):
            return ParsedIntent(
                intent="GET_POSE",
                target_place=None,
                route_name=None,
                motion=None,
                query=user_message,
                response_text="I am determining my current location.",
            )

        if any(phrase in msg for phrase in [
            "previous position",
            "previous pose",
            "last position",
            "where was i before",
            "where was the robot before",
            "where was your last position before the current position",
            "where were you last time",
        ]):
            return ParsedIntent(
                intent="GET_PREVIOUS_POSE",
                target_place=None,
                route_name=None,
                motion=None,
                query=user_message,
                response_text="I am checking my last known position before the current one.",
            )

        if any(phrase in msg for phrase in [
            "last command",
            "what did i ask last",
            "what was my last command",
            "previous command",
        ]):
            return ParsedIntent(
                intent="GET_LAST_COMMAND",
                target_place=None,
                route_name=None,
                motion=None,
                query=user_message,
                response_text="I am checking the most recent command.",
            )

        raw = self.llm.chat_json(INTENT_SYSTEM_PROMPT, user_message)
        data = json.loads(raw)
        return ParsedIntent(**data)


_intent_parser: IntentParser | None = None


def get_intent_parser() -> IntentParser:
    global _intent_parser
    if _intent_parser is None:
        _intent_parser = IntentParser()
    return _intent_parser