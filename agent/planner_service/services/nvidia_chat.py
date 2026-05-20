import json
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI


def extract_json_object(text: str) -> Dict[str, Any]:
    """Parse a JSON object, tolerating markdown fences and extra model text."""
    cleaned = (text or "").strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json") :].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```") :].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[: -len("```")].strip()

    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}

    try:
        parsed = json.loads(cleaned[start : end + 1])
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


class NvidiaChatClient:
    """Small OpenAI-compatible NVIDIA client with optional streaming support."""

    def __init__(
        self,
        *,
        api_key: Optional[str],
        base_url: str,
        model: str,
        fallback_model: Optional[str],
        max_tokens: int,
        temperature: float,
        top_p: float,
        timeout: float,
        stream: bool,
    ):
        self.api_key = api_key
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key or "missing-nvidia-api-key")
        self.model = model
        self.fallback_model = fallback_model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.timeout = timeout
        self.stream = stream

    @property
    def models_to_try(self) -> List[str]:
        if self.fallback_model and self.fallback_model != self.model:
            return [self.model, self.fallback_model]
        return [self.model]

    async def complete(self, prompt: str, *, force_json: bool = False) -> tuple[str, str, str]:
        """
        Return (content, reasoning, model_used).

        Some NVIDIA-hosted reasoning models stream `delta.reasoning_content`; we keep it
        separate from final content so JSON parsing is not polluted by reasoning tokens.
        """
        suffix = ""
        if force_json:
            suffix = "\n\nCRITICAL: Respond ONLY with one raw valid JSON object. No markdown. No prose."

        last_error = None
        if not self.api_key:
            raise RuntimeError(
                "NVIDIA reasoning API key is not set. Add NVIDIA_REASONING_API_KEY "
                "or NVIDIA_API_KEY to the environment or a local .env file."
            )

        for model in self.models_to_try:
            try:
                if self.stream:
                    stream = await self.client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt + suffix}],
                        temperature=self.temperature,
                        top_p=self.top_p,
                        max_tokens=self.max_tokens,
                        stream=True,
                        timeout=self.timeout,
                    )
                    content_parts: list[str] = []
                    reasoning_parts: list[str] = []
                    async for chunk in stream:
                        if not getattr(chunk, "choices", None):
                            continue
                        delta = chunk.choices[0].delta
                        reasoning = getattr(delta, "reasoning_content", None)
                        if reasoning:
                            reasoning_parts.append(reasoning)
                        if delta.content is not None:
                            content_parts.append(delta.content)
                    return "".join(content_parts), "".join(reasoning_parts), model

                completion = await self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt + suffix}],
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_tokens,
                    timeout=self.timeout,
                )
                content = completion.choices[0].message.content or ""
                reasoning = getattr(completion.choices[0].message, "reasoning_content", "") or ""
                return content, reasoning, model
            except Exception as exc:
                last_error = exc

        if last_error:
            raise last_error
        return "", "", self.model
