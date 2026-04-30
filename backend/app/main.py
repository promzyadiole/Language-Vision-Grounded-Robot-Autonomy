# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.api.routes import chat, memory, navigation, robot, system, vision
# from app.core.config import get_settings
# from app.services.ros2_bridge import get_ros2_bridge




# settings = get_settings()

# app = FastAPI(title=settings.app_name)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(system.router)
# app.include_router(robot.router)
# app.include_router(navigation.router)
# app.include_router(vision.router)
# app.include_router(chat.router)
# app.include_router(memory.router)


# @app.on_event("startup")
# def startup_event():
#     get_ros2_bridge()


# @app.get("/")
# def root():
#     return {"message": f"{settings.app_name} is running."}


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, localization, navigation, robot, system, vision

app = FastAPI(title="Robot Command Center API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(robot.router)
app.include_router(navigation.router)
app.include_router(localization.router)
app.include_router(chat.router)
app.include_router(vision.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}