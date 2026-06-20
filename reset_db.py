import asyncio
from backend.database.connection import init_db, async_engine
from backend.database.models import Base

async def reset():
    print("Dropping all tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Recreating all tables...")
    await init_db()
    print("Database reset complete.")

asyncio.run(reset())
