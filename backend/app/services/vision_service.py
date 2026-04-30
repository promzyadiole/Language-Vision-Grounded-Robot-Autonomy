from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import cv2

from app.services.sam_clip_perceptor import SamClipPerceptor
from app.services.state_store import state_store
from app.services.yaml_registry import get_yaml_registry


class VisionService:
    def __init__(self, perceptor: SamClipPerceptor) -> None:
        self.perceptor = perceptor

    def get_latest_frame(self) -> Dict[str, Any]:
        image = state_store.get("latest_image")
        meta = state_store.get("latest_image_meta")
        return {"image": image, "meta": meta}

    def detect_objects_fast(self) -> Dict[str, Any]:
        frame_data = self.get_latest_frame()
        image = frame_data["image"]
        meta = frame_data["meta"]

        if image is None or meta is None:
            return {
                "mode": "fast",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "frame_id": None,
                "width": None,
                "height": None,
                "objects": [],
            }

        objects = self.perceptor.predict_fast(image)
        objects = sorted(objects, key=lambda d: d["confidence"], reverse=True)
        top_objects = objects[:5]

        state_store.set("vision_objects", top_objects)

        return {
            "mode": "fast",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "frame_id": meta.get("frame_id"),
            "width": meta.get("width"),
            "height": meta.get("height"),
            "objects": top_objects,
        }

    def detect_objects_fast_annotated(self) -> Dict[str, Any]:
        frame_data = self.get_latest_frame()
        image = frame_data["image"]
        meta = frame_data["meta"]

        if image is None or meta is None:
            return {
                "mode": "fast_annotated",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "frame_id": None,
                "width": None,
                "height": None,
                "objects": [],
                "annotated_image": None,
            }

        objects = self.perceptor.predict_fast(image)
        objects = sorted(objects, key=lambda d: d["confidence"], reverse=True)
        top_objects = objects[:5]

        annotated_image = self._build_annotated_image(image, top_objects)

        state_store.set("vision_objects", top_objects)

        return {
            "mode": "fast_annotated",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "frame_id": meta.get("frame_id"),
            "width": meta.get("width"),
            "height": meta.get("height"),
            "objects": top_objects,
            "annotated_image": annotated_image,
        }

    def detect_objects_full(self) -> Dict[str, Any]:
        frame_data = self.get_latest_frame()
        image = frame_data["image"]
        meta = frame_data["meta"]

        if image is None or meta is None:
            return {
                "mode": "full",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "frame_id": None,
                "width": None,
                "height": None,
                "objects": [],
            }

        objects = self.perceptor.predict_full(image)
        objects = sorted(objects, key=lambda d: d["confidence"], reverse=True)
        top_objects = objects[:5]

        state_store.set("vision_objects", top_objects)

        return {
            "mode": "full",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "frame_id": meta.get("frame_id"),
            "width": meta.get("width"),
            "height": meta.get("height"),
            "objects": top_objects,
        }

    def scene_summary_fast(self) -> Dict[str, Any]:
        detection_result = self.detect_objects_fast()
        return self._build_summary(detection_result)

    def scene_summary_fast_annotated(self) -> Dict[str, Any]:
        detection_result = self.detect_objects_fast_annotated()
        return self._build_summary(detection_result)

    def scene_summary_full(self) -> Dict[str, Any]:
        detection_result = self.detect_objects_full()
        return self._build_summary(detection_result)

    def _build_summary(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        objects = detection_result["objects"]

        if not objects:
            return {
                "mode": detection_result.get("mode"),
                "summary": "I do not currently detect any known objects in view.",
                "objects": [],
                "annotated_image": detection_result.get("annotated_image"),
            }

        phrases = []
        for obj in objects[:5]:
            label = obj["label"]
            direction = obj.get("direction")
            confidence = obj["confidence"]

            if direction:
                phrases.append(f"{label} on the {direction} ({confidence:.2f})")
            else:
                phrases.append(f"{label} ({confidence:.2f})")

        return {
            "mode": detection_result.get("mode"),
            "summary": "I can currently see: " + ", ".join(phrases) + ".",
            "objects": objects,
            "annotated_image": detection_result.get("annotated_image"),
        }

    def _build_annotated_image(self, image, objects: List[Dict[str, Any]]) -> str | None:
        if image is None:
            return None

        annotated = image.copy()

        for obj in objects:
            x1, y1, x2, y2 = obj["bbox"]
            label = obj["label"]
            conf = obj["confidence"]
            direction = obj.get("direction", "")

            text = f"{label} {conf:.2f}"
            if direction:
                text += f" [{direction}]"

            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated,
                text,
                (x1, max(y1 - 8, 14)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

        bgr = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
        ok, buffer = cv2.imencode(".jpg", bgr)
        if not ok:
            return None

        return base64.b64encode(buffer.tobytes()).decode("utf-8")


_vision_service: Optional[VisionService] = None


def get_vision_service() -> VisionService:
    global _vision_service
    if _vision_service is None:
        registry = get_yaml_registry()
        perceptor = SamClipPerceptor(registry)
        _vision_service = VisionService(perceptor)
    return _vision_service