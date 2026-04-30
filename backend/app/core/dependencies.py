# from functools import lru_cache

# from app.core.config import get_settings
# from app.services.action_mapper import ActionMapper
# from app.services.intent_parser import IntentParser
# from app.services.ros2_bridge import get_ros2_bridge
# from app.services.sam_clip_perceptor import SamClipPerceptor
# from app.services.state_store import StateStore, get_state_store
# from app.services.vision_service import VisionService
# from app.services.yaml_registry import YAMLRegistry


# @lru_cache
# def get_registry() -> YAMLRegistry:
#     settings = get_settings()
#     return YAMLRegistry(settings.actions_yaml_path)


# @lru_cache
# def get_intent_parser() -> IntentParser:
#     return IntentParser()


# @lru_cache
# def get_action_mapper() -> ActionMapper:
#     return ActionMapper(get_registry())


# @lru_cache
# def get_perceptor() -> SamClipPerceptor:
#     return SamClipPerceptor(get_registry())


# @lru_cache
# def get_vision_service() -> VisionService:
#     return VisionService(get_perceptor())


# def get_ros_bridge_dep():
#     return get_ros2_bridge()


# def get_state_store_dep() -> StateStore:
#     return get_state_store()


from __future__ import annotations

from app.services.action_mapper import ActionMapper, get_action_mapper
from app.services.environment_service import EnvironmentService, get_environment_service
from app.services.intent_parser import IntentParser, get_intent_parser
from app.services.ros2_bridge import ROS2Bridge, get_ros2_bridge
from app.services.state_store import StateStore, get_state_store
from app.services.vision_service import VisionService, get_vision_service


def get_ros_bridge_dep() -> ROS2Bridge:
    return get_ros2_bridge()


def get_state_store_dep() -> StateStore:
    return get_state_store()


def get_intent_parser_dep() -> IntentParser:
    return get_intent_parser()


def get_action_mapper_dep() -> ActionMapper:
    return get_action_mapper()


def get_vision_service_dep() -> VisionService:
    return get_vision_service()


def get_environment_service_dep() -> EnvironmentService:
    return get_environment_service()