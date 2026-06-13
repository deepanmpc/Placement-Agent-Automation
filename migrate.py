import sqlite3
import pymysql
import json
import uuid
from datetime import datetime

# MySQL config
mysql_config = {
    'user': 'root',
    'password': '15713007',
    'host': '127.0.0.1',
    'database': 'placement_agent'
}

def migrate():
    # Connect to MySQL
    print("Connecting to MySQL...")
    try:
        myconn = pymysql.connect(**mysql_config)
        mycursor = myconn.cursor()
    except Exception as e:
        print(f"Failed to connect to MySQL: {e}")
        return

    # Connect to SQLite
    print("Connecting to SQLite...")
    try:
        sqlconn = sqlite3.connect('placement_agent.db')
        sqlconn.row_factory = sqlite3.Row
        sqlcursor = sqlconn.cursor()
    except Exception as e:
        print(f"Failed to connect to SQLite: {e}")
        return

    sqlcursor.execute("SELECT * FROM student_profiles")
    rows = sqlcursor.fetchall()
    
    print(f"Found {len(rows)} records in SQLite.")

    for row in rows:
        student_uuid = row['student_uuid']
        profile_data = json.loads(row['profile_data']) if row['profile_data'] else {}
        
        # 1. Insert into students
        # extract personal info
        personal = profile_data.get('personal', {})
        education = profile_data.get('education', {})
        
        name = personal.get('name')
        email = personal.get('email')
        if not email:
            email = f"{student_uuid}@placeholder.com"
            
        phone = personal.get('phone')
        github_username = personal.get('github_url', '').split('/')[-1] if personal.get('github_url') else None
        leetcode_username = personal.get('leetcode_username')
        codeforces_username = personal.get('codeforces_username')
        codechef_username = personal.get('codechef_username')
        portfolio_url = personal.get('portfolio_url')
        
        degree = education.get('degree')
        branch = education.get('branch')
        cgpa = education.get('cgpa')
        graduation_year = education.get('graduation_year')

        mycursor.execute("SELECT id FROM students WHERE email = %s", (email,))
        student_id_row = mycursor.fetchone()
        
        if student_id_row:
            student_id = student_id_row[0]
            print(f"Student {email} already exists, ID: {student_id}")
        else:
            insert_student_query = """
            INSERT INTO students (student_uuid, name, email, phone, degree, branch, cgpa, graduation_year, 
                                  github_username, leetcode_username, codeforces_username, codechef_username, portfolio_url, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            mycursor.execute(insert_student_query, (
                student_uuid, name, email, phone, degree, branch, cgpa, graduation_year,
                github_username, leetcode_username, codeforces_username, codechef_username, portfolio_url
            ))
            student_id = mycursor.lastrowid
        
        # 2. Insert Resume Data
        skills = profile_data.get('skills', {})
        projects = profile_data.get('projects', [])
        
        mycursor.execute("SELECT id FROM resume_data WHERE student_id = %s", (student_id,))
        if not mycursor.fetchone():
            insert_resume = """
            INSERT INTO resume_data (student_id, skills_json, projects_json, created_at)
            VALUES (%s, %s, %s, NOW())
            """
            mycursor.execute(insert_resume, (
                student_id, 
                json.dumps(skills),
                json.dumps(projects)
            ))
        
        # 3. Insert GitHub Snapshot
        github_profile = json.loads(row['github_profile']) if row['github_profile'] else {}
        if github_profile:
            public_repos = github_profile.get('public_repos', 0)
            stars = github_profile.get('total_stars', 0)
            followers = github_profile.get('followers', 0)
            following = github_profile.get('following', 0)
            languages = github_profile.get('languages', [])
            
            mycursor.execute("SELECT id FROM github_snapshots WHERE student_id = %s AND snapshot_date = CURDATE()", (student_id,))
            if not mycursor.fetchone():
                mycursor.execute("""
                INSERT INTO github_snapshots (student_id, snapshot_date, public_repos, stars, followers, following, language_distribution_json, created_at, updated_at)
                VALUES (%s, CURDATE(), %s, %s, %s, %s, %s, NOW(), NOW())
                """, (student_id, public_repos, stars, followers, following, json.dumps(languages)))
                
        # 4. Insert LeetCode Snapshot
        leetcode_profile = json.loads(row['leetcode_profile']) if row['leetcode_profile'] else {}
        if leetcode_profile:
            total_solved = leetcode_profile.get('total_solved', 0)
            easy_solved = leetcode_profile.get('easy_solved', 0)
            medium_solved = leetcode_profile.get('medium_solved', 0)
            hard_solved = leetcode_profile.get('hard_solved', 0)
            ranking = leetcode_profile.get('ranking', 0)
            rating = leetcode_profile.get('recent_contest_rating', 0.0)
            contests = leetcode_profile.get('contests_participated', 0)
            
            mycursor.execute("SELECT id FROM leetcode_snapshots WHERE student_id = %s AND snapshot_date = CURDATE()", (student_id,))
            if not mycursor.fetchone():
                mycursor.execute("""
                INSERT INTO leetcode_snapshots (student_id, snapshot_date, total_solved, easy_solved, medium_solved, hard_solved, ranking, rating, contests_participated, created_at, updated_at)
                VALUES (%s, CURDATE(), %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (student_id, total_solved, easy_solved, medium_solved, hard_solved, ranking, rating, contests))

        # 5. Insert Codeforces Snapshot
        cf_profile = json.loads(row['codeforces_profile']) if row['codeforces_profile'] else {}
        if cf_profile:
            rating = cf_profile.get('rating', 0)
            max_rating = cf_profile.get('maxRating', 0)
            rank = cf_profile.get('rank', '')
            solved = cf_profile.get('total_problems_solved', 0)
            contests = cf_profile.get('contests_participated', 0)
            
            mycursor.execute("SELECT id FROM codeforces_snapshots WHERE student_id = %s AND snapshot_date = CURDATE()", (student_id,))
            if not mycursor.fetchone():
                mycursor.execute("""
                INSERT INTO codeforces_snapshots (student_id, snapshot_date, rating, max_rating, rank_name, solved_count, contests, created_at, updated_at)
                VALUES (%s, CURDATE(), %s, %s, %s, %s, %s, NOW(), NOW())
                """, (student_id, rating, max_rating, rank, solved, contests))
                
        # 6. Insert CodeChef Snapshot
        cc_profile = json.loads(row['codechef_profile']) if row['codechef_profile'] else {}
        if cc_profile:
            rating = cc_profile.get('currentRating', 0)
            highest_rating = cc_profile.get('highestRating', 0)
            stars = cc_profile.get('stars', '1★')
            solved = cc_profile.get('totalProblemsSolved', 0)
            contests = cc_profile.get('contestsParticipated', 0)
            
            mycursor.execute("SELECT id FROM codechef_snapshots WHERE student_id = %s AND snapshot_date = CURDATE()", (student_id,))
            if not mycursor.fetchone():
                mycursor.execute("""
                INSERT INTO codechef_snapshots (student_id, snapshot_date, rating, highest_rating, stars, solved_count, contests, created_at, updated_at)
                VALUES (%s, CURDATE(), %s, %s, %s, %s, %s, NOW(), NOW())
                """, (student_id, rating, highest_rating, stars, solved, contests))

    myconn.commit()
    print("Migration complete!")
    mycursor.close()
    myconn.close()
    sqlconn.close()

if __name__ == '__main__':
    migrate()
