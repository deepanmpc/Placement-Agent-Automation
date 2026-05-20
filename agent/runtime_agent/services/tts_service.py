import os
import subprocess
from datetime import datetime
from runtime_agent.config import Config

import requests

class TTSService:
    def __init__(self):
        self.output_dir = os.path.join(Config.OUTPUT_DIR, "audio")
        self.api_key = Config.NVIDIA_TTS_API_KEY
        self.api_url = "https://integrate.api.nvidia.com/v1/audio/speech"
        
    def generate_audio(self, text: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = os.path.join(self.output_dir, f"tts_{timestamp}.wav")

        # Try NVIDIA TTS API first
        if self.api_key and Config.ENABLE_NVIDIA_TTS:
            try:
                response = requests.post(
                    self.api_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": Config.NVIDIA_TTS_MODEL,
                        "input": text,
                        "voice": "af_bella", # Example voice
                        "response_format": "wav"
                    }
                )
                response.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path
            except Exception as e:
                print(f"NVIDIA TTS failed, falling back: {e}")
        
        piper_binary = os.path.join(os.path.dirname(Config.BASE_DIR), ".venv", "bin", "piper")
        
        # Fix for broken shebang - use python -m piper instead
        piper_wrapper = os.path.join(Config.BASE_DIR, "piper_wrapper.sh")
        if os.path.exists(piper_binary):
            with open(piper_wrapper, 'w') as f:
                f.write("#!/bin/bash\nexec " + os.path.join(os.path.dirname(Config.BASE_DIR), ".venv", "bin", "python") + " -m piper \"$@\"\n")
            os.chmod(piper_wrapper, 0o755)
            piper_binary = piper_wrapper
        
        piper_model = os.path.join(Config.BASE_DIR, "models", "en_US-lessac-medium.onnx")
        
        if os.path.exists(piper_binary) and os.path.exists(piper_model):
            # Run offline Piper TTS
            escaped_text = text.replace("'", "").replace('"', "")
            command = f"echo '{escaped_text}' | {piper_binary} -m {piper_model} -f {output_path}"
            try:
                subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return output_path
            except subprocess.CalledProcessError as e:
                print(f"Piper TTS Error, falling back: {e}")
                
        # Fallback to ultra-fast native macOS `say`
        command = [
            "say",
            "-v", "Samantha",
            "--data-format=LEF32@22050",
            "-o", output_path,
            text
        ]
        
        try:
            subprocess.run(command, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"TTS Error: {e}")
            return ""
