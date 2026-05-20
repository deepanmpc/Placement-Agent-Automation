import os
from dotenv import load_dotenv

# Load env variables from root '.env' file
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_PATH, override=True)

class Config:
    # Outputs
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
    SCREENSHOTS_DIR = os.path.join(OUTPUT_DIR, "screenshots")
    PARSED_DIR = os.path.join(OUTPUT_DIR, "parsed")
    LOGS_DIR = os.path.join(OUTPUT_DIR, "logs")

    # API configuration
    PLANNER_URL = os.getenv("PLANNER_URL", "http://localhost:8000/planner/context")
    PLANNER_TIMEOUT_SEC = 5.0
    NVIDIA_API_BASE_URL = os.getenv("NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_VISION_API_KEY = os.getenv("NVIDIA_VISION_API_KEY") or os.getenv("NVIDIA_API_KEY")
    NVIDIA_PARSER_API_KEY = (
        os.getenv("NVIDIA_PARSER_API_KEY")
        or os.getenv("NVIDIA_VISION_API_KEY")
        or os.getenv("NVIDIA_API_KEY")
    )

    if not NVIDIA_VISION_API_KEY:
        import sys
        print(f"DEBUG: NVIDIA_VISION_API_KEY not found in {ENV_PATH}", file=sys.stderr)
    else:
        import sys
        print(f"DEBUG: NVIDIA_VISION_API_KEY loaded successfully (starts with {NVIDIA_VISION_API_KEY[:10]})", file=sys.stderr)
    VISION_VLM_MODEL = os.getenv("VISION_VLM_MODEL", "meta/llama-4-maverick-17b-128e-instruct")
    NEMOTRON_PARSER_MODEL = os.getenv("NEMOTRON_PARSER_MODEL", "nvidia/nemotron-parse")
    ENABLE_VISION_VLM = os.getenv("ENABLE_VISION_VLM", "false").lower() == "true"
    ENABLE_NEMOTRON_PARSER = os.getenv("ENABLE_NEMOTRON_PARSER", "false").lower() == "true"
    VISION_API_TIMEOUT = float(os.getenv("VISION_API_TIMEOUT", "30"))
    VISION_MAX_TOKENS = int(os.getenv("VISION_MAX_TOKENS", "1024"))

    # Vision constraints
    MAX_IMAGE_SIZE = (1920, 1080)
    COMPRESSION_QUALITY = 85
    
    # Execution
    FPS_TARGET = float(os.getenv("FPS_TARGET", "2.0"))

# Ensure directories exist
os.makedirs(Config.SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(Config.PARSED_DIR, exist_ok=True)
os.makedirs(Config.LOGS_DIR, exist_ok=True)
