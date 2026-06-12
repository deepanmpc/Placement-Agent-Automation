# Placement Agent Ranking Rules

## Stage 1 — Hard Filtering

Must happen before ranking.

Filters:

- CGPA
- Branch
- Backlogs
- Graduation Year
- Mandatory Skills
- Eligibility Rules

Only eligible students proceed.

---

## Stage 2 — Weighted Rule Ranking

Generate RuleScore.

Components:

1. Skill Match
2. Coding Strength
3. GitHub Strength
4. Academic Strength
5. Communication Score
6. Aptitude Score

RuleScore ∈ [0,100]

---

## Coding Strength Formula

CodingStrength =
0.2 * EasySolved
+ 0.5 * MediumSolved
+ 1.0 * HardSolved
+ 0.3 * Rating
+ Consistency

All values normalized.

---

## GitHub Strength

Factors:

- Repository Count
- Stars
- Commit Frequency
- Contribution Consistency
- Language Diversity
- Project Quality

GitHubScore ∈ [0,100]

---

## Academic Strength

Factors:

- CGPA
- Aptitude
- Communication

AcademicScore ∈ [0,100]

---

## Stage 3 — Semantic Ranking

Use embeddings.

Compare:

- Resume
- Projects
- GitHub README
- Skills
- Job Description

Output:

SemanticScore ∈ [0,100]

---

## Stage 4 — ML Ranking (Optional)

Use historical placement data.

Output:

MLScore ∈ [0,100]

---

## Final Aggregation

FinalScore =
w1 * RuleScore
+ w2 * SemanticScore
+ w3 * MLScore

Default:

w1 = 0.6
w2 = 0.4
w3 = 0.0

---

## Explainability

Every ranking must contain:

- Matched skills
- Missing skills
- Coding score breakdown
- GitHub score breakdown
- Semantic similarity breakdown
- Final score breakdown

Never return a score without explanation.
