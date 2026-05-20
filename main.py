import asyncio

from executor_service.main import main as run_autonomous_agent


if __name__ == "__main__":
    asyncio.run(run_autonomous_agent())
