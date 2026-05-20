import os
import requests

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

PIPER_MODEL_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
PIPER_CONFIG_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"

def download_file(url, dest):
    print(f"Downloading {os.path.basename(dest)}...")
    response = requests.get(url, stream=True)
    with open(dest, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Done.")

if __name__ == "__main__":
    print("Downloading Piper TTS Model (en_US-lessac-medium)...")
    download_file(PIPER_MODEL_URL, os.path.join(MODEL_DIR, "en_US-lessac-medium.onnx"))
    download_file(PIPER_CONFIG_URL, os.path.join(MODEL_DIR, "en_US-lessac-medium.onnx.json"))
    
    print("\nModels downloaded successfully to runtime_agent/models/")
    print("Faster-Whisper (STT) model will automatically download on first run.")
