import re

with open('frontend/src/data/mockData.ts', 'r') as f:
    text = f.read()

# Replace all occurrences of skills: { ... } with skills: ['Python', 'JavaScript']
# using a regex that handles nested brackets.
# It's easier to just find "skills: {" and replace it up to the matching "}"
def replace_skills(t):
    result = []
    i = 0
    while i < len(t):
        if t[i:i+8] == 'skills: ':
            j = i + 8
            while j < len(t) and t[j] in ' \n\t': j += 1
            if j < len(t) and t[j] == '{':
                # find matching '}'
                depth = 1
                k = j + 1
                while k < len(t) and depth > 0:
                    if t[k] == '{': depth += 1
                    elif t[k] == '}': depth -= 1
                    k += 1
                # Replace everything from i to k with skills: ['Python', 'JavaScript']
                result.append("skills: ['Python', 'JavaScript']")
                i = k
                continue
        result.append(t[i])
        i += 1
    return "".join(result)

text = replace_skills(text)

# Also fix the line 434 inside computeFinalScore
# It might be `student.skills.programming_languages.filter` or similar
text = re.sub(r'student\.skills\.programming_languages\.filter', 'student.skills.filter', text)
text = re.sub(r'!student\.skills\.programming_languages\.includes\((.*?)\)\s*&&.*?\);', r'!student.skills.includes(\1));', text, flags=re.DOTALL)

with open('frontend/src/data/mockData.ts', 'w') as f:
    f.write(text)
