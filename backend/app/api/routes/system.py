# # from fastapi import APIRouter

# # from app.services.state_store import state_store

# # router = APIRouter(prefix="/api/system", tags=["system"])


# # @router.get("/health")
# # def health():
# #     snapshot = state_store.snapshot()
# #     return {
# #         "status": "ok",
# #         "nav2_ready": snapshot.get("nav2_ready", False),
# #         "camera_available": snapshot.get("latest_image_meta") is not None,
# #     }


# from __future__ import annotations

# from fastapi import APIRouter, Depends

# from app.models.schemas import BasicActionResponse
# from app.services.environment_service import EnvironmentService, get_environment_service

# router = APIRouter(prefix="/api/system", tags=["system"])


# @router.get("/environment", response_model=BasicActionResponse)
# def get_environment(
#     env_service: EnvironmentService = Depends(get_environment_service),
# ) -> BasicActionResponse:
#     return BasicActionResponse(
#         success=True,
#         message="Environment loaded successfully.",
#         data=env_service.environment,
#     )


from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import get_environment_service_dep
from app.models.schemas import BasicActionResponse
from app.services.environment_service import EnvironmentService

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/environment", response_model=BasicActionResponse)
def get_environment(
    env_service: EnvironmentService = Depends(get_environment_service_dep),
) -> BasicActionResponse:
    return BasicActionResponse(
        success=True,
        message="Environment loaded successfully.",
        data=env_service.environment,
    )