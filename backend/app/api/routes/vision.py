from fastapi import APIRouter, Depends

from app.core.dependencies import get_vision_service
from app.services.vision_service import VisionService

router = APIRouter(prefix="/api/vision", tags=["vision"])


@router.get("/objects")
def get_visible_objects_fast(vision: VisionService = Depends(get_vision_service)):
    return vision.detect_objects_fast()


@router.get("/objects-fast")
def get_visible_objects_fast_explicit(vision: VisionService = Depends(get_vision_service)):
    return vision.detect_objects_fast()


@router.get("/objects-fast-annotated")
def get_visible_objects_fast_annotated(vision: VisionService = Depends(get_vision_service)):
    return vision.detect_objects_fast_annotated()


@router.get("/objects-full")
def get_visible_objects_full(vision: VisionService = Depends(get_vision_service)):
    return vision.detect_objects_full()


@router.get("/scene-summary")
def get_scene_summary_fast(vision: VisionService = Depends(get_vision_service)):
    return vision.scene_summary_fast()


@router.get("/scene-summary-fast")
def get_scene_summary_fast_explicit(vision: VisionService = Depends(get_vision_service)):
    return vision.scene_summary_fast()


@router.get("/scene-summary-fast-annotated")
def get_scene_summary_fast_annotated(vision: VisionService = Depends(get_vision_service)):
    return vision.scene_summary_fast_annotated()


@router.get("/scene-summary-full")
def get_scene_summary_full(vision: VisionService = Depends(get_vision_service)):
    return vision.scene_summary_full()