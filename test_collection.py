import asyncio
from backend.database.connection import async_session_factory
from backend.database.repository import StudentRepository
from backend.collection.service import PlatformSyncService

async def main():
    async with async_session_factory() as session:
        repo = StudentRepository(session)
        records = await repo.get_all_profiles()
        if not records:
            print("No students found.")
            return
        
        # Take the first student with some platform username
        for r in records:
            if r.personal_info.leetcode_username or r.personal_info.github_url or r.personal_info.codeforces_username or r.personal_info.codechef_username:
                print(f"Testing collection for {r.personal_info.name} - UUID: {r.student_uuid}")
                profile = await PlatformSyncService.sync_platforms(session, r.student_uuid)
                
                from backend.api.main import attach_ranking
                from backend.ingestion.models.student_profile import StudentProfile
                
                sp = StudentProfile.model_validate(profile.profile_data)
                try:
                    attach_ranking(sp)
                    print("Ranking attached successfully.")
                    print("Ranking:", sp.ranking)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                
                break

if __name__ == "__main__":
    asyncio.run(main())
