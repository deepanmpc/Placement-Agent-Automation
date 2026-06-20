import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from backend.config import Settings
from backend.database.models import StudentProfileRecord
from backend.ingestion.models.student_profile import StudentProfile

async def main():
    settings = Settings()
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(StudentProfileRecord))
        records = result.scalars().all()
        for r in records:
            p = StudentProfile.model_validate(r.profile_data)
            print(f"Candidate: {p.personal_info.name}")
            print(f"  Skills: {p.skills.all_skills if p.skills else 'None'}")
            if p.projects:
                for proj in p.projects:
                    print(f"  Project: {proj.title} - Tech: {proj.technologies}")
            else:
                print("  Projects: None")

asyncio.run(main())
