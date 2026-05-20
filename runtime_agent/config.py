import os
from dotenv import load_dotenv

# Load env variables from root '.env' file
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_PATH, override=True)

class Config:
    # Runtime Settings
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
    
    # Endpoints for existing services
    VISION_SERVICE_URL = os.getenv("VISION_SERVICE_URL", "http://127.0.0.1:8000/context/vision") 
    
    # LLM Settings (NVIDIA API)
    NVIDIA_API_BASE_URL = os.getenv("NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_API_KEY = os.getenv("NVIDIA_REASONING_API_KEY") or os.getenv("NVIDIA_API_KEY")

    if not NVIDIA_API_KEY:
        import sys
        print(f"DEBUG: NVIDIA_API_KEY not found in {ENV_PATH}", file=sys.stderr)
    else:
        import sys
        print(f"DEBUG: NVIDIA_API_KEY loaded successfully (starts with {NVIDIA_API_KEY[:10]})", file=sys.stderr)
    NVIDIA_REASONING_MODEL = os.getenv("NVIDIA_REASONING_MODEL", "openai/gpt-oss-120b")
    NVIDIA_FALLBACK_MODEL = os.getenv("NVIDIA_FALLBACK_MODEL", "meta/llama-3.3-70b-instruct")
    NVIDIA_MAX_TOKENS = int(os.getenv("NVIDIA_MAX_TOKENS", "4096"))
    NVIDIA_TEMPERATURE = float(os.getenv("NVIDIA_TEMPERATURE", "0.2"))
    NVIDIA_TOP_P = float(os.getenv("NVIDIA_TOP_P", "0.7"))
    NVIDIA_STREAM = os.getenv("NVIDIA_STREAM", "true").lower() == "true"
    LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "45"))
    LLM_MODEL = os.getenv("LLM_MODEL", NVIDIA_REASONING_MODEL)
    
    # Chat Mode
    NVIDIA_CHAT_API_KEY = os.getenv("NVIDIA_CHAT_API_KEY")
    NVIDIA_CHAT_MODEL = os.getenv("NVIDIA_CHAT_MODEL", "meta/llama-3.3-70b-instruct")
    
    # TTS & STT Settings
    NVIDIA_TTS_API_KEY = os.getenv("NVIDIA_TTS_API_KEY")
    NVIDIA_STT_API_KEY = os.getenv("NVIDIA_STT_API_KEY")
    NVIDIA_TTS_MODEL = os.getenv("NVIDIA_TTS_MODEL", "nvidia/canary-1b")
    NVIDIA_STT_MODEL = os.getenv("NVIDIA_STT_MODEL", "nvidia/canary-1b")
    ENABLE_NVIDIA_TTS = os.getenv("ENABLE_NVIDIA_TTS", "true").lower() == "true"
    
    # TTS Settings
    TTS_VOICE = "en_US-lessac-medium" # Example piper voice
    
    @classmethod
    def setup_dirs(cls):
        os.makedirs(os.path.join(cls.OUTPUT_DIR, "audio"), exist_ok=True)
        os.makedirs(os.path.join(cls.OUTPUT_DIR, "screenshots"), exist_ok=True)
        os.makedirs(os.path.join(cls.OUTPUT_DIR, "transcripts"), exist_ok=True)
        os.makedirs(os.path.join(cls.OUTPUT_DIR, "logs"), exist_ok=True)

Config.setup_dirs()
