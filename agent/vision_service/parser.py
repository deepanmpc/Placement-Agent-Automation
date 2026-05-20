import uuid
from datetime import datetime
from typing import Dict, Any, List
from PIL import Image

from vision_service.utils.logger import logger
from vision_service.utils.timings import global_metrics
from vision_service.schemas import UIElement, ScreenState, Relationship
from vision_service.config import Config

_nvidia_vision_service = None


def _get_nvidia_vision_service():
    global _nvidia_vision_service
    if _nvidia_vision_service is None:
        from vision_service.nvidia_vision import NvidiaVisionService

        _nvidia_vision_service = NvidiaVisionService()
    return _nvidia_vision_service

def parse_ui(
    img_pil: Image.Image,
    ocr_data: Dict[str, Any],
    capture_info: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Combines OCR output and image semantic detections into a unified UI schema.
    In the future, this is where OmniParser detection hooks in.
    """
    with global_metrics.measure("semantic_parsing"):
        width, height = img_pil.size
        timestamp = datetime.now().isoformat()
        
        capture_info = capture_info or {}
        origin_x = int(capture_info.get("origin_x", 0))
        origin_y = int(capture_info.get("origin_y", 0))

        screen_state = ScreenState(
            width=width,
            height=height,
            timestamp=timestamp,
            origin_x=origin_x,
            origin_y=origin_y,
            coordinate_system=capture_info.get("coordinate_system", "screen"),
            capture_scope=capture_info.get("capture_scope", "unknown"),
            app=capture_info.get("app"),
            title=capture_info.get("title"),
            screenshot_path=capture_info.get("screenshot_path"),
        )
        
        # For Phase 1 without OmniParser running inline, we treat OCR texts as basic UI elements
        raw_elements = []
        for text_item in ocr_data.get("texts", []):
            bbox = text_item.get("bbox")
            center = text_item.get("center")
            if not bbox or not center:
                continue

            absolute_bbox = (
                int(bbox[0]) + origin_x,
                int(bbox[1]) + origin_y,
                int(bbox[2]) + origin_x,
                int(bbox[3]) + origin_y,
            )
            absolute_center = (
                int(center[0]) + origin_x,
                int(center[1]) + origin_y,
            )
            elem = UIElement(
                id=f"elem_{uuid.uuid4().hex[:8]}",
                type="text",
                text=text_item.get("text"),
                bbox=absolute_bbox,
                center=absolute_center,
                clickable=False, # We don't know without OmniParser
                confidence=text_item.get("confidence", 0.0),
                source="ocr"
            )
            raw_elements.append(elem)

        enrichment_metadata: Dict[str, Any] = {}
        if Config.ENABLE_NEMOTRON_PARSER:
            try:
                parser_payload = _get_nvidia_vision_service().parse_ui(img_pil)
                enrichment_metadata["nemotron_parse_summary"] = parser_payload.get("summary", "")
                raw_elements.extend(
                    _model_elements_to_ui_elements(
                        parser_payload.get("elements", []),
                        origin_x=origin_x,
                        origin_y=origin_y,
                        source="nemotron-parse",
                    )
                )
            except Exception as e:
                logger.warning(f"Nemotron parser enrichment failed: {e}")

        if Config.ENABLE_VISION_VLM:
            try:
                vision_payload = _get_nvidia_vision_service().describe_screen(img_pil)
                enrichment_metadata["vision_summary"] = vision_payload.get("summary", "")
                enrichment_metadata["vision_task_state"] = vision_payload.get("likely_task_state", "")
                enrichment_metadata["vision_targets"] = vision_payload.get("important_targets", [])
            except Exception as e:
                logger.warning(f"Vision VLM enrichment failed: {e}")

        # TODO: Call OmniParser locally to detect buttons, inputs, etc.
        # omni_detections = call_omniparser(img_pil)
        # raw_elements.extend(omni_detections)
        
        # Normalize and deduplicate
        elements = normalize_elements(raw_elements)
        relationships = build_ui_graph(elements)
        
        parsed_state = {
            "screen": screen_state.model_dump(),
            "elements": [e.model_dump() for e in elements],
            "relationships": [r.model_dump() for r in relationships],
            "metadata": {
                **ocr_data.get("metadata", {}),
                **capture_info,
                **enrichment_metadata,
                "coordinate_system": screen_state.coordinate_system,
            },
        }
        
        logger.info(f"Parsed UI: {len(elements)} elements detected.")
        return parsed_state


def _model_elements_to_ui_elements(
    elements: List[Dict[str, Any]],
    *,
    origin_x: int,
    origin_y: int,
    source: str,
) -> List[UIElement]:
    normalized = []
    for item in elements:
        if not isinstance(item, dict):
            continue

        text = str(item.get("text") or item.get("label") or "").strip()
        bbox = item.get("bbox") or item.get("box")
        if not text or not bbox or len(bbox) != 4:
            continue

        try:
            x1, y1, x2, y2 = [int(float(v)) for v in bbox]
        except (TypeError, ValueError):
            continue

        # Defensive normalization for [x, y, width, height] style outputs.
        if x2 <= x1 or y2 <= y1:
            x2 = x1 + max(1, x2)
            y2 = y1 + max(1, y2)

        absolute_bbox = (x1 + origin_x, y1 + origin_y, x2 + origin_x, y2 + origin_y)
        absolute_center = (
            int((absolute_bbox[0] + absolute_bbox[2]) / 2),
            int((absolute_bbox[1] + absolute_bbox[3]) / 2),
        )

        normalized.append(
            UIElement(
                id=f"elem_{uuid.uuid4().hex[:8]}",
                type=str(item.get("type") or "element"),
                text=text,
                bbox=absolute_bbox,
                center=absolute_center,
                clickable=bool(item.get("clickable", True)),
                confidence=float(item.get("confidence", 0.7) or 0.7),
                source=source,
            )
        )
    return normalized

def normalize_elements(elements: List[UIElement]) -> List[UIElement]:
    """
    Deduplicate overlapping OCR/UI detections and merge tags.
    Priority:
    1. Prefer 'nemotron-parse' or 'omni-parser' for 'type' and 'clickable'.
    2. Prefer 'ocr' for precise 'text' if they overlap significantly.
    """
    if not elements:
        return []

    # Sort so that enriched models are processed first
    priority = {"nemotron-parse": 0, "omni-parser": 1, "ocr": 2}
    sorted_elements = sorted(elements, key=lambda x: priority.get(x.source, 99))

    final_elements: List[UIElement] = []

    for new_el in sorted_elements:
        is_duplicate = False
        for existing_el in final_elements:
            # Calculate Intersection over Union (IoU) or simply Intersection over Self
            iou = _calculate_iou(new_el.bbox, existing_el.bbox)
            
            # If they overlap significantly (>70%)
            if iou > 0.7:
                is_duplicate = True
                # Merge: If existing is VLM and new is OCR, keep VLM type but update text if OCR is better
                if existing_el.source != "ocr" and new_el.source == "ocr":
                    if not existing_el.text or len(new_el.text) > len(existing_el.text):
                        existing_el.text = new_el.text
                    existing_el.confidence = max(existing_el.confidence, new_el.confidence)
                break
        
        if not is_duplicate:
            final_elements.append(new_el)

    return final_elements

def _calculate_iou(boxA, boxB):
    # box = (x1, y1, x2, y2)
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def build_ui_graph(elements: List[UIElement]) -> List[Relationship]:
    """
    Build hierarchical relationships (e.g. dialog -> button) based on geometry.
    """
    relationships = []
    # Placeholder: if an element is completely enclosed in another, it is a child.
    return relationships
