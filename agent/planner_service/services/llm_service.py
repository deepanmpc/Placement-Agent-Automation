from typing import Dict, Any
from vision_service.utils.logger import logger
from planner_service.config import Config
from planner_service.services.nvidia_chat import NvidiaChatClient, extract_json_object

class LLMService:
    def __init__(self):
        self.chat = NvidiaChatClient(
            api_key=Config.NVIDIA_API_KEY,
            base_url=Config.NVIDIA_API_BASE_URL,
            model=Config.PLANNER_MODEL,
            fallback_model=Config.NVIDIA_FALLBACK_MODEL,
            max_tokens=Config.NVIDIA_MAX_TOKENS,
            temperature=Config.NVIDIA_TEMPERATURE,
            top_p=Config.NVIDIA_TOP_P,
            timeout=Config.LLM_TIMEOUT,
            stream=Config.NVIDIA_STREAM,
        )

    async def generate_plan(self, prompt: str) -> Dict[str, Any]:
        """Calls the NVIDIA API and returns a validated JSON object."""
        try:
            response_text, reasoning, model = await self.chat.complete(prompt, force_json=True)
            if reasoning:
                logger.debug(f"Planner reasoning received from {model} ({len(reasoning)} chars).")

            parsed = extract_json_object(response_text)
            if parsed:
                return parsed

            logger.error(f"Failed to parse planner JSON output from {model}: {response_text}")
        except Exception as e:
            logger.error(f"Planner LLM call failed: {e}")

        return {}
