import asyncio
from backend.collection.collectors import CodeChefCollector

async def main():
    profile = await CodeChefCollector.collect('klu2300032731')
    print(profile)

asyncio.run(main())
