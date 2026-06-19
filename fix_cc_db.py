import asyncio
import json
import aiomysql
from backend.collection.collectors import CodeChefCollector
from backend.config import Settings

async def update_all_highest_ratings():
    settings = Settings()
    pool = await aiomysql.create_pool(
        host="127.0.0.1", port=3306, user="root", password="15713007", db="placement_agent", autocommit=True
    )
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, codechef_username, codechef_profile FROM student_profiles WHERE codechef_username IS NOT NULL;")
            rows = await cur.fetchall()
            
            for row in rows:
                sid, uname, profile_json = row
                if not uname: continue
                
                # Rescrape the profile using the fixed collector
                print(f"Scraping {uname}...")
                new_data = await CodeChefCollector.collect(uname)
                if not new_data: continue
                
                # Parse existing profile
                try:
                    prof = json.loads(profile_json) if isinstance(profile_json, str) else profile_json
                except:
                    prof = {}
                
                # Update highest rating
                if prof.get("highest_rating") != new_data.highest_rating:
                    print(f"Updating {uname} highest_rating: {prof.get('highest_rating')} -> {new_data.highest_rating}")
                    prof["highest_rating"] = new_data.highest_rating
                    
                    # Also update profile_data -> codechef
                    await cur.execute("SELECT profile_data FROM student_profiles WHERE id = %s", (sid,))
                    master_row = await cur.fetchone()
                    try:
                        master_prof = json.loads(master_row[0]) if isinstance(master_row[0], str) else master_row[0]
                        if "codechef" in master_prof:
                            master_prof["codechef"]["highest_rating"] = new_data.highest_rating
                    except:
                        master_prof = master_row[0]

                    await cur.execute(
                        "UPDATE student_profiles SET codechef_profile = %s, profile_data = %s WHERE id = %s",
                        (json.dumps(prof), json.dumps(master_prof), sid)
                    )
                else:
                    print(f"{uname} highest_rating is already correct ({new_data.highest_rating})")
                    
    pool.close()
    await pool.wait_closed()

asyncio.run(update_all_highest_ratings())
