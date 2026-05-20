import asyncio
from runtime_agent.config import Config
from runtime_agent.graph import AgentOrchestrator

def main():
    Config.setup_dirs()
    agent = AgentOrchestrator()
    try:
        asyncio.run(agent.run_interactive())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
