#!/usr/bin/env python3
"""
EDITH-style HUD Interface
Cyberpunk/Terminal aesthetic with red & blue theme
"""
import os
import sys
import asyncio
import time
from datetime import datetime
from typing import Optional

os.environ['PYTHONPATH'] = '.'

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.table import Table

console = Console()

# Color palette
RED = "#FF0040"
BLUE = "#00D4FF"
DARK_RED = "#1a000d"
DARK_BLUE = "#001a1a"
WHITE = "#FFFFFF"
CYAN = "#00FFFF"
GREEN = "#00FF00"
YELLOW = "#FFFF00"

# Styles
EDITH_RED = Style(color=RED, bold=True)
EDITH_BLUE = Style(color=BLUE, bold=True)
EDITH_CYAN = Style(color=CYAN, bold=True)
EDITH_GREEN = Style(color=GREEN)
EDITH_DIM = Style(color="#666666")
EDITH_WHITE = Style(color=WHITE)

MODE_COLORS = {
    "CHAT": EDITH_BLUE,
    "AUTO": EDITH_RED,
    "VOICE": EDITH_GREEN,
    "IDLE": EDITH_DIM,
}


class EDITHHUD:
    def __init__(self):
        self.mode = "IDLE"
        self.running = True
        self.history = []
        self.status = "STANDBY"
        self.scanlines = 100
        self.vision = None
        self.llm = None
        self.tts = None
        
    def init_services(self):
        """Initialize backend services"""
        try:
            from runtime_agent.services.vision_client import VisionClient
            from runtime_agent.services.llm_service import ConversationalLLMService
            from runtime_agent.services.tts_service import TTSService
            
            self.vision = VisionClient()
            self.llm = ConversationalLLMService()
            self.tts = TTSService()
            self.status = "ONLINE"
            return True
        except Exception as e:
            console.print(f"[red]Service init failed: {e}[/]")
            return False
    
    def draw_header(self) -> Panel:
        """Draw EDITH-style header"""
        title = Text()
        title.append("╔═", style=EDITH_RED)
        title.append("─"*30, style=EDITH_DIM)
        title.append("═╗", style=EDITH_RED)
        title.append("\n║ ", style=EDITH_RED)
        
        # Animated E.D.I.T.H
        edith_name = "E.D.I.T.H"
        for i, c in enumerate(edith_name):
            if c == ".":
                title.append(".", style=EDITH_DIM)
            elif i % 2 == 0:
                title.append(f"{c}", style=EDITH_RED)
            else:
                title.append(f"{c}", style=EDITH_BLUE)
        
        title.append(" A.I. ", style=EDITH_CYAN)
        title.append(" "*12, style=EDITH_DIM)
        
        time_str = datetime.now().strftime("%H:%M:%S")
        title.append(f"║ [{time_str}]", style=EDITH_DIM)
        title.append("\n╚", style=EDITH_RED)
        title.append("─"*31, style=EDITH_DIM)
        title.append("═╝", style=EDITH_RED)
        
        return Panel(
            title,
            style=Style(bgcolor=DARK_RED),
            padding=(0, 0),
            border_style=RED,
        )
    
    def draw_status_bar(self) -> Table:
        """Draw status indicators"""
        table = Table(box=None, show_header=False, padding=(0, 1))
        table.add_column("key", style=EDITH_DIM)
        table.add_column("value", style=EDITH_GREEN)
        
        mode_style = MODE_COLORS.get(self.mode, EDITH_CYAN)
        
        # Status indicators
        status_icons = {
            "IDLE": "○",
            "CHAT": "◉",
            "AUTO": "◈",
            "VOICE": "◐",
            "PROCESSING": "◑",
        }
        
        table.add_row(f"[{RED}]◆[/{RED}] MODE", f"[{self.mode}]", style=mode_style)
        table.add_row(f"[{BLUE}]◆[/{BLUE}] STATUS", f"[{self.status}]", style=EDITH_CYAN)
        table.add_row(f"[{GREEN}]◆[/{GREEN}] SCAN", f"[{self.scanlines}%]", style=EDITH_DIM)
        
        return table
    
    def draw_mode_selector(self) -> Panel:
        """Draw mode selection bar"""
        menu = Text()
        
        modes = [
            ("IDLE", "Standby"),
            ("CHAT", "Chat Mode"),
            ("AUTO", "Auto Mode"), 
            ("VOICE", "Voice"),
            ("EXIT", "Exit"),
        ]
        
        for mode_name, desc in modes:
            if mode_name == "EXIT":
                menu.append(" │ ", style=EDITH_DIM)
            
            if mode_name == self.mode:
                menu.append(f"[{RED}]▸ {mode_name}[/{RED}]", style=EDITH_RED)
            else:
                menu.append(f"  {mode_name}  ", style=EDITH_DIM)
            
            if mode_name != "EXIT":
                menu.append(" │ ", style=EDITH_DIM)
        
        return Panel(
            menu,
            style=Style(bgcolor=DARK_BLUE),
            padding=(0, 1),
            border_style=BLUE,
        )
    
    def draw_history(self) -> Optional[Panel]:
        """Draw recent history"""
        if not self.history:
            return None
        
        items = []
        for h in self.history[-4:]:
            ts, mode, msg = h.get("time", ""), h.get("mode", "IDLE"), h.get("msg", "")[:40]
            items.append(f"[{BLUE}]{ts}[/] [{mode}] {msg}")
        
        return Panel(
            "\n".join(items),
            title=f"[{CYAN}]◈ RECENT ACTIVITY[/{CYAN}]",
            border_style=BLUE,
            style=Style(bgcolor=DARK_BLUE),
        )
    
    def render_welcome(self):
        """Initial welcome screen"""
        console.clear()
        
        # ASCII Art
        art = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   █████╗  ██████╗ ██████╗  █████╗ ████████╗███████╗██╗     ███████╗███████╗ ║
║  ██╔══██╗██╔════╝ ██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ║
║  ███████║██║  ███╗██████╔╝███████║   ██║   █████╗  ██║     █████╗  ███████╗ ║
║  ██╔══██║██║   ██║██╔══██╗██╔══██║   ██║   ██╔══╝  ██║     ██╔══╝  ╚════██║ ║
║  ██║  ██║╚██████╔╝██║  ██║██║  ██║   ██║   ███████╗███████╗███████╗███████║ ║
║  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝ ║
║                                                                           ║
║                    ██████╗ ███████╗ █████╗ ████████╗                    ║
║                    ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝                    ║
║                    ██████╔╝█████╗  ███████║   ██║                       ║
║                    ██╔══██╗██╔══╝  ██╔══██║   ██║                       ║
║                    ██║  ██║███████╗██║  ██║   ██║                       ║
║                    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝                       ║
║                     A U T O N O M O U S   A G E N T                    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
        console.print(art, style=EDITH_DIM, justify="center")
        
        console.print()
        
        # Loading animation
        with console.status("[bold cyan]Initializing EDITH Core...") as status:
            time.sleep(0.3)
            status.update("[bold blue]Loading Vision Service...")
            time.sleep(0.2)
            status.update("[bold red]Loading NLP Engine...")
            time.sleep(0.2)
            status.update("[bold cyan]Loading Executor...")
            time.sleep(0.2)
            status.update("[bold green]EDITH ONLINE")
            time.sleep(0.1)
        
        console.print()
        console.print(Panel(
            Text("Type a command or select a mode below", style=EDITH_CYAN),
            border_style=BLUE,
            style=Style(bgcolor=DARK_BLUE),
        ))
        time.sleep(1)
    
    def render_main(self):
        """Main HUD render"""
        console.clear()
        
        # Header
        console.print(self.draw_header())
        console.print()
        
        # Status
        console.print(self.draw_status_bar())
        console.print()
        
        # History
        history_panel = self.draw_history()
        if history_panel:
            console.print(history_panel)
            console.print()
        
        # Mode selector
        console.print(self.draw_mode_selector())
    
    def process_chat(self, user_input: str) -> str:
        """Process chat mode input"""
        self.status = "THINKING"
        
        try:
            # Simple response for now
            response = f"Processing: {user_input}\n\n(This will connect to LLM service)"
        except Exception as e:
            response = f"Error: {e}"
        
        self.status = "ONLINE"
        return response
    
    def process_auto(self, goal: str) -> str:
        """Process auto mode - run autonomous agent"""
        self.status = "EXECUTING"
        
        try:
            # Would run autonomous agent here
            response = f"Executing goal: {goal}\n\n(Autonomous mode - would run executor)"
        except Exception as e:
            response = f"Error: {e}"
        
        self.status = "ONLINE"
        return response
    
    def switch_mode(self, new_mode: str):
        """Switch between modes"""
        self.mode = new_mode
        
        if new_mode == "EXIT":
            self.running = False
            return
        
        console.print(f"\n[{BLUE}]▶ Switching to {new_mode} mode[/{BLUE}]")
    
    def shutdown(self):
        """Shutdown animation"""
        console.print()
        console.print(Panel(
            Text("EDITH SHUTDOWN SEQUENCE INITIATED...", style=EDITH_RED),
            border_style=RED,
        ))
        time.sleep(0.5)


async def main():
    """Main EDITH loop"""
    edith = EDITHHUD()
    edith.render_welcome()
    
    while edith.running:
        edith.render_main()
        
        # Mode selector
        console.print()
        modes = {
            "IDLE": "i",
            "CHAT": "c", 
            "AUTO": "a",
            "VOICE": "v",
            "EXIT": "e"
        }
        
        mode_input = console.input(f"\n[{RED}]Select[{BLUE}]:[{RED}] [IDLE/C/A/V/E][/{RED}] ").strip().lower()
        
        if mode_input in ["idle", "i"]:
            edith.switch_mode("IDLE")
        elif mode_input in ["chat", "c"]:
            edith.switch_mode("CHAT")
        elif mode_input in ["auto", "a", "autonomous"]:
            edith.switch_mode("AUTO")
        elif mode_input in ["voice", "v"]:
            edith.switch_mode("VOICE")
        elif mode_input in ["exit", "e", "quit"]:
            edith.switch_mode("EXIT")
        else:
            # Treat as input for current mode
            if edith.mode == "CHAT":
                response = edith.process_chat(mode_input)
                console.print(Panel(response, border_style=BLUE))
                edith.history.append({
                    "time": datetime.now().strftime("%H:%M"),
                    "mode": "CHAT",
                    "msg": mode_input[:30]
                })
            elif edith.mode == "AUTO":
                response = edith.process_auto(mode_input)
                console.print(Panel(response, border_style=RED))
                edith.history.append({
                    "time": datetime.now().strftime("%H:%M"),
                    "mode": "AUTO", 
                    "msg": mode_input[:30]
                })
            elif edith.mode == "VOICE":
                console.print(f"[{GREEN}]🎤 Voice recognition would activate[/]")
                edith.switch_mode("IDLE")
    
    return 0


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n[bold red] EDITH powering down...[/]")
    sys.exit(0)