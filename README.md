<p align="center">
  <h1 align="center">🤖 COWORK — Autonomous macOS Desktop Agent</h1>
  <p align="center">
    Give it a goal. It sees your screen, reasons, and acts — like a human co-worker who never sleeps.
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python" />
    <img src="https://img.shields.io/badge/Platform-macOS-black?style=flat-square&logo=apple" />
    <img src="https://img.shields.io/badge/LLM-NVIDIA_NIM-green?style=flat-square" />
    <img src="https://img.shields.io/badge/Voice-Whisper_+_Piper-orange?style=flat-square" />
    <img src="https://img.shields.io/badge/Vision-OmniParser_+_PaddleOCR-red?style=flat-square" />
  </p>
</p>

---

## What is COWORK?

COWORK is a fully autonomous desktop agent for macOS.

You type (or speak) a goal like:

> *"Open Google Docs and write a 500-word essay about Paris"*

And the agent:
1. **Sees** your screen via screenshot
2. **Understands** the current UI state (buttons, inputs, text)
3. **Plans** a sequence of actions using an LLM
4. **Executes** mouse clicks, keyboard inputs, and app shortcuts
5. **Verifies** each step completed correctly — and retries if not

No scripting. No automation rules. Just a goal.

---

## Architecture

```
User Goal / Voice Command
        │
        ▼
┌───────────────────┐
│   Voice / STT     │  ← Whisper (speech-to-text)
└────────┬──────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│                 Main Orchestrator Loop               │
│                   (runtime_agent)                    │
└──┬──────────┬────────────┬───────────────────┬──────┘
   │          │            │                   │
   ▼          ▼            ▼                   ▼
Vision     Planner      Executor           Verifier
Service    Service      Service            Service
   │          │            │                   │
   │     NVIDIA NIM    PyAutoGUI /         State Diff
   │     (LLM API)     Playwright /        Loop Detect
   │                   PyObjC              Retry Logic
   │
Screenshot → OCR → UI JSON (40-element compressed)
```

### The 4 Core Services

| Service | What it does |
|---|---|
| **`vision_service`** | Captures screen with MSS, runs PaddleOCR + OmniParser, returns structured UI JSON |
| **`planner_service`** | Feeds goal + UI state to NVIDIA LLM, gets back a batched action plan |
| **`executor_service`** | Translates actions into real OS events: clicks, typing, shortcuts, scrolls |
| **`verifier_service`** | Compares before/after UI state, detects loops, triggers recovery if needed |

### Key Optimizations

- **Coordinate Caching** — found a button once? It's cached. No re-scanning.
- **UI Compression** — dense screens capped at 40 elements before LLM sees them. No token bloat.
- **Batch Execution** — planner outputs a queue of actions, not one at a time. Faster loops.
- **Loop Detection** — verifier catches infinite retry spirals and breaks out intelligently.

---

## Prerequisites

- **macOS** (Ventura or later recommended)
- **Python 3.10+**
- **NVIDIA Build API Key** — get yours free at [build.nvidia.com](https://build.nvidia.com)
- **Accessibility + Screen Recording permissions** for your terminal (macOS Privacy Settings)

> [!IMPORTANT]
> You must grant **Accessibility** and **Screen Recording** permissions to your terminal app before running COWORK.
> Go to: **System Settings → Privacy & Security → Accessibility** and add your terminal.
> Without this, PyAutoGUI cannot control the mouse or keyboard.

---

## Setup & Installation

### Step 1 — Clone the Repository

```bash
git clone https://github.com/deepanmpc/COWORK_AGENT_DESKTOP_AUTOMATION.git
cd COWORK_AGENT_DESKTOP_AUTOMATION
```

### Step 2 — Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> [!NOTE]
> First install takes a few minutes — it pulls PyTorch, PaddleOCR, Playwright, and other heavy packages.
> After install, also run: `playwright install chromium`

### Step 4 — Get Your NVIDIA API Key

COWORK uses [NVIDIA Build](https://build.nvidia.com) to access powerful LLMs (Llama, Nemotron, GPT-OSS models) via a single API endpoint.

1. Go to **[build.nvidia.com](https://build.nvidia.com)**
2. Sign up or log in (free account)
3. Navigate to **API Keys** and generate a new key
4. You'll use this key in the next step

> [!TIP]
> NVIDIA Build gives you free credits to start. The models used by COWORK (Llama 4 Maverick, GPT-OSS 120B, Nemotron) are all available on their free tier.

### Step 5 — Configure Environment Variables

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

Now open `.env` and replace the placeholder values:

```ini
# ─── NVIDIA Build API ───────────────────────────────────────────────────
NVIDIA_API_BASE_URL=https://integrate.api.nvidia.com/v1

# Get your key from: https://build.nvidia.com → API Keys
# You can use ONE key for all three, or create separate keys per model
NVIDIA_REASONING_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NVIDIA_VISION_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NVIDIA_PARSER_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Fallback key (used if specific keys above are empty)
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ─── Model Selection ────────────────────────────────────────────────────
# Reasoning model — handles multi-step planning
# Options: openai/gpt-oss-120b | meta/llama-3.3-70b-instruct
NVIDIA_REASONING_MODEL=openai/gpt-oss-120b
NVIDIA_FALLBACK_MODEL=meta/llama-3.3-70b-instruct

# Vision model — interprets screenshots
VISION_VLM_MODEL=meta/llama-4-maverick-17b-128e-instruct

# Parser model — extracts structured UI elements
NEMOTRON_PARSER_MODEL=nvidia/nemotron-parse

# ─── Optional: Enable Cloud Vision & Parser ──────────────────────────────
# Set to true to use NVIDIA cloud models for vision/parsing
# Default: false (uses local MSS + PaddleOCR, which is faster)
ENABLE_VISION_VLM=false
ENABLE_NEMOTRON_PARSER=false

# ─── LLM Parameters ─────────────────────────────────────────────────────
NVIDIA_MAX_TOKENS=4096
NVIDIA_TEMPERATURE=0.2
NVIDIA_TOP_P=0.7
NVIDIA_STREAM=true
LLM_TIMEOUT=45

# ─── Vision Parameters ───────────────────────────────────────────────────
VISION_API_TIMEOUT=30
VISION_MAX_TOKENS=1024

# ─── Agent Behaviour ─────────────────────────────────────────────────────
MAX_AGENT_ITERATIONS=10
```

> [!WARNING]
> Never commit your `.env` file. It's already in `.gitignore`, but double-check before pushing.

---

## Running COWORK

### Option A — CLI Mode (Recommended)

```bash
PYTHONPATH=. python cli.py
```

You'll see the EDITH interface. Then:

| Input | What happens |
|---|---|
| Type your goal + `Enter` | Agent runs autonomously |
| Type `v` + `Enter` | Speak your goal (voice mode via Whisper) |
| Press `ESC` | Immediately halt execution |
| Type `exit` or `quit` | Exit the agent |

**Example goals to try:**

```
→ Open Safari and go to github.com
→ Create a new note in Apple Notes titled "Meeting Summary"
→ Open Spotify and search for lo-fi hip hop
→ Write a 300-word blog post about AI in Google Docs
→ Open the calculator and compute 2847 × 391
```

### Option B — Direct Python

```bash
PYTHONPATH=. python main.py
```

### Option C — Executor Service Only

```bash
cd executor_service
PYTHONPATH=.. python main.py
```

---

## Project Structure

```
COWORK_AGENT_DESKTOP_AUTOMATION/
│
├── runtime_agent/          # Master orchestrator loop
│   ├── config.py           # Global runtime configuration
│   └── services/           # Vision client, TTS, microphone, LLM chat
│
├── vision_service/         # Screen capture + UI understanding
│   ├── screenshot.py       # MSS screen capture
│   ├── ocr.py              # PaddleOCR text extraction
│   ├── parser.py           # Structured UI JSON builder
│   ├── som_detector.py     # OmniParser YOLO element detection
│   └── nvidia_vision.py    # NVIDIA cloud vision (optional)
│
├── planner_service/        # LLM-powered action planning
│   ├── planner.py          # ReasoningEngine — core planning logic
│   ├── prompt_builder.py   # Builds goal + UI state prompts
│   ├── schemas.py          # Action type definitions
│   └── task_memory.py      # Short-term task context
│
├── executor_service/       # OS-level action execution
│   ├── executor.py         # Main executor dispatcher
│   ├── action_router.py    # Routes actions to correct handler
│   ├── element_cache.py    # Coordinate caching layer
│   ├── ui_compressor.py    # Compresses UI to 40-element cap
│   ├── interrupt_manager.py# ESC key interrupt handler
│   └── actions/            # Click, type, scroll, key handlers
│
├── verifier_service/       # Post-action verification
│   ├── verifier.py         # Main verifier logic
│   ├── state_diff.py       # Before/after UI comparison
│   ├── loop_detector.py    # Detects stuck retry loops
│   └── completion_detector.py # Goal completion check
│
├── memory/                 # Session and episodic memory
│   ├── session.py          # Redis-backed session state
│   └── episodic.py         # Long-term task history
│
├── OmniParser/             # Microsoft OmniParser (UI grounding model)
├── main.py                 # Entry point
├── cli.py                  # EDITH CLI interface
├── best.pt                 # YOLO weights for UI element detection
├── requirements.txt        # All Python dependencies
├── .env.example            # Environment variable template
└── .gitignore
```

---

## Model Guide

COWORK uses **3 different models** from NVIDIA Build for different jobs:

| Role | Model | Why |
|---|---|---|
| **Reasoning / Planner** | `openai/gpt-oss-120b` | Best at multi-step task planning and recovery |
| **Fallback Planner** | `meta/llama-3.3-70b-instruct` | Faster, cheaper, great for simple tasks |
| **Vision** | `meta/llama-4-maverick-17b-128e-instruct` | Understands screenshots and UI layouts |
| **Parser** | `nvidia/nemotron-parse` | Structured element extraction from raw UI |

> [!TIP]
> **For longer, complex tasks** (10+ steps), the `gpt-oss-120b` model is recommended. If you want even stronger reasoning, you can swap in `openai/o3` or `anthropic/claude-opus-4` via NVIDIA's compatible API endpoint — just update `NVIDIA_REASONING_MODEL` in your `.env`.

---

## Troubleshooting

**Agent clicks in the wrong place**
→ Check your display scaling. If you use a Retina display, ensure `screenshot.py` is using the correct DPI scale factor.

**`NSAccessibilityException` or clicks do nothing**
→ Your terminal app doesn't have Accessibility permission. Go to System Settings → Privacy & Security → Accessibility and add it.

**`NVIDIA_API_KEY` errors**
→ Make sure your `.env` file is in the root directory and `python-dotenv` is installed. Double-check the key starts with `nvapi-`.

**PaddleOCR install fails**
→ Run: `pip install paddlepaddle paddleocr --upgrade`. On Apple Silicon, you may need `pip install paddlepaddle-gpu` instead.

**Voice mode not working**
→ Make sure your microphone has permission in System Settings → Privacy & Security → Microphone.

---

## Roadmap

- [ ] Swap reasoning model to `o3` / `claude-opus-4` for longer autonomous runs
- [ ] Windows support via `xdotool` equivalent
- [ ] Web dashboard for task monitoring
- [ ] Persistent episodic memory across sessions (Qdrant)
- [ ] Task scheduling (run goals on a cron)

---

## Contributing

PRs welcome. If you're building on COWORK or extending it with a new model backend, open an issue first to discuss — happy to help integrate it cleanly.

---

## License

MIT

---

<p align="center">Built by <a href="https://github.com/deepanmpc">deepanmpc</a> · Powered by NVIDIA Build · Vision by OmniParser + PaddleOCR</p>