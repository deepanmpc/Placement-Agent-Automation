import sys, re
from backend.api.main import extract_text_from_file

class Project:
    def __init__(self):
        self.title = ""
        self.description = ""
        self.technologies = []
        self.achievements = []

text = extract_text_from_file('/Users/deepandee/Downloads/2300032731_DEEPAN_CHANDRASEKARAN.pdf', '.pdf')
lines = [line.strip() for line in text.split('\n') if line.strip()]

sections = {"EDUCATION": "", "EXPERIENCE": "", "PROJECT": "", "SKILL": "", "CERTIFICATION": "", "LINKS": "", "PROFILE": "", "ACHIEVEMENT": ""}
current_section = None
for line in lines:
    upper_line = line.upper()
    matched_section = None
    for sec in sections.keys():
        if sec in upper_line and len(line) < 30:
            matched_section = sec
            break
    if matched_section:
        current_section = matched_section
    elif current_section:
        sections[current_section] += line + "\n"

proj_lines = [l.strip() for l in sections["PROJECT"].split('\n') if l.strip()]
projects = []
current_proj = None

i = 0
while i < len(proj_lines):
    line = proj_lines[i]
    is_bullet = bool(re.match(r'^[\•\-\*]', line))
    has_tech = '·' in line or '|' in line
    is_date = bool(re.search(r'\b(20\d{2}|present)\b', line, re.IGNORECASE)) and len(line) < 40
    
    is_title = False
    # Also require that it's not starting with lowercase to be a title?
    if not is_bullet and not has_tech and not is_date and len(line) < 150:
        for j in range(1, 3):
            if i + j < len(proj_lines):
                next_line = proj_lines[i+j]
                if '·' in next_line or '|' in next_line or (bool(re.search(r'\b(20\d{2}|present)\b', next_line, re.IGNORECASE)) and len(next_line) < 40):
                    is_title = True
                    break
    
    if is_title:
        if current_proj and current_proj.title:
            projects.append(current_proj)
        current_proj = Project()
        current_proj.title = line
    elif current_proj:
        if has_tech:
            current_proj.technologies.extend([t.strip() for t in re.split(r'[·|]', line) if t.strip()])
        elif is_bullet:
            clean_bullet = re.sub(r'^[\•\-\*]\s*', '', line)
            current_proj.achievements.append(clean_bullet)
            current_proj.description += clean_bullet + " "
        else:
            if not is_date:
                if current_proj.achievements:
                    current_proj.achievements[-1] += " " + line
                current_proj.description += " " + line
    i += 1

if current_proj and current_proj.title:
    projects.append(current_proj)

print(f"Extracted {len(projects)} projects:")
for p in projects:
    print(f"- {p.title} | Tech: {len(p.technologies)} | Achs: {len(p.achievements)}")
