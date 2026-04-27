from functools import lru_cache

from app.core.config import get_settings
from app.services.action_mapper import ActionMapper
from app.services.intent_parser import IntentParser
from app.services.ros2_bridge import get_ros2_bridge
from app.services.sam_clip_perceptor import SamClipPerceptor
from app.services.state_store import StateStore, get_state_store
from app.services.vision_service import VisionService
from app.services.yaml_registry import YAMLRegistry


@lru_cache
def get_registry() -> YAMLRegistry:
    settings = get_settings()
    return YAMLRegistry(settings.actions_yaml_path)


@lru_cache
def get_intent_parser() -> IntentParser:
    return IntentParser()


@lru_cache
def get_action_mapper() -> ActionMapper:
    return ActionMapper(get_registry())


@lru_cache
def get_perceptor() -> SamClipPerceptor:
    return SamClipPerceptor(get_registry())


@lru_cache
def get_vision_service() -> VisionService:
    return VisionService(get_perceptor())


def get_ros_bridge_dep():
    return get_ros2_bridge()


def get_state_store_dep() -> StateStore:
    return get_state_store()