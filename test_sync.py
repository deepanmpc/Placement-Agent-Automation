import asyncio
from backend.database.connection import async_session_factory
from backend.collection.service import PlatformSyncService
from sqlalchemy.future import select
from backend.database.models import StudentProfileRecord, ExtractionJob

async def test():
    async with async_session_factory() as db:
        uuids = (await db.execute(select(StudentProfileRecord.student_uuid).limit(2))).scalars().all()
        if not uuids:
            return
        
        job = ExtractionJob(
            status="IN_PROGRESS",
            total_count=len(uuids),
            completed_count=0,
            target_uuids={"uuids": list(uuids)},
            completed_uuids={"uuids": []}
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        job_id = job.id
        
    print("Job ID:", job_id)
    
    async with async_session_factory() as db:
        result = await db.execute(select(ExtractionJob).where(ExtractionJob.id == job_id))
        job = result.scalars().first()
        target_uuids = job.target_uuids.get("uuids", [])
        completed_uuids = job.completed_uuids.get("uuids", [])
        remaining_uuids = [u for u in target_uuids if u not in completed_uuids]
        
        for uuid in remaining_uuids:
            print("Processing", uuid)
            job_refresh = await db.execute(select(ExtractionJob).where(ExtractionJob.id == job_id))
            job_current = job_refresh.scalars().first()
            
            try:
                await PlatformSyncService.sync_platforms(db, uuid)
            except Exception as e:
                print(f"Error syncing {uuid}: {e}")
                
            completed_uuids.append(uuid)
            job_current.completed_uuids = {"uuids": completed_uuids}
            job_current.completed_count = len(completed_uuids)
            if job_current.completed_count >= job_current.total_count:
                job_current.status = "COMPLETED"
            
            await db.commit()
            print("Committed", uuid)

if __name__ == '__main__':
    asyncio.run(test())
