from __future__ import annotations

import os
import threading
from typing import Any, Dict, List

import cv2
import numpy as np
import open_clip
import torch
from PIL import Image
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

from app.core.config import get_settings
from app.services.yaml_registry import YAMLRegistry


class SamClipPerceptor:
    def __init__(self, registry: YAMLRegistry) -> None:
        self.settings = get_settings()
        self.registry = registry

        self.device = self._resolve_device(self.settings.vision_device)
        self.labels = self._load_labels()
        self.text_prompts = [self._to_clip_prompt(label) for label in self.labels]

        self._predict_lock = threading.Lock()

        self._load_models()

    def _resolve_device(self, configured: str) -> str:
        if configured == "cuda" and torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def _load_labels(self) -> List[str]:
        vision_yaml_path = self.settings.vision_labels_yaml_path
        registry = YAMLRegistry(vision_yaml_path)
        raw = registry.data.get("vision_labels", [])
        labels = []
        for item in raw:
            if isinstance(item, str):
                labels.append(item)
            elif isinstance(item, dict) and "name" in item:
                labels.append(item["name"])
        return labels

    def _to_clip_prompt(self, label: str) -> str:
        return f"a photo of a {label}"

    def _load_models(self) -> None:
        if not self.settings.sam_checkpoint_path or not os.path.exists(self.settings.sam_checkpoint_path):
            raise FileNotFoundError(
                f"SAM checkpoint not found: {self.settings.sam_checkpoint_path}"
            )

        checkpoint_name = os.path.basename(self.settings.sam_checkpoint_path).lower()
        model_type = self.settings.sam_model_type.lower()

        if "vit_b" in checkpoint_name and model_type != "vit_b":
            raise ValueError(
                f"SAM model mismatch: checkpoint '{checkpoint_name}' requires SAM_MODEL_TYPE=vit_b, "
                f"but got '{self.settings.sam_model_type}'."
            )
        if "vit_l" in checkpoint_name and model_type != "vit_l":
            raise ValueError(
                f"SAM model mismatch: checkpoint '{checkpoint_name}' requires SAM_MODEL_TYPE=vit_l, "
                f"but got '{self.settings.sam_model_type}'."
            )
        if "vit_h" in checkpoint_name and model_type != "vit_h":
            raise ValueError(
                f"SAM model mismatch: checkpoint '{checkpoint_name}' requires SAM_MODEL_TYPE=vit_h, "
                f"but got '{self.settings.sam_model_type}'."
            )

        sam = sam_model_registry[self.settings.sam_model_type](
            checkpoint=self.settings.sam_checkpoint_path
        )
        sam.to(device=self.device)

        self.mask_generator = SamAutomaticMaskGenerator(
            model=sam,
            pred_iou_thresh=0.84,
            stability_score_thresh=0.90,
            min_mask_region_area=self.settings.vision_min_mask_area,
        )

        cache_dir = os.path.join(
            os.path.dirname(self.settings.sam_checkpoint_path),
            "hf_cache",
        )
        os.makedirs(cache_dir, exist_ok=True)

        self.clip_model, _, self.clip_preprocess = open_clip.create_model_and_transforms(
            self.settings.clip_model_name,
            pretrained=self.settings.clip_pretrained,
            device=self.device,
            cache_dir=cache_dir,
        )
        self.clip_tokenizer = open_clip.get_tokenizer(self.settings.clip_model_name)

        with torch.no_grad():
            text_tokens = self.clip_tokenizer(self.text_prompts).to(self.device)
            text_features = self.clip_model.encode_text(text_tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        self.text_features = text_features

    def predict_fast(self, rgb_image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Faster mode:
        - downscale image
        - use a small fixed grid of candidate regions
        - classify those regions directly with CLIP
        - no SAM automatic mask generation
        """
        if rgb_image is None:
            return []

        with self._predict_lock:
            original_h, original_w = rgb_image.shape[:2]

            target_w = 320
            scale = target_w / float(original_w)
            target_h = int(original_h * scale)

            small_image = cv2.resize(rgb_image, (target_w, target_h), interpolation=cv2.INTER_AREA)

            candidate_boxes = self._grid_candidate_boxes(target_w, target_h)
            detections: List[Dict[str, Any]] = []

            for idx, bbox in enumerate(candidate_boxes):
                det = self._classify_box(small_image, bbox, idx)
                if det is None:
                    continue
                if not self._passes_geometry_filters(det["bbox"], target_w, target_h):
                    continue

                x1, y1, x2, y2 = det["bbox"]
                det["bbox"] = [
                    int(x1 / scale),
                    int(y1 / scale),
                    int(x2 / scale),
                    int(y2 / scale),
                ]
                cx, cy = det["center_px"]
                det["center_px"] = [int(cx / scale), int(cy / scale)]

                detections.append(det)

            detections = self._deduplicate(detections)
            detections = self._limit_per_label(detections, max_per_label=2)
            detections = self._attach_direction(detections, original_w)

            return sorted(detections, key=lambda d: d["confidence"], reverse=True)

    def predict_full(self, rgb_image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Slower, fuller mode:
        - SAM automatic masks
        - CLIP classification on masked crops
        """
        if rgb_image is None:
            return []

        with self._predict_lock:
            original_h, original_w = rgb_image.shape[:2]

            target_w = 320
            scale = target_w / float(original_w)
            target_h = int(original_h * scale)

            small_image = cv2.resize(rgb_image, (target_w, target_h), interpolation=cv2.INTER_AREA)

            masks = self.mask_generator.generate(small_image)
            masks = self._sort_and_limit_masks(masks, self.settings.vision_max_masks)

            detections: List[Dict[str, Any]] = []

            for idx, mask_data in enumerate(masks):
                det = self._classify_mask(small_image, mask_data, idx)
                if det is None:
                    continue
                if not self._passes_geometry_filters(det["bbox"], target_w, target_h):
                    continue

                x1, y1, x2, y2 = det["bbox"]
                det["bbox"] = [
                    int(x1 / scale),
                    int(y1 / scale),
                    int(x2 / scale),
                    int(y2 / scale),
                ]
                cx, cy = det["center_px"]
                det["center_px"] = [int(cx / scale), int(cy / scale)]

                detections.append(det)

            detections = self._deduplicate(detections)
            detections = self._limit_per_label(detections, max_per_label=3)
            detections = self._attach_direction(detections, original_w)

            return sorted(detections, key=lambda d: d["confidence"], reverse=True)

    def _grid_candidate_boxes(self, image_w: int, image_h: int) -> List[List[int]]:
        boxes: List[List[int]] = []

        thirds_x = [0, image_w // 3, 2 * image_w // 3, image_w]
        thirds_y = [0, image_h // 3, 2 * image_h // 3, image_h]

        for row in range(3):
            for col in range(3):
                x1 = thirds_x[col]
                y1 = thirds_y[row]
                x2 = thirds_x[col + 1]
                y2 = thirds_y[row + 1]
                boxes.append([x1, y1, x2, y2])

        boxes.append([image_w // 4, image_h // 4, 3 * image_w // 4, 3 * image_h // 4])
        boxes.append([0, image_h // 2, image_w, image_h])
        boxes.append([0, 0, image_w, image_h // 2])

        return boxes

    def _classify_box(
        self,
        rgb_image: np.ndarray,
        bbox: List[int],
        box_id: int,
    ) -> Dict[str, Any] | None:
        x1, y1, x2, y2 = bbox
        crop = rgb_image[y1:y2, x1:x2].copy()

        if crop.size == 0:
            return None

        pil_image = Image.fromarray(crop)
        image_tensor = self.clip_preprocess(pil_image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            image_features = self.clip_model.encode_image(image_tensor)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            logits = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)[0]
            best_idx = int(torch.argmax(logits).item())
            confidence = float(logits[best_idx].item())

        if confidence < self.settings.vision_confidence_threshold:
            return None

        label = self.labels[best_idx]
        center_px = [int((x1 + x2) / 2), int((y1 + y2) / 2)]

        return {
            "label": label,
            "confidence": round(confidence, 4),
            "bbox": [x1, y1, x2, y2],
            "center_px": center_px,
            "mask_id": box_id,
        }

    def _sort_and_limit_masks(self, masks: List[Dict[str, Any]], max_masks: int) -> List[Dict[str, Any]]:
        filtered = [
            m for m in masks
            if int(m.get("area", 0)) >= self.settings.vision_min_mask_area
        ]
        filtered.sort(
            key=lambda x: (
                float(x.get("predicted_iou", 0.0)),
                float(x.get("stability_score", 0.0)),
                float(x.get("area", 0.0)),
            ),
            reverse=True,
        )
        return filtered[:max_masks]

    def _classify_mask(
        self,
        rgb_image: np.ndarray,
        mask_data: Dict[str, Any],
        mask_id: int,
    ) -> Dict[str, Any] | None:
        seg = mask_data["segmentation"].astype(bool)
        x, y, w, h = mask_data["bbox"]
        x1, y1 = int(x), int(y)
        x2, y2 = int(x + w), int(y + h)

        if x2 <= x1 or y2 <= y1:
            return None

        crop = rgb_image[y1:y2, x1:x2].copy()
        crop_mask = seg[y1:y2, x1:x2]

        if crop.size == 0 or crop_mask.size == 0:
            return None

        visible_ratio = float(crop_mask.mean())
        if visible_ratio < 0.08:
            return None

        masked_crop = crop.copy()
        masked_crop[~crop_mask] = 0

        pil_image = Image.fromarray(masked_crop)
        image_tensor = self.clip_preprocess(pil_image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            image_features = self.clip_model.encode_image(image_tensor)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            logits = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)[0]
            best_idx = int(torch.argmax(logits).item())
            confidence = float(logits[best_idx].item())

        if confidence < self.settings.vision_confidence_threshold:
            return None

        label = self.labels[best_idx]
        center_px = [int((x1 + x2) / 2), int((y1 + y2) / 2)]

        return {
            "label": label,
            "confidence": round(confidence, 4),
            "bbox": [x1, y1, x2, y2],
            "center_px": center_px,
            "mask_id": mask_id,
        }

    def _passes_geometry_filters(self, bbox: List[int], image_w: int, image_h: int) -> bool:
        x1, y1, x2, y2 = bbox
        bw = max(1, x2 - x1)
        bh = max(1, y2 - y1)
        area = bw * bh
        image_area = image_w * image_h
        aspect = bw / bh

        if area < self.settings.vision_min_mask_area:
            return False

        if area > image_area * 0.72:
            return False

        if bw > image_w * 0.995 or bh > image_h * 0.995:
            return False

        if aspect > 14.0 or aspect < 0.08:
            return False

        edge_touch_count = 0
        margin_x = int(image_w * 0.01)
        margin_y = int(image_h * 0.01)

        if x1 <= margin_x:
            edge_touch_count += 1
        if y1 <= margin_y:
            edge_touch_count += 1
        if x2 >= image_w - margin_x:
            edge_touch_count += 1
        if y2 >= image_h - margin_y:
            edge_touch_count += 1

        if edge_touch_count >= 3 and area > image_area * 0.25:
            return False

        return True

    def _deduplicate(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        kept: List[Dict[str, Any]] = []

        for det in sorted(detections, key=lambda d: d["confidence"], reverse=True):
            should_keep = True
            for existing in kept:
                if det["label"] != existing["label"]:
                    continue
                if self._iou(det["bbox"], existing["bbox"]) > 0.55:
                    should_keep = False
                    break
            if should_keep:
                kept.append(det)

        return kept

    def _limit_per_label(self, detections: List[Dict[str, Any]], max_per_label: int = 3) -> List[Dict[str, Any]]:
        counts: Dict[str, int] = {}
        result: List[Dict[str, Any]] = []

        for det in sorted(detections, key=lambda d: d["confidence"], reverse=True):
            label = det["label"]
            counts[label] = counts.get(label, 0)
            if counts[label] >= max_per_label:
                continue
            result.append(det)
            counts[label] += 1

        return result

    def _attach_direction(self, detections: List[Dict[str, Any]], image_w: int) -> List[Dict[str, Any]]:
        for det in detections:
            cx = det["center_px"][0]
            ratio = cx / max(1, image_w)

            if ratio < 0.33:
                direction = "left"
            elif ratio < 0.67:
                direction = "center"
            else:
                direction = "right"

            det["direction"] = direction

        return detections

    def _iou(self, a: List[int], b: List[int]) -> float:
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b

        inter_x1 = max(ax1, bx1)
        inter_y1 = max(ay1, by1)
        inter_x2 = min(ax2, bx2)
        inter_y2 = min(ay2, by2)

        inter_w = max(0, inter_x2 - inter_x1)
        inter_h = max(0, inter_y2 - inter_y1)
        inter_area = inter_w * inter_h

        area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
        area_b = max(0, bx2 - bx1) * max(0, by2 - by1)

        union = area_a + area_b - inter_area
        if union <= 0:
            return 0.0
        return inter_area / union