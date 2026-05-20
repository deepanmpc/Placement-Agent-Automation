from typing import Dict, Any
from faster_whisper import WhisperModel
from vision_service.utils.logger import logger
from planner_service.config import Config
import os

import requests
import base64

class VoiceService:
    def __init__(self):
        self.model_size = Config.WHISPER_MODEL
        self._model = None
        self.api_key = Config.NVIDIA_STT_API_KEY
        self.api_url = "https://integrate.api.nvidia.com/v1/audio/transcriptions"

    def _get_model(self) -> WhisperModel:
        if not self._model:
            logger.info(f"Loading FasterWhisper model '{self.model_size}'...")
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        return self._model

    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        # Try NVIDIA STT API first
        if self.api_key and Config.ENABLE_NVIDIA_STT:
            try:
                with open(audio_path, "rb") as f:
                    response = requests.post(
                        self.api_url,
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        files={"file": f},
                        data={"model": Config.NVIDIA_STT_MODEL, "response_format": "json"}
                    )
                response.raise_for_status()
                data = response.json()
                return {
                    "transcript": data.get("text", "").strip(),
                    "language": "en",
                    "confidence": 1.0,
                    "source": "nvidia"
                }
            except Exception as e:
                logger.warning(f"NVIDIA STT failed, falling back to local: {e}")

        # Fallback to Local FasterWhisper
        model = self._get_model()
        segments, info = model.transcribe(audio_path, beam_size=5)
        transcript = "".join([segment.text for segment in segments])
        
        return {
            "transcript": transcript.strip(),
            "language": info.language,
            "confidence": info.language_probability,
            "source": "local"
        }
