import urllib.request
import json

try:
    # Get all profiles
    url = "http://localhost:8000/profiles?job_description=ESP32"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        profiles = json.loads(response.read().decode())
    
    if not profiles:
        print("No profiles found")
    else:
        p = profiles[0]
        uuid = p['student_uuid']
        print(f"List API Fitment Score: {p.get('ranking', {}).get('fitment_score')}")
        
        # Get single profile
        url_single = f"http://localhost:8000/profiles/{uuid}?job_description=ESP32"
        req_single = urllib.request.Request(url_single)
        with urllib.request.urlopen(req_single) as response_single:
            single_p = json.loads(response_single.read().decode())
        
        print(f"Single API Fitment Score: {single_p.get('ranking', {}).get('fitment_score')}")
except Exception as e:
    print("Error:", e)
