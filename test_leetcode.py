import asyncio
from backend.ingestion.leetcode_collector.collector import LeetCodeCollector

async def main():
    collector = LeetCodeCollector()
    profile = await collector.collect("neal_wu")
    print(f"Rating: {profile.rating}")
    print(f"Contests: {profile.contests_participated}")

asyncio.run(main())
