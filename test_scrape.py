import httpx
from bs4 import BeautifulSoup
import re

url = "https://www.codechef.com/users/klu2300032731"
resp = httpx.get(url)
soup = BeautifulSoup(resp.text, 'html.parser')

rating = 0
rating_elem = soup.find('div', class_='rating-number')
if rating_elem:
    m = re.search(r'\d+', rating_elem.text)
    if m: rating = int(m.group())

stars = "1★"
star_elem = soup.find('div', class_='rating-star')
if star_elem:
    stars = star_elem.text.strip() or "1★"

highest = rating
highest_elem = soup.find('small')
if highest_elem and 'Highest Rating' in highest_elem.text:
    m = re.search(r'\d+', highest_elem.text)
    if m: highest = int(m.group())

solved = 0
solved_section = soup.find('section', class_='rating-data-section problems-solved')
if solved_section:
    match = re.search(r'Total Problems Solved:\s*(\d+)', solved_section.text)
    if match: solved = int(match.group(1))

contests = 0
contests_section = soup.find('div', class_='contest-participated-count')
if contests_section:
    m = re.search(r'\d+', contests_section.text)
    if m: contests = int(m.group())

print(f"Rating: {rating}")
print(f"Stars: {stars}")
print(f"Highest: {highest}")
print(f"Solved: {solved}")
print(f"Contests: {contests}")

