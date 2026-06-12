from typing import Dict, Any
import asyncio
from vision_service.screenshot import ScreenshotCapturer
from vision_service.ocr import extract_text
from vision_service.parser import parse_ui

class VisionClient:
    def __init__(self):
        # We reuse the robust modules built in Phase 1 for on-demand capture
        self.capturer = ScreenshotCapturer()

    async def capture_and_parse(self) -> Dict[str, Any]:
        """Takes a fresh active window screenshot and returns the parsed UI elements."""
        print("[Vision] Capturing active window...")
        
        # Run synchronous capture in a background thread to not block async loop
        def _capture():
            img_np, img_pil, saved_path = self.capturer.capture_active_window()
            capture_info = dict(self.capturer.last_capture_info)
            ocr_data = extract_text(img_np)
            parsed_ui_state = parse_ui(img_pil, ocr_data, capture_info)
            return parsed_ui_state
            
        parsed_ui = await asyncio.to_thread(_capture)
        print(f"[Vision] Detected {len(parsed_ui['elements'])} UI elements.")
        
        return parsed_ui
