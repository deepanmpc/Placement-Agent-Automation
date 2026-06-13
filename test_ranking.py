import asyncio
import os
import sys

from backend.database.connection import AsyncSessionLocal
from backend.ingestion.service import IngestionService
from backend.config import Settings
from backend.api.main import attach_ranking

async def main():
    async with AsyncSessionLocal() as db:
        settings = Settings()
        service = IngestionService(db_session=db, settings=settings)
        profiles = await service.get_all_profiles(limit=1)
        if profiles:
            p = profiles[0]
            try:
                attach_ranking(p)
                print("Ranking successful!")
            except Exception as e:
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
