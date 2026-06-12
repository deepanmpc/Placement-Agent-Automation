import os
from dotenv import load_dotenv

# Load env variables from root '.env' file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), override=True)


class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
    LOG_DIR = os.path.join(OUTPUT_DIR, "logs")
    VERIFICATION_HISTORY_DIR = os.path.join(OUTPUT_DIR, "verification_history")
    FAILURE_CASES_DIR = os.path.join(OUTPUT_DIR, "failure_cases")
    PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

    # --- Verification Tuning ---
    # Maximum number of identical states before declaring a loop
    LOOP_DETECTION_THRESHOLD = 3
    # Maximum repeated identical actions before declaring a loop
    ACTION_REPEAT_THRESHOLD = 3
    # Minimum element overlap ratio to consider two states "same"
    STATE_SIMILARITY_THRESHOLD = 0.85
    # Minimum confidence for LLM verification to be trusted
    LLM_CONFIDENCE_THRESHOLD = 0.6

    # --- LLM ---
    NVIDIA_API_BASE = os.getenv("NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_API_KEY = os.getenv("NVIDIA_REASONING_API_KEY") or os.getenv("NVIDIA_API_KEY")
    NVIDIA_REASONING_MODEL = os.getenv("NVIDIA_REASONING_MODEL", "openai/gpt-oss-120b")
    NVIDIA_FALLBACK_MODEL = os.getenv("NVIDIA_FALLBACK_MODEL", "meta/llama-3.3-70b-instruct")
    NVIDIA_MAX_TOKENS = int(os.getenv("NVIDIA_MAX_TOKENS", "4096"))
    NVIDIA_TEMPERATURE = float(os.getenv("NVIDIA_TEMPERATURE", "0.2"))
    NVIDIA_TOP_P = float(os.getenv("NVIDIA_TOP_P", "0.7"))
    NVIDIA_STREAM = os.getenv("NVIDIA_STREAM", "true").lower() == "true"
    VERIFIER_MODEL = os.getenv("VERIFIER_MODEL", NVIDIA_REASONING_MODEL)

    # --- Timeouts ---
    VERIFICATION_TIMEOUT = 5.0  # seconds for full verification pass
    LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "45"))

    @classmethod
    def setup_dirs(cls):
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        os.makedirs(cls.VERIFICATION_HISTORY_DIR, exist_ok=True)
        os.makedirs(cls.FAILURE_CASES_DIR, exist_ok=True)


Config.setup_dirs()
