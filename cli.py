import asyncio
import os
import sys
import time
import logging

# 1. SILENCE ALL NOISE (MUST BE FIRST)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PADDLE_TF_LOG_LEVEL'] = '3'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
logging.getLogger("numba").setLevel(logging.ERROR)
logging.getLogger("librosa").setLevel(logging.ERROR)

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED, MINIMAL

# Core Services
from runtime_agent.services.vision_client import VisionClient
from runtime_agent.services.microphone_service import MicrophoneService
from runtime_agent.services.tts_service import TTSService
from runtime_agent.services.audio_service import AudioService
from runtime_agent.services.llm_service import ConversationalLLMService
from planner_service.services.voice_service import VoiceService
from planner_service.planner import ReasoningEngine
from executor_service.executor import Executor
from executor_service.element_cache import ElementCache
from verifier_service.verifier import Verifier
from runtime_agent.config import Config as RuntimeConfig

class EdithCLI:
    def __init__(self):
        # 2. SILENCE STDOUT/STDERR DURING INIT
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        devnull = open(os.devnull, 'w')
        sys.stdout = devnull
        sys.stderr = devnull
        
        try:
            self.console = Console()
            self.vision = VisionClient()
            self.llm = ConversationalLLMService()
            self.tts = TTSService()
            self.audio = AudioService()
            self.mic = MicrophoneService()
            self.stt = VoiceService()
            self.planner = ReasoningEngine()
            self.executor = Executor()
            self.verifier = Verifier()
            self.element_cache = ElementCache()
        finally:
            # 3. RESTORE STREAMS
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
            devnull.close()
        
        self.mode = "chat" # chat or autonomous
        self.is_running = True

    def display_header(self):
        # High-fidelity Card inspired by the screenshot
        logo = Text()
        logo.append("  ▄▀  \n", style="bold cyan")
        logo.append(" █    \n", style="bold blue")
        logo.append("  ▀▄  ", style="bold red")
        
        info = Text()
        info.append("E.D.I.T.H. ", style="bold white")
        info.append("v2.0.42\n", style="dim white")
        info.append("Signed in as ", style="white")
        info.append("OPERATOR /auth\n", style="bold green")
        info.append("Plan: ", style="white")
        info.append("LEVEL ALPHA /root", style="bold blue")

        header_table = Table.grid(padding=(0, 2))
        header_table.add_row(logo, info)

        self.console.print("\n")
        self.console.print(Panel(
            header_table,
            box=MINIMAL,
            border_style="dim white",
            padding=(1, 2)
        ))
        self.console.print("[dim]" + "─" * 50 + "[/dim]\n")

    def print_system(self, text):
        self.console.print(f"[dim cyan]⚙ SYSTEM:[/dim cyan] [dim]{text}[/dim]")

    def print_agent(self, text):
        self.console.print("\n")
        self.console.print(Panel(
            Text(text, style="white"),
            title="[bold green]E.D.I.T.H.[/bold green]",
            title_align="left",
            border_style="green",
            box=ROUNDED,
            padding=(1, 2)
        ))
        self.console.print("\n")

    async def run(self):
        self.display_header()
        self.print_system("All systems nominal. Secure link established.")
        
        while self.is_running:
            try:
                mode_color = "blue" if self.mode == "chat" else "yellow"
                prompt = Text.assemble(
                    ("\n( ", "white"),
                    (self.mode.upper(), f"bold {mode_color}"),
                    (" ) ", "white"),
                    ("➤ ", "bold green")
                )
                
                user_input = self.console.input(prompt).strip()

                if not user_input:
                    continue

                cmd = user_input.lower()
                if cmd == 'exit':
                    self.print_system("Initiating shutdown sequence...")
                    self.is_running = False
                    break
                
                if cmd in ['chat', 'auto', 'mode']:
                    if cmd == 'mode':
                        self.mode = "autonomous" if self.mode == "chat" else "chat"
                    else:
                        self.mode = "chat" if cmd == 'chat' else "autonomous"
                    self.print_system(f"Mode switched to {self.mode.upper()}")
                    continue

                if cmd == 'v':
                    self.print_system("Listening...")
                    user_input = await self._get_voice_input()
                    if not user_input:
                        self.print_system("Silence detected.")
                        continue
                    self.console.print(f"[bold white]Voice Input:[/bold white] {user_input}")

                if self.mode == "chat":
                    await self._handle_chat(user_input)
                else:
                    from executor_service.main import agent_loop
                    self.print_system(f"Starting objective: {user_input}")
                    await agent_loop(user_input, self.vision, self.planner, self.executor, self.verifier, self.element_cache)
                    self.print_system("Objective cycle complete.")

            except KeyboardInterrupt:
                self.print_system("Interrupt received. Powering down.")
                break
            except Exception as e:
                self.console.print(f"[bold red]CRITICAL ERROR:[/bold red] {e}")
                import traceback
                self.console.print(traceback.format_exc())

    async def _get_voice_input(self) -> str:
        try:
            audio_path = self.mic.record_until_keypress()
            if not audio_path: return ""
            stt_res = await asyncio.to_thread(self.stt.transcribe_audio, audio_path)
            return stt_res.get("transcript", "")
        except Exception as e:
            self.print_system(f"STT Error: {e}")
            return ""

    async def _handle_chat(self, query: str):
        self.print_system("Analyzing visual context...")
        
        ui_state_str = "No visual context provided."
        keywords = ["screen", "see", "visible", "look", "page", "app", "window", "tab", "display", "what is on", "read"]
        if any(k in query.lower() for k in keywords):
            ui_state = await self.vision.capture_and_parse()
            elements = ui_state.get("elements", [])
            condensed = [f"[{e.get('type')}] '{e.get('text')}'" for e in elements if e.get('text')]
            ui_state_str = "\n".join(condensed[:20])

        prompt_path = os.path.join(RuntimeConfig.BASE_DIR, "prompts", "screen_analysis.txt")
        with open(prompt_path, "r") as f:
            template = f.read()
        
        prompt = template.replace("{query}", query).replace("{ui_state}", ui_state_str)
        self.print_system("Generating response...")
        response_text = await self.llm.generate_response(prompt)
        
        self.print_agent(response_text)
        
        try:
            audio_path = await asyncio.to_thread(self.tts.generate_audio, response_text)
            if audio_path:
                asyncio.create_task(self.audio.play_audio_async(audio_path))
        except Exception as e:
            self.print_system(f"TTS Error: {e}")

if __name__ == "__main__":
    cli = EdithCLI()
    asyncio.run(cli.run())
