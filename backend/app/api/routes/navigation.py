from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_registry, get_ros_bridge_dep, get_state_store_dep
from app.models.schemas import BasicActionResponse, FollowRouteRequest, GoToPlaceRequest
from app.services.ros2_bridge import ROS2Bridge
from app.services.state_store import StateStore
from app.services.yaml_registry import YAMLRegistry

router = APIRouter(prefix="/api/navigation", tags=["navigation"])


@router.post("/go-to", response_model=BasicActionResponse)
def go_to_place(
    payload: GoToPlaceRequest,
    registry: YAMLRegistry = Depends(get_registry),
    bridge: ROS2Bridge = Depends(get_ros_bridge_dep),
    store: StateStore = Depends(get_state_store_dep),
):
    place = registry.resolve_place(payload.place)
    if not place:
        raise HTTPException(status_code=404, detail=f"Unknown place: {payload.place}")

    pose = place["pose"]

    # Capture pose before navigation
    pose_before_raw = bridge.get_current_pose()
    pose_before = None
    if pose_before_raw:
        store.update_pose(
            x=pose_before_raw["x"],
            y=pose_before_raw["y"],
            yaw=pose_before_raw["yaw"],
            frame_id=pose_before_raw.get("frame_id", "map"),
        )
        pose_before = store.get_current_pose()

    store.set_last_command(payload.place, "navigation")

    result = bridge.navigate_to_pose(pose["x"], pose["y"], pose["yaw"])

    # Capture pose after navigation request
    pose_after_raw = bridge.get_current_pose()
    if pose_after_raw:
        store.update_pose(
            x=pose_after_raw["x"],
            y=pose_after_raw["y"],
            yaw=pose_after_raw["yaw"],
            frame_id=pose_after_raw.get("frame_id", "map"),
        )

    pose_after = store.get_current_pose()

    store.set_last_result(result)
    store.add_event(
        command=payload.place,
        command_type="navigation",
        status="success" if result.get("success", True) else "failed",
        pose_before=None,
        pose_after=None,
        result=result,
        metadata={
            "target_pose": pose,
            "place_key": place.get("key"),
            "pose_before_snapshot": pose_before,
            "pose_after_snapshot": pose_after,
        },
    )

    return BasicActionResponse(**result)


@router.post("/follow-route", response_model=BasicActionResponse)
def follow_route(
    payload: FollowRouteRequest,
    registry: YAMLRegistry = Depends(get_registry),
    bridge: ROS2Bridge = Depends(get_ros_bridge_dep),
    store: StateStore = Depends(get_state_store_dep),
):
    route = registry.resolve_route(payload.route_name)
    if not route:
        raise HTTPException(status_code=404, detail=f"Unknown route: {payload.route_name}")

    pose_before_raw = bridge.get_current_pose()
    pose_before = None
    if pose_before_raw:
        store.update_pose(
            x=pose_before_raw["x"],
            y=pose_before_raw["y"],
            yaw=pose_before_raw["yaw"],
            frame_id=pose_before_raw.get("frame_id", "map"),
        )
        pose_before = store.get_current_pose()

    store.set_last_command(payload.route_name, "waypoint_route")

    result = bridge.follow_waypoints(route["points"])

    pose_after_raw = bridge.get_current_pose()
    if pose_after_raw:
        store.update_pose(
            x=pose_after_raw["x"],
            y=pose_after_raw["y"],
            yaw=pose_after_raw["yaw"],
            frame_id=pose_after_raw.get("frame_id", "map"),
        )

    pose_after = store.get_current_pose()

    store.set_last_result(result)
    store.add_event(
        command=payload.route_name,
        command_type="waypoint_route",
        status="success" if result.get("success", True) else "failed",
        pose_before=None,
        pose_after=None,
        result=result,
        metadata={
            "num_points": len(route["points"]),
            "pose_before_snapshot": pose_before,
            "pose_after_snapshot": pose_after,
        },
    )

    return BasicActionResponse(**result)