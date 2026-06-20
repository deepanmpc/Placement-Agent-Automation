import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        with open('/Users/deepandee/Downloads/2300032731_DEEPAN_CHANDRASEKARAN.pdf', 'rb') as f:
            files = {'file': ('resume_latest2.pdf', f, 'application/pdf')}
            response = await client.post('http://localhost:8000/ingest', files=files)
            print("Status:", response.status_code)
            data = response.json()
            if 'projects' in data:
                print("Extracted", len(data['projects']), "projects:")
                for p in data['projects']:
                    print(" -", p.get('title'))
            else:
                print(data)

asyncio.run(main())
