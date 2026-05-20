import base64
import io
from typing import Any, Dict, Optional

from openai import OpenAI
from PIL import Image

from planner_service.services.nvidia_chat import extract_json_object
from vision_service.config import Config


def _image_to_data_url(img: Image.Image) -> str:
    """Convert a PIL image to a compact JPEG data URL for NVIDIA chat completions."""
    rgb = img.convert("RGB")
    buffer = io.BytesIO()
    rgb.save(buffer, format="JPEG", quality=Config.COMPRESSION_QUALITY, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


class NvidiaVisionService:
    """Optional hosted VLM/parser enrichment for screenshot understanding."""

    def __init__(self):
        self.base_url = Config.NVIDIA_API_BASE_URL
        self.vision_key = Config.NVIDIA_VISION_API_KEY
        self.parser_key = Config.NVIDIA_PARSER_API_KEY

    def _client(self, api_key: Optional[str], key_name: str) -> OpenAI:
        if not api_key:
            raise RuntimeError(f"{key_name} is not set.")
        return OpenAI(base_url=self.base_url, api_key=api_key)

    def _chat_image_json(
        self,
        *,
        api_key: Optional[str],
        key_name: str,
        model: str,
        img: Image.Image,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float = 0.0,
        image_only: bool = False,
    ) -> Dict[str, Any]:
        client = self._client(api_key, key_name)
        
        if image_only:
            content = [{"type": "image_url", "image_url": {"url": _image_to_data_url(img)}}]
        else:
            content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": _image_to_data_url(img)}},
            ]
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            max_tokens=max_tokens or Config.VISION_MAX_TOKENS,
            temperature=temperature,
            top_p=1.0,
            stream=False,
        )
        result_content = response.choices[0].message.content or "{}"
        return extract_json_object(result_content)

    def parse_ui(self, img: Image.Image) -> Dict[str, Any]:
        """
        Ask Nemotron Parse for structured screen text/metadata.

        Expected output is normalized defensively because hosted parser schemas can vary.
        """
        prompt = "Analyze this desktop screenshot and return JSON with UI elements."
        return self._chat_image_json(
            api_key=self.parser_key,
            key_name="NVIDIA_PARSER_API_KEY",
            model=Config.NEMOTRON_PARSER_MODEL,
            img=img,
            prompt=prompt,
            max_tokens=Config.VISION_MAX_TOKENS,
            image_only=True,
        )

    def describe_screen(self, img: Image.Image) -> Dict[str, Any]:
        """Ask the vision VLM for a compact semantic summary of the current screen."""
        prompt = """
Describe this desktop screenshot for an autonomous computer-use agent.
Return only JSON:
{
  "summary": "what screen/app/page is visible",
  "likely_task_state": "what appears to be happening",
  "important_targets": ["short visible labels that may be useful to click"]
}
"""
        return self._chat_image_json(
            api_key=self.vision_key,
            key_name="NVIDIA_VISION_API_KEY",
            model=Config.VISION_VLM_MODEL,
            img=img,
            prompt=prompt,
            max_tokens=512,
        )
