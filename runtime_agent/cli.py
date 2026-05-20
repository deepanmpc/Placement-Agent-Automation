import typer
import asyncio
from rich.console import Console
from rich.panel import Panel
from runtime_agent.graph import AgentOrchestrator

app = typer.Typer()
console = Console()

@app.command()
def interact():
    """Starts the interactive CLI loop for the autonomous agent."""
    console.print(Panel.fit("[bold green]Agent Runtime Started[/bold green]\nType your command or 'exit' to quit.", title="System"))
    
    agent = AgentOrchestrator()
    asyncio.run(agent.run_interactive())

if __name__ == "__main__":
    app()
