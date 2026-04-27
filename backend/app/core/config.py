from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Robot Command Center"
    debug: bool = True
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    actions_yaml_path: str = "app/data/robot_actions.yaml"
    vision_labels_yaml_path: str = "app/data/vision_labels.yaml"
    ros_use_sim_time: bool = True

    vision_device: str = Field(default="cpu", alias="VISION_DEVICE")
    sam_model_type: str = Field(default="vit_b", alias="SAM_MODEL_TYPE")
    sam_checkpoint_path: str = Field(default="", alias="SAM_CHECKPOINT_PATH")
    clip_model_name: str = Field(default="ViT-B-32", alias="CLIP_MODEL_NAME")
    clip_pretrained: str = Field(default="laion2b_s34b_b79k", alias="CLIP_PRETRAINED")
    vision_confidence_threshold: float = Field(default=0.24, alias="VISION_CONFIDENCE_THRESHOLD")
    vision_max_masks: int = Field(default=12, alias="VISION_MAX_MASKS")
    vision_min_mask_area: int = Field(default=1200, alias="VISION_MIN_MASK_AREA")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


def get_settings() -> Settings:
    return Settings()