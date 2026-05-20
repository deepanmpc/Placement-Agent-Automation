import asyncio
import os
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from runtime_agent.config import Config
from runtime_agent.services.vision_client import VisionClient
from runtime_agent.services.llm_service import ConversationalLLMService
from runtime_agent.services.tts_service import TTSService
from runtime_agent.services.audio_service import AudioService
from runtime_agent.services.microphone_service import MicrophoneService
from planner_service.services.voice_service import VoiceService

console = Console()

class AgentState(TypedDict, total=False):
    user_input: str
    is_voice: bool
    vision_context: str
    llm_response: str
    tts_audio_path: str
    end_loop: bool

class AgentOrchestrator:
    def __init__(self):
        self.vision = VisionClient()
        self.llm = ConversationalLLMService()
        self.tts = TTSService()
        self.audio = AudioService()
        self.mic = MicrophoneService()
        self.stt = VoiceService()
        
        prompt_path = os.path.join(Config.BASE_DIR, "prompts", "screen_analysis.txt")
        with open(prompt_path, "r") as f:
            self.screen_prompt_template = f.read()

        # Compile LangGraph
        builder = StateGraph(AgentState)
        
        builder.add_node("listen", self.node_listen)
        builder.add_node("perceive", self.node_perceive)
        builder.add_node("reason", self.node_reason)
        builder.add_node("speak", self.node_speak)
        
        builder.add_edge(START, "listen")
        builder.add_conditional_edges("listen", self.route_from_listen)
        builder.add_edge("perceive", "reason")
        builder.add_edge("reason", "speak")
        builder.add_edge("speak", "listen")
        
        self.graph = builder.compile()

    def route_from_listen(self, state: AgentState) -> str:
        if state.get("end_loop"):
            return END
        if not state.get("user_input"):
            return "listen" # Try again if input was empty
        return "perceive"

    async def node_listen(self, state: AgentState) -> AgentState:
        self.audio.stop_audio()
        choice = Prompt.ask("\n[bold cyan]Type your query, or type 'v' for Voice Input[/bold cyan]")
        
        if choice.lower() in ["exit", "quit"]:
            console.print("[bold red]Exiting runtime...[/bold red]")
            return {"end_loop": True, "user_input": ""}
            
        if choice.lower() == 'v':
            audio_path = self.mic.record_until_keypress()
            if not audio_path:
                return {"user_input": "", "is_voice": True}
                
            console.print("[dim]Transcribing...[/dim]")
            stt_res = await asyncio.to_thread(self.stt.transcribe_audio, audio_path)
            query = stt_res["transcript"]
            console.print(f"[bold green]You said:[/bold green] {query}")
            return {"user_input": query, "is_voice": True}
            
        return {"user_input": choice, "is_voice": False}

    async def node_perceive(self, state: AgentState) -> AgentState:
        query = state.get("user_input", "")
        keywords = ["screen", "see", "visible", "look", "page", "app", "window", "tab", "display", "what is on", "read"]
        needs_context = any(k in query.lower() for k in keywords)
        
        if needs_context:
            console.print("[bold yellow][Vision][/bold yellow] Capturing active window...")
            vision_res = await self.vision.capture_and_parse()
            elements = vision_res.get("elements", [])
            console.print(f"[bold yellow][Vision][/bold yellow] Detected {len(elements)} UI elements.")
            
            ui_state_str = "\n".join([str(el) for el in elements])
            if not ui_state_str:
                ui_state_str = "No specific UI elements were detected, or the screen is blank."
            return {"vision_context": ui_state_str}
        
        return {"vision_context": "No visual context provided."}

    async def node_reason(self, state: AgentState) -> AgentState:
        query = state.get("user_input", "")
        ui_state_str = state.get("vision_context", "")
        
        console.print("[dim]Thinking...[/dim]")
        prompt = self.screen_prompt_template.replace("{{query}}", query).replace("{{ui_state}}", ui_state_str)
        
        response = await self.llm.generate_response(prompt)
        console.print(Panel(response, title="Agent Reasoning", border_style="green"))
        
        return {"llm_response": response}

    async def node_speak(self, state: AgentState) -> AgentState:
        text = state.get("llm_response", "")
        if not text:
            return {"tts_audio_path": ""}
            
        console.print("[dim]Generating Speech...[/dim]")
        audio_path = await asyncio.to_thread(self.tts.generate_audio, text)
        if audio_path:
            await self.audio.play_audio_async(audio_path)
            
        return {"tts_audio_path": audio_path}

    async def run_interactive(self):
        console.print(f"╭{'─'*39}╮")
        console.print(f"│ [bold magenta]LangGraph Orchestrator Started[/bold magenta]      │")
        console.print(f"│ Type your command or 'exit' to quit. │")
        console.print(f"╰{'─'*39}╯")
        
        initial_state = AgentState(
            user_input="", 
            is_voice=False, 
            vision_context="", 
            llm_response="", 
            tts_audio_path="", 
            end_loop=False
        )
        
        try:
            # stream_mode="updates" yields {node_name: StateUpdateDict}
            async for s in self.graph.astream(initial_state, config={"recursion_limit": 1000}):
                for node_name, state_update in s.items():
                    if state_update.get("end_loop"):
                        return
        except KeyboardInterrupt:
            console.print("\n[bold red]Interrupted. Exiting...[/bold red]")
