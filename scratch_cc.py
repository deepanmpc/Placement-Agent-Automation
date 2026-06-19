import asyncio
import sys
from backend.collection.collectors import CodeChefCollector

async def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "deepan_07"
    res = await CodeChefCollector.collect(username)
    print(res)

asyncio.run(main())
