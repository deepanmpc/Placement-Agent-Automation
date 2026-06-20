import sys
from backend.api.main import extract_text_from_file
from backend.ingestion.resume_parser.resume_extractor import ResumeExtractor

text = extract_text_from_file('/Users/deepandee/Downloads/2300032731_DEEPAN_CHANDRASEKARAN.pdf', '.pdf')
ex = ResumeExtractor()
data = ex.parse_with_local_heuristics(text)
print(f"Extracted {len(data.projects)} projects:")
for p in data.projects:
    print(f"- {p.title} | Tech: {len(p.technologies)} | Achs: {len(p.achievements)}")
