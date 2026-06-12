import os
from typing import Dict, Any

import numpy as np
from PIL import Image

# Initialize paddleocr early to save load time in loops
# Note: we use use_angle_cls=False for speed if orientation is fixed
try:
    from paddleocr import PaddleOCR
    _ocr_engine = PaddleOCR(lang='en', ocr_version='PP-OCRv3', use_angle_cls=False)
except Exception as e:
    import logging
    logging.getLogger("vision_service").warning(f"PaddleOCR failed to initialize: {e}")
    _ocr_engine = None

from vision_service.utils.logger import logger
from vision_service.utils.timings import global_metrics
from vision_service.schemas import OCRText

def extract_text(img_np: np.ndarray) -> Dict[str, Any]:
    """
    Extracts text from a numpy array image using PaddleOCR.
    """
    if _ocr_engine is None:
        logger.warning("PaddleOCR is not installed or failed to load.")
        return {"texts": [], "metadata": {"total_texts": 0, "ocr_time_ms": 0}}

    with global_metrics.measure("ocr_extraction"):
        try:
            # paddleocr expects BGR numpy array. Strip Alpha channel if BGRA.
            if len(img_np.shape) == 3 and img_np.shape[2] == 4:
                import cv2
                img_np = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
                
            results = _ocr_engine.ocr(img_np)
            normalized_results = normalize_ocr_results(results)
            
            return {
                "texts": [t.model_dump() for t in normalized_results],
                "metadata": {
                    "total_texts": len(normalized_results),
                    "ocr_time_ms": global_metrics.get_metrics().get("ocr_extraction", 0)
                }
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"OCR Extraction failed: {e}")
            return {"texts": [], "metadata": {"total_texts": 0, "ocr_time_ms": 0, "error": str(e)}}

def normalize_ocr_results(paddle_results) -> list[OCRText]:
    """
    Normalizes PaddleOCR output into the standard OCRText schema.
    """
    normalized = []
    if not paddle_results or paddle_results == [None]:
        return normalized

    # Support dictionary structure returned by PaddleX pipeline
    if isinstance(paddle_results, list) and len(paddle_results) > 0 and isinstance(paddle_results[0], dict):
        item = paddle_results[0]
        rec_texts = item.get("rec_texts", [])
        rec_scores = item.get("rec_scores", [])
        rec_boxes = item.get("rec_boxes", []) # numpy array of [xmin, ymin, xmax, ymax]
        
        for i in range(len(rec_texts)):
            text = rec_texts[i]
            confidence = rec_scores[i]
            box = rec_boxes[i] # [xmin, ymin, xmax, ymax]
            
            x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            
            normalized.append(OCRText(
                text=str(text),
                confidence=float(confidence),
                bbox=(int(x1), int(y1), int(x2), int(y2)),
                center=(cx, cy)
            ))
        return normalized

    # Safely extract the first image's results (legacy list-of-lists format)
    lines = paddle_results[0]
    
    if not lines:
        return normalized

    # Check if lines is actually just a single bounding box detection (flat structure)
    if isinstance(lines, list) and len(lines) == 2 and isinstance(lines[1], tuple):
        lines = paddle_results

    for res in lines:
        if not res or len(res) != 2:
            continue
            
        box, (text, confidence) = res
        
        # box is 4 points. Extract bounding box.
        x_coords = [point[0] for point in box]
        y_coords = [point[1] for point in box]
        
        x1, x2 = min(x_coords), max(x_coords)
        y1, y2 = min(y_coords), max(y_coords)
        
        # Calculate center
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        
        normalized.append(OCRText(
            text=text,
            confidence=float(confidence),
            bbox=(int(x1), int(y1), int(x2), int(y2)),
            center=(cx, cy)
        ))
        
    return normalized
