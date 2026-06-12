from runtime_agent.config import Config
from planner_service.services.nvidia_chat import NvidiaChatClient

class ConversationalLLMService:
    def __init__(self):
        self.chat = NvidiaChatClient(
            api_key=Config.NVIDIA_API_KEY,
            base_url=Config.NVIDIA_API_BASE_URL,
            model=Config.LLM_MODEL,
            fallback_model=Config.NVIDIA_FALLBACK_MODEL,
            max_tokens=Config.NVIDIA_MAX_TOKENS,
            temperature=Config.NVIDIA_TEMPERATURE,
            top_p=Config.NVIDIA_TOP_P,
            timeout=Config.LLM_TIMEOUT,
            stream=Config.NVIDIA_STREAM,
        )

    async def generate_response(self, prompt: str) -> str:
        """Calls NVIDIA API via OpenAI SDK and returns standard text."""
        try:
            content, _, _ = await self.chat.complete(prompt)
            return content or "Sorry, I couldn't generate a response."
        except Exception as e:
            print(f"LLM attempt failed (Type: {type(e)}): {e}")
            return "Sorry, all LLM connection attempts failed."
