import asyncio
import os
import sys
import uuid
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live
from rich.table import Table

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

# Config
from runtime_agent.config import Config as RuntimeConfig

console = Console()

class AgentCLI:
    def __init__(self):
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
        
        self.mode = "chat" # chat or autonomous
        self.is_running = True

    def display_welcome(self):
        welcome_text = (
            "[bold magenta]Gemini Desktop Agent CLI[/bold magenta]\n"
            "-----------------------------------\n"
            "Modes:\n"
            "  - [bold cyan]Chat Mode[/bold cyan]: Talk to the agent about your screen.\n"
            "  - [bold yellow]Autonomous Mode[/bold yellow]: Give a goal, and the agent executes it.\n\n"
            "Commands:\n"
            "  - [bold green]'v'[/bold green]: Trigger Voice Input\n"
            "  - [bold green]'mode'[/bold green]: Toggle between Chat and Autonomous\n"
            "  - [bold green]'exit'[/bold green]: Quit the CLI"
        )
        console.print(Panel(welcome_text, title="🤖 Welcome", border_style="magenta"))

    async def run(self):
        self.display_welcome()
        
        while self.is_running:
            try:
                mode_str = f"[bold cyan]CHAT[/bold cyan]" if self.mode == "chat" else f"[bold yellow]AUTO[/bold yellow]"
                prompt_text = f"\n({mode_str}) [bold white]Enter query/goal[/bold white]"
                user_input = Prompt.ask(prompt_text).strip()

                if user_input.lower() == 'exit':
                    self.is_running = False
                    break
                
                if user_input.lower() == 'mode':
                    self.mode = "autonomous" if self.mode == "chat" else "chat"
                    console.print(f"[dim]Switched to {self.mode} mode.[/dim]")
                    continue

                if user_input.lower() == 'v':
                    user_input = await self._get_voice_input()
                    if not user_input: continue
                    console.print(f"[bold green]Voice Input:[/bold green] {user_input}")

                if not user_input:
                    continue

                if self.mode == "chat":
                    await self._handle_chat(user_input)
                else:
                    from executor_service.main import agent_loop
                    await agent_loop(user_input, self.vision, self.planner, self.executor, self.verifier, self.element_cache)

            except KeyboardInterrupt:
                console.print("\n[bold red]Interrupted. Exiting...[/bold red]")
                break
            except Exception as e:
                console.print(f"[bold red]CLI Error: {e}[/bold red]")

    async def _get_voice_input(self) -> str:
        console.print("[dim]🎙 Listening... (Press Ctrl+C to stop or wait for silence)[/dim]")
        audio_path = self.mic.record_until_keypress()
        if not audio_path: return ""
        console.print("[dim]Transcribing...[/dim]")
        stt_res = await asyncio.to_thread(self.stt.transcribe_audio, audio_path)
        return stt_res.get("transcript", "")

    async def _handle_chat(self, query: str):
        console.print("[dim]🧠 Thinking...[/dim]")
        
        # Decide if we need visual context (reuse logic from AgentLoop)
        ui_state_str = "No visual context provided."
        keywords = ["screen", "see", "visible", "look", "page", "app", "window", "tab", "display", "what is on", "read"]
        if any(k in query.lower() for k in keywords):
            ui_state = await self.vision.capture_and_parse()
            elements = ui_state.get("elements", [])
            condensed = [f"[{e.get('type')}] '{e.get('text')}'" for e in elements if e.get('text')]
            ui_state_str = "\n".join(condensed[:20])

        # Load screen analysis prompt
        prompt_path = os.path.join(RuntimeConfig.BASE_DIR, "prompts", "screen_analysis.txt")
        with open(prompt_path, "r") as f:
            template = f.read()
        
        prompt = template.replace("{query}", query).replace("{ui_state}", ui_state_str)
        response_text = await self.llm.generate_response(prompt)
        
        console.print(Panel(response_text, title="[bold magenta]Agent[/bold magenta]"))
        
        # TTS
        audio_path = await asyncio.to_thread(self.tts.generate_audio, response_text)
        if audio_path:
            asyncio.create_task(self.audio.play_audio_async(audio_path))

if __name__ == "__main__":
    cli = AgentCLI()
    asyncio.run(cli.run())
