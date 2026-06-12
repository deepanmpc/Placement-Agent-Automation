from rich.console import Console

from verifier_service.config import Config
from planner_service.services.nvidia_chat import NvidiaChatClient, extract_json_object

console = Console()


class VerifierLLMService:
    """LLM service for verification reasoning (uses same NVIDIA API as planner)."""

    def __init__(self):
        self.chat = NvidiaChatClient(
            base_url=Config.NVIDIA_API_BASE,
            api_key=Config.NVIDIA_API_KEY,
            model=Config.VERIFIER_MODEL,
            fallback_model=Config.NVIDIA_FALLBACK_MODEL,
            max_tokens=Config.NVIDIA_MAX_TOKENS,
            temperature=Config.NVIDIA_TEMPERATURE,
            top_p=Config.NVIDIA_TOP_P,
            timeout=Config.LLM_TIMEOUT,
            stream=Config.NVIDIA_STREAM,
        )

    async def query(self, prompt: str) -> dict:
        """Send a verification prompt and parse JSON response."""
        try:
            text, _, model = await self.chat.complete(prompt, force_json=True)
            parsed = extract_json_object(text)
            if parsed:
                return parsed
            console.print(f"  [dim][Verifier LLM] JSON parse error from {model}[/dim]")
            return {}
        except Exception as e:
            console.print(f"  [dim][Verifier LLM] Error: {e}[/dim]")
            return {}
