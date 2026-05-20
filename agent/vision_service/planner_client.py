import httpx
import json
from typing import Dict, Any
from vision_service.config import Config
from vision_service.utils.logger import logger
from vision_service.utils.timings import global_metrics

class PlannerClient:
    def __init__(self):
        self.url = Config.PLANNER_URL
        self.timeout = Config.PLANNER_TIMEOUT_SEC
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def send_to_planner(self, payload: Dict[str, Any]) -> bool:
        """
        Sends the parsed UI state to the Planner Service.
        """
        with global_metrics.measure("planner_api_request"):
            try:
                response = await self.client.post(
                    self.url,
                    json=payload
                )
                response.raise_for_status()
                logger.debug(f"Payload successfully sent to planner. Status: {response.status_code}")
                return True
            except httpx.HTTPError as e:
                logger.error(f"Failed to send payload to planner: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error sending payload: {e}")
                return False

    async def close(self):
        await self.client.aclose()
