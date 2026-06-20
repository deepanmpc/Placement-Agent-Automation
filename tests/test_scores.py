import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from backend.config import Settings
from backend.database.models import StudentProfileRecord
from backend.ingestion.models.student_profile import StudentProfile
from backend.ranking.weighted_ranker.semantic_ranker import SemanticRanker
from backend.ranking.weighted_ranker.rule_score import RuleScoreAggregator, ExplainableScore

async def main():
    settings = Settings()
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    jd = "robotics and esp32"
    
    async with async_session() as session:
        result = await session.execute(select(StudentProfileRecord))
        records = result.scalars().all()
        for r in records:
            p = StudentProfile.model_validate(r.profile_data)
            
            # mock platform and behavioral scores just to test semantic
            sem = SemanticRanker.calculate_fitment(p, jd)
            print(f"Candidate: {p.personal_info.name} -> Semantic: {sem.total_score}")

asyncio.run(main())
