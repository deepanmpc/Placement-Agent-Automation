import asyncio
import uuid
import time
from typing import Optional

from vision_service.config import Config
from vision_service.utils.logger import logger
from vision_service.utils.timings import global_metrics
from vision_service.screenshot import ScreenshotCapturer
from vision_service.ocr import extract_text
from vision_service.parser import parse_ui
from vision_service.planner_client import PlannerClient
from vision_service.schemas import PlannerPayload

class VisionPipeline:
    def __init__(self):
        self.capturer = ScreenshotCapturer()
        self.planner_client = PlannerClient()
        self.session_id = uuid.uuid4().hex
        self.running = False

    async def run_cycle(self) -> Optional[float]:
        """Runs a single pass of the vision pipeline. Returns cycle duration in ms."""
        frame_id = uuid.uuid4().hex[:8]
        logger.info(f"--- Starting Frame: {frame_id} ---")
        
        with global_metrics.measure("total_pipeline_cycle"):
            # 1. Capture Screenshot (Active Window Only)
            img_np, img_pil, saved_path = self.capturer.capture_active_window()
            capture_info = dict(self.capturer.last_capture_info)
            
            # 2. Extract Text via OCR
            ocr_data = extract_text(img_np)
            
            # 3. Parse UI (Combine OCR + OmniParser)
            parsed_ui_state = parse_ui(img_pil, ocr_data, capture_info)
            
            # 4. Build Payload
            payload = PlannerPayload(
                session_id=self.session_id,
                frame_id=frame_id,
                screen=parsed_ui_state["screen"],
                elements=parsed_ui_state["elements"],
                relationships=parsed_ui_state["relationships"],
                metadata=parsed_ui_state.get("metadata", ocr_data["metadata"])
            )
            
            # 5. Send to Planner Service
            await self.planner_client.send_to_planner(payload.model_dump())
            
        metrics = global_metrics.get_metrics()
        logger.info(f"Metrics | Capture: {metrics.get('screenshot_capture', 0):.1f}ms | "
                    f"OCR: {metrics.get('ocr_extraction', 0):.1f}ms | "
                    f"Parse: {metrics.get('semantic_parsing', 0):.1f}ms | "
                    f"End-to-End: {metrics.get('total_pipeline_cycle', 0):.1f}ms")
                    
        return metrics.get('total_pipeline_cycle')

    async def start(self):
        """Starts the continuous asynchronous vision pipeline."""
        logger.info(f"Starting Vision Service Pipeline. Session ID: {self.session_id}")
        self.running = True
        
        target_frame_time = 1.0 / Config.FPS_TARGET
        
        try:
            while self.running:
                cycle_start = time.time()
                
                await self.run_cycle()
                
                # Throttle to maintain target FPS
                elapsed = time.time() - cycle_start
                sleep_time = max(0, target_frame_time - elapsed)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    
        except asyncio.CancelledError:
            logger.info("Pipeline cancelled.")
        except Exception as e:
            logger.error(f"Pipeline crashed: {e}")
        finally:
            await self.shutdown()

    async def shutdown(self):
        logger.info("Shutting down Vision Service...")
        self.running = False
        await self.planner_client.close()

if __name__ == "__main__":
    pipeline = VisionPipeline()
    try:
        asyncio.run(pipeline.start())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting.")
