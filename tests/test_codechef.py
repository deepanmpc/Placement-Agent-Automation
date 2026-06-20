import urllib.request, re

html = urllib.request.urlopen('https://www.codechef.com/users/klu2300032731').read().decode('utf-8')
match = re.search(r'<div class="rating-number">.*?(\d+).*?</div>', html, re.DOTALL)
rating = int(match.group(1)) if match else 0

star_match = re.search(r'(\d+★)', html)
stars = star_match.group(1) if star_match else "1★"

hr_match = re.search(r'Highest Rating[^0-9]*(\d+)', html)
highest_rating = int(hr_match.group(1)) if hr_match else 0

c_match = re.search(r'Contests Participated[^0-9]*(\d+)', html)
contests = int(c_match.group(1)) if c_match else 0

s_match = re.search(r'Fully Solved \(([0-9]+)\)', html)
solved_count = int(s_match.group(1)) if s_match else 0

print("Rating:", rating)
print("Stars:", stars)
print("Highest Rating:", highest_rating)
print("Contests:", contests)
print("Solved:", solved_count)
