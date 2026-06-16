import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine("mysql+aiomysql://root:15713007@localhost:3306/placement_agent")
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE scoring_rules;"))
        print("Truncated scoring_rules")

asyncio.run(main())
