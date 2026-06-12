import { useEffect, useState } from 'react';
import type { PageView } from '../types';
import type { Profile } from '../api';

interface Props {
  studentId: string | null;
  onNavigate: (page: PageView) => void;
}

function SkillSection({ label, items }: { label: string; items: string[] }) {
  if (!items || items.length === 0) return null;
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
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);

  useEffect(() => {
    if (!studentId) return;
    fetch(`http://localhost:8000/profiles/${studentId}`)
      .then(res => res.json())
      .then(data => {
        setProfile(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [studentId]);

  const handleEnrich = async () => {
    if (!studentId) return;
    setEnriching(true);
    try {
      const response = await fetch(`http://localhost:8000/profiles/${studentId}/enrich`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to enrich');
      const data = await response.json();
      setProfile(data);
      alert('Platform data extracted successfully!');
    } catch (err) {
      console.error(err);
      alert('Failed to extract platform data.');
    } finally {
      setEnriching(false);
    }
  };

  if (loading || !profile) {
    return <div className="page"><div className="page-header"><h1>Loading student...</h1></div></div>;
  }

  const s = profile;

  return (
    <div className="page">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button className="btn btn-ghost" onClick={() => onNavigate('candidates')}>
          &larr; Back to Dashboard
        </button>
        <button 
          className="btn btn-primary" 
          onClick={handleEnrich} 
          disabled={enriching}
        >
          {enriching ? 'Extracting...' : 'Extract Recent Platform Data'}
        </button>
      </div>

      <div className="student-detail">
        <div className="detail-main">
          <div className="detail-header">
            <div>
              <h1>{s.personal_info.name || 'No Name'}</h1>
              <p className="detail-meta">
                {s.personal_info.email} &middot; {s.personal_info.phone}
              </p>
              <p className="detail-meta">
                {s.education.degree} in {s.education.branch} at {s.education.college}
                &middot; CGPA {s.education.cgpa} &middot; {s.education.graduation_year}
              </p>
              <div className="detail-links">
                {s.personal_info.github_url && (
                  <a href={s.personal_info.github_url} target="_blank" rel="noreferrer">GitHub</a>
                )}
                {s.personal_info.linkedin_url && (
                  <a href={s.personal_info.linkedin_url} target="_blank" rel="noreferrer">LinkedIn</a>
                )}
                {s.personal_info.portfolio_url && (
                  <a href={s.personal_info.portfolio_url} target="_blank" rel="noreferrer">Portfolio</a>
                )}
              </div>
            </div>
          </div>

          <div className="detail-skills">
            <h3>Skills</h3>
            <SkillSection label="Programming" items={s.skills.programming_languages} />
            <SkillSection label="Frameworks" items={s.skills.frameworks} />
            <SkillSection label="All Extracted Skills" items={s.skills.all_skills} />
          </div>

          <div className="detail-projects">
            <h3>Projects ({s.projects.length})</h3>
            {s.projects.map((p, idx) => (
              <div key={idx} className="project-item">
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
        </div>

        <div className="detail-sidebar">
          <div className="detail-card">
            <h3>GitHub Profile</h3>
            <div className="score-row">
              <div className="score-stats">
                <div>Username: {s.github.username || 'N/A'}</div>
                <div>Repos: {s.github.public_repos}</div>
                <div>Stars: {s.github.total_stars}</div>
                <div>Followers: {s.github.followers}</div>
                <div>Consistency: {s.github.contribution_consistency.toFixed(1)}%</div>
              </div>
            </div>
            <div className="skill-tags">
              {s.github.languages.map((l) => (
                <span key={l} className="tag tag-lang">{l}</span>
              ))}
            </div>
          </div>

          <div className="detail-card">
            <h3>LeetCode Profile</h3>
            <div className="score-row">
              <div className="score-stats">
                <div>Username: {s.leetcode.username || 'N/A'}</div>
                <div>Rating: {s.leetcode.rating.toFixed(0)}</div>
                <div>Solved: {s.leetcode.total_solved} (E: {s.leetcode.easy_solved}, M: {s.leetcode.medium_solved}, H: {s.leetcode.hard_solved})</div>
              </div>
            </div>
          </div>

          <div className="detail-card">
            <h3>Codeforces & CodeChef</h3>
            <div className="score-row">
              <div className="score-stats">
                <div>Codeforces: {s.codeforces.rating} (Max: {s.codeforces.max_rating}) - {s.codeforces.rank || 'Unrated'}</div>
                <div>CF Solved: {s.codeforces.solved_count}</div>
                <div>CodeChef: {s.codechef.rating} ({s.codechef.stars || 'Unrated'})</div>
                <div>CC Solved: {s.codechef.solved_count}</div>
              </div>
            </div>
          </div>

          <div className="detail-card detail-card-full">
            <h3>Metadata</h3>
            <div className="score-stats">
              <div>Ingested At: {new Date(s.metadata.ingested_at).toLocaleString()}</div>
              <div>Sources: {s.metadata.sources_collected.join(', ')}</div>
              {s.metadata.errors.length > 0 && (
                <div style={{ color: 'var(--color-danger)', marginTop: '8px' }}>
                  <strong>Errors:</strong>
                  <ul>
                    {s.metadata.errors.map((e, i) => <li key={i}>{e}</li>)}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
