from fastapi import APIRouter

from app.services.state_store import state_store

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health")
def health():
    snapshot = state_store.snapshot()
    return {
        "status": "ok",
        "nav2_ready": snapshot.get("nav2_ready", False),
        "camera_available": snapshot.get("latest_image_meta") is not None,
    }