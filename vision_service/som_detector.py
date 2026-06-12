import os
import base64
import io
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw
import numpy as np

from vision_service.utils.logger import logger


class SoMDetector:
    """Set-of-Mark (SoM) button detection using YOLOv8."""
    
    def __init__(self, model_path: str = None):
        self.model = None
        # Use SOC's best.pt model from their repo
        self.model_path = model_path or "/Users/deepandee/Desktop/self-operating-computer/operate/models/weights/best.pt"
        self._load_model()
    
    def _load_model(self):
        """Load YOLOv8 model for button detection."""
        try:
            # Import ultralytics lazily to avoid conflicts with Paddle
            import sys
            # Check if we can load without Paddle interference
            if os.path.exists(self.model_path):
                # Try importing in a clean way
                import ultralytics
                self.model = ultralytics.YOLO(self.model_path)
                logger.info(f"SoM detector loaded: {self.model_path}")
            else:
                logger.warning(f"SoM model not found at {self.model_path}")
        except Exception as e:
            logger.warning(f"Failed to load SoM model: {e}")
    
    def detect_buttons(self, img_pil: Image.Image) -> List[Dict[str, Any]]:
        """Detect clickable buttons/elements in the screenshot."""
        if self.model is None:
            return []
        
        try:
            # Convert PIL to numpy
            if isinstance(img_pil, Image.Image):
                img_np = np.array(img_pil)
            else:
                img_np = img_pil
            
            # Run with lower confidence for more detections
            results = self.model(img_np, conf=0.2, verbose=False)
            buttons = []
            
            for r in results:
                boxes = r.boxes
                if boxes is None:
                    continue
                boxes_list = boxes.xyxy
                if boxes_list is None or len(boxes_list) == 0:
                    continue
                    
                for i in range(len(boxes_list)):
                    box = boxes_list[i]
                    conf = float(boxes.conf[i]) if hasattr(boxes, 'conf') else 0.5
                    
                    x1, y1, x2, y2 = box[0].item(), box[1].item(), box[2].item(), box[3].item()
                    
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)
                    
                    buttons.append({
                        "id": f"btn_{i}",
                        "label": f"button_{i+1}",
                        "bbox": [int(x1), int(y1), int(x2), int(y2)],
                        "center": [center_x, center_y],
                        "confidence": conf,
                        "type": "button"
                    })
            
            logger.debug(f"SoM detected {len(buttons)} buttons")
            return buttons
        except Exception as e:
            logger.warning(f"SoM detection failed: {e}")
            return []
    
    def add_labels_to_image(self, img_pil: Image.Image, elements: List[Dict[str, Any]]) -> Image.Image:
        """Draw numbered labels on image for visual grounding."""
        draw = ImageDraw.Draw(img_pil)
        
        for i, elem in enumerate(elements):
            center = elem.get("center", [])
            if center:
                x, y = center[0], center[1]
                label = str(i + 1)
                
                # Draw circle background
                r = 12
                draw.ellipse([x-r, y-r, x+r, y+r], fill="red", outline="white", width=2)
                
                # Draw number
                draw.text((x-4, y-6), label, fill="white")
        
        return img_pil
    
    def create_element_map(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create hash map: label -> coordinates for LLM reference."""
        element_map = {}
        for i, elem in enumerate(elements):
            label = str(i + 1)
            center = elem.get("center", [])
            if center:
                element_map[label] = {
                    "coordinates": center,
                    "text": elem.get("text", ""),
                    "type": elem.get("type", "element"),
                    "bbox": elem.get("bbox", [])
                }
        return element_map