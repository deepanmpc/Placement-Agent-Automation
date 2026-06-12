import { MOCK_STUDENT, MOCK_RANKINGS } from '../data/mockData';
import type { PageView } from '../types';
import ScoreGauge from '../components/ScoreGauge';
import ScoreBreakdown from '../components/ScoreBreakdown';

interface Props {
  studentId: string | null;
  onNavigate: (page: PageView) => void;
}

function SkillSection({ label, items }: { label: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div className="skill-section">
      <h4>{label}</h4>
      <div className="skill-tags">
        {items.map((s) => (
          <span key={s} className="tag tag-skill">{s}</span>
        ))}
      </div>
    </div>
  );
}

export default function StudentDetail({ studentId, onNavigate }: Props) {
  const ranking = MOCK_RANKINGS.find((r) => r.student.id === studentId);
  const student = ranking ? ranking.student : MOCK_STUDENT;
  const scores = ranking ? ranking.scores : MOCK_RANKINGS[0].scores;
  const s = student;

  return (
    <div className="page">
      <div className="page-header">
        <button className="btn btn-ghost" onClick={() => onNavigate('candidates')}>
          Back to Candidates
        </button>
      </div>

      <div className="student-detail">
        <div className="detail-main">
          <div className="detail-header">
            <div>
              <h1>{s.personalInfo.name}</h1>
              <p className="detail-meta">
                {s.personalInfo.email} &middot; {s.personalInfo.phone} &middot; {s.personalInfo.location}
              </p>
              <p className="detail-meta">
                {s.education.degree} in {s.education.specialization} at {s.education.institution}
                &middot; CGPA {s.education.cgpa} &middot; {s.education.endYear}
              </p>
              <div className="detail-links">
                <a href={`https://${s.personalInfo.github}`} target="_blank" rel="noreferrer">
                  GitHub
                </a>
                <a href={`https://${s.personalInfo.linkedin}`} target="_blank" rel="noreferrer">
                  LinkedIn
                </a>
              </div>
            </div>
            <ScoreGauge score={scores.finalScore} size={100} strokeWidth={8} label="Final" />
          </div>

          <div className="detail-skills">
            <h3>Skills</h3>
            <SkillSection label="All Skills" items={s.skills} />
          </div>

          <div className="detail-projects">
            <h3>Projects ({s.projects.length})</h3>
            {s.projects.map((p) => (
              <div key={p.title} className="project-item">
                <h4>{p.title}</h4>
                <p>{p.description}</p>
                <div className="skill-tags">
                  {p.technologies.map((t) => (
                    <span key={t} className="tag tag-tech">{t}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {s.experience.length > 0 && (
            <div className="detail-experience">
              <h3>Experience</h3>
              {s.experience.map((e) => (
                <div key={e.company + e.role} className="exp-item">
                  <h4>{e.role} at {e.company}</h4>
                  <p className="exp-duration">{e.duration}</p>
                  <p>{e.description}</p>
                </div>
              ))}
            </div>
          )}

          {s.certifications.length > 0 && (
            <div className="detail-certs">
              <h3>Certifications</h3>
              {s.certifications.map((c) => (
                <div key={c.name} className="cert-item">
                  <span>{c.name}</span>
                  <span className="cert-issuer">{c.issuer} &middot; {c.year}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="detail-sidebar">
          <div className="detail-card">
            <h3>GitHub Profile</h3>
            <div className="score-row">
              <ScoreGauge score={s.github.score} size={56} strokeWidth={4} label="GitHub" />
              <div className="score-stats">
                <div>Repos: {s.github.repositories}</div>
                <div>Stars: {s.github.stars}</div>
                <div>Commits: {s.github.commitCount}</div>
                <div>Consistency: {s.github.contributionConsistency}%</div>
              </div>
            </div>
            <div className="skill-tags">
              {s.github.languages.map((l) => (
                <span key={l} className="tag tag-lang">{l}</span>
              ))}
            </div>
          </div>

          <div className="detail-card">
            <h3>Coding Platforms</h3>
            <div className="score-row">
              <ScoreGauge score={s.coding.codingStrength} size={56} strokeWidth={4} label="Overall" />
              <div className="score-stats">
                <div>LeetCode: {s.coding.leetcode.contestRating} ({s.coding.leetcode.mediumSolved + s.coding.leetcode.easySolved + s.coding.leetcode.hardSolved} solved)</div>
                <div>Codeforces: {s.coding.codeforces.rating}</div>
                <div>CodeChef: {s.coding.codechef.rating}</div>
              </div>
            </div>
          </div>

          <div className="detail-card">
            <h3>Aptitude and Communication</h3>
            <div className="score-row">
              <ScoreGauge score={s.aptitudeScore} size={56} strokeWidth={4} label="Aptitude" />
              <ScoreGauge score={s.communicationScore} size={56} strokeWidth={4} label="Comm." />
            </div>
          </div>

          <div className="detail-card detail-card-full">
            <h3>Score Breakdown</h3>
            <ScoreBreakdown scores={scores} />
          </div>
        </div>
      </div>
    </div>
  );
}
