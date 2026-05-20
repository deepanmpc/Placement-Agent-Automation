import os
from dotenv import load_dotenv

# Load env variables from root '.env' file
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_PATH, override=True)

class Config:
    # Planner Settings
    PLANNER_PORT = int(os.getenv("PLANNER_PORT", 8000))
    PLANNER_HOST = os.getenv("PLANNER_HOST", "127.0.0.1")
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
    
    # Storage
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
    DB_PATH = os.path.join(OUTPUT_DIR, "planner_state.db")
    
    # LLM Provider
    PLANNER_MODEL = os.getenv("PLANNER_MODEL", NVIDIA_REASONING_MODEL)
    
    # Chat Mode (separate from reasoning/agent mode)
    NVIDIA_CHAT_API_KEY = os.getenv("NVIDIA_CHAT_API_KEY")
    NVIDIA_CHAT_MODEL = os.getenv("NVIDIA_CHAT_MODEL", "meta/llama-3.3-70b-instruct")
    
    # STT Model
    NVIDIA_STT_API_KEY = os.getenv("NVIDIA_STT_API_KEY")
    NVIDIA_STT_MODEL = os.getenv("NVIDIA_STT_MODEL", "nvidia/canary-1b")
    ENABLE_NVIDIA_STT = os.getenv("ENABLE_NVIDIA_STT", "true").lower() == "true"
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    
    @classmethod
    def setup_dirs(cls):
        os.makedirs(os.path.join(cls.OUTPUT_DIR, "logs"), exist_ok=True)
        os.makedirs(os.path.join(cls.OUTPUT_DIR, "plans"), exist_ok=True)
        os.makedirs(os.path.join(cls.OUTPUT_DIR, "transcripts"), exist_ok=True)

Config.setup_dirs()
