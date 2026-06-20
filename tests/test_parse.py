import sys
import pypdf
reader = pypdf.PdfReader('/Users/deepandee/Downloads/2300032731_DEEPAN_CHANDRASEKARAN.pdf')
text = "".join(p.extract_text() for p in reader.pages)
sections = {"PROJECT": "", "SKILL": "", "ACHIEVEMENT": ""}
current = None
for line in text.split('\n'):
    upper = line.upper()
    matched = None
    if "PROJECT" in upper and len(line) < 30:
        matched = "PROJECT"
    elif "SKILL" in upper and len(line) < 30:
        matched = "SKILL"
    elif "ACHIEVEMENT" in upper and len(line) < 30:
        matched = "ACHIEVEMENT"
    if matched:
        current = matched
    elif current:
        sections[current] += line + "\n"

print("PROJECT SECTION:")
print(repr(sections["PROJECT"]))
