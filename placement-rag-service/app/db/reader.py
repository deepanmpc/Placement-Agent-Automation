from typing import AsyncGenerator, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Integer, String, JSON, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config.settings import settings

async_engine = create_async_engine(settings.database_url, echo=False)
async_session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

class StudentProfileRecord(Base):
    __tablename__ = "student_profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    profile_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    # Ignoring other columns as we just need profile_data for RAG

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_profile(student_uuid: str) -> Optional[dict]:
    async with async_session_factory() as session:
        stmt = select(StudentProfileRecord.profile_data).where(StudentProfileRecord.student_uuid == student_uuid)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

async def get_all_profile_uuids() -> List[str]:
    async with async_session_factory() as session:
        stmt = select(StudentProfileRecord.student_uuid)
        result = await session.execute(stmt)
        return list(result.scalars().all())

async def get_all_profiles(limit: int = 100, offset: int = 0) -> List[dict]:
    async with async_session_factory() as session:
        stmt = select(StudentProfileRecord).limit(limit).offset(offset)
        result = await session.execute(stmt)
        records = result.scalars().all()
        return [{"student_uuid": r.student_uuid, "profile_data": r.profile_data} for r in records]
