import asyncio
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from runtime_agent.services.vision_client import VisionClient
from runtime_agent.services.llm_service import ConversationalLLMService
from runtime_agent.services.tts_service import TTSService
from runtime_agent.services.audio_service import AudioService
from runtime_agent.config import Config

console = Console()

from runtime_agent.services.microphone_service import MicrophoneService
from planner_service.services.voice_service import VoiceService

class AgentLoop:
    def __init__(self):
        self.vision = VisionClient()
        self.llm = ConversationalLLMService()
        self.tts = TTSService()
        self.audio = AudioService()
        self.mic = MicrophoneService()
        self.stt = VoiceService()
        
        # Load prompt template
        prompt_path = os.path.join(Config.BASE_DIR, "prompts", "screen_analysis.txt")
        with open(prompt_path, "r") as f:
            self.screen_prompt_template = f.read()

    def _needs_screen_context(self, query: str) -> bool:
        """Heuristic to decide if we should trigger a screenshot."""
        keywords = ["screen", "see", "visible", "look", "page", "app", "window", "tab", "display", "what is on", "read"]
        return any(k in query.lower() for k in keywords)

    async def run_interactive(self):
        while True:
            try:
                # 1. Get input (Text or Voice)
                choice = Prompt.ask("\n[bold cyan]Type your query, or type 'v' for Voice Input[/bold cyan]")
                
                if choice.lower() in ["exit", "quit"]:
                    console.print("[bold red]Exiting runtime...[/bold red]")
                    break
                    
                # Interrupt any playing audio
                self.audio.stop_audio()
                
                if choice.lower() == 'v':
                    audio_path = self.mic.record_until_keypress()
                    if not audio_path: continue
                    console.print("[dim]Transcribing...[/dim]")
                    # STT conversion is blocking, run in thread
                    stt_res = await asyncio.to_thread(self.stt.transcribe_audio, audio_path)
                    query = stt_res["transcript"]
                    console.print(f"[bold green]You said:[/bold green] {query}")
                else:
                    query = choice
                
                # 2. Check if screen context is needed
                ui_state_str = "No visual context provided."
                if self._needs_screen_context(query):
                    ui_state = await self.vision.capture_and_parse()
                    
                    # Condense for the LLM
                    elements = ui_state.get("elements", [])
                    condensed = [f"[{e.get('type')}] '{e.get('text')}'" for e in elements if e.get('text')]
                    ui_state_str = "\n".join(condensed[:20]) # Limit to top 20 elements to save tokens
                    
                # 3. Build Prompt & Call LLM
                prompt = self.screen_prompt_template.replace("{query}", query).replace("{ui_state}", ui_state_str)
                
                console.print("[dim]Thinking...[/dim]")
                response_text = await self.llm.generate_response(prompt)
                
                # 4. Display output
                console.print(Panel(response_text, title="[bold magenta]Agent Reasoning[/bold magenta]"))
                
                # 5. Generate and play TTS audio
                console.print("[dim]Generating Speech...[/dim]")
                
                # Run TTS generation in thread to not block async loop (say command is blocking)
                audio_path = await asyncio.to_thread(self.tts.generate_audio, response_text)
                
                if audio_path:
                    # Play asynchronously
                    asyncio.create_task(self.audio.play_audio_async(audio_path))
                    
            except KeyboardInterrupt:
                console.print("\n[bold red]Interrupted. Exiting...[/bold red]")
                break
            except Exception as e:
                console.print(f"[bold red]Error in loop: {e}[/bold red]")
