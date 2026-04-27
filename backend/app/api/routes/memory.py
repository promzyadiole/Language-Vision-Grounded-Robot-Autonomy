from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_state_store_dep
from app.services.state_store import StateStore

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.get("/summary")
def get_memory_summary(store: StateStore = Depends(get_state_store_dep)):
    return store.get_summary()


@router.get("/current-pose")
def get_current_pose(store: StateStore = Depends(get_state_store_dep)):
    return {"current_pose": store.get_current_pose()}


@router.get("/previous-pose")
def get_previous_pose(store: StateStore = Depends(get_state_store_dep)):
    return {"previous_pose": store.get_previous_pose()}


@router.get("/last-command")
def get_last_command(store: StateStore = Depends(get_state_store_dep)):
    return {"last_command": store.get_last_command()}


@router.get("/last-result")
def get_last_result(store: StateStore = Depends(get_state_store_dep)):
    return {"last_result": store.get_last_result()}


@router.get("/pose-history")
def get_pose_history(
    limit: int = Query(default=10, ge=1, le=100),
    store: StateStore = Depends(get_state_store_dep),
):
    return {"items": store.get_pose_history(limit=limit)}


@router.get("/event-history")
def get_event_history(
    limit: int = Query(default=10, ge=1, le=100),
    store: StateStore = Depends(get_state_store_dep),
):
    return {"items": store.get_event_history(limit=limit)}