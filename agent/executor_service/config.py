import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
    LOG_DIR = os.path.join(OUTPUT_DIR, "logs")
    ACTION_HISTORY_DIR = os.path.join(OUTPUT_DIR, "action_history")
    TASK_STATE_DIR = os.path.join(OUTPUT_DIR, "task_state")

    # --- Execution Speed (SLOW & ACCURATE) ---
    MOUSE_MOVE_DURATION = 0.5         # slower, more accurate mouse movement
    TYPING_INTERVAL = 0.05            # slower typing for accuracy
    DEFAULT_WAIT_SECONDS = 2.0        # wait after each action for UI to update
    ACTION_TIMEOUT_SECONDS = 15.0     # more time per action
    MAX_AGENT_ITERATIONS = int(os.getenv("MAX_AGENT_ITERATIONS", "10"))

    # --- Retry ---
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 1.0            # longer delay between retries
    RETRY_MAX_DELAY = 3.0

    # --- Safety ---
    DEFAULT_SAFETY_LEVEL = "LOW"
    DANGEROUS_KEYWORDS = [
        "sudo", "rm -rf", "delete", "format", "payment", "purchase",
        "checkout", "password", "credential", "shutdown", "reboot",
    ]

    # --- PyAutoGUI ---
    PYAUTOGUI_FAILSAFE = True
    PYAUTOGUI_PAUSE = 0.02             # minimal global pause

    # --- App Launch ---
    APP_LAUNCH_WAIT = 1.0              # reduced from 1.5
    SCREENSHOT_PRE_DELAY = 0.3

    # --- Element Cache ---
    ELEMENT_CACHE_TTL_MS = 5000        # cache elements for 5 seconds
    ELEMENT_CACHE_MAX_SIZE = 200

    # --- UI Compression ---
    MAX_UI_ELEMENTS_FOR_LLM = 40       # max elements to send to planner
    MIN_ELEMENT_CONFIDENCE = 0.3       # filter low-confidence OCR
    MIN_ELEMENT_TEXT_LENGTH = 1        # filter empty/tiny text

    @classmethod
    def setup_dirs(cls):
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        os.makedirs(cls.ACTION_HISTORY_DIR, exist_ok=True)
        os.makedirs(cls.TASK_STATE_DIR, exist_ok=True)

Config.setup_dirs()
