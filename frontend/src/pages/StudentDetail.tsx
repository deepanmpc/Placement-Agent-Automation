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

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div className="detail-main">
          <div className="detail-header">
            <div>
              <h1>{s.personal_info.name || 'No Name'} {s.personal_info.id_number ? `(${s.personal_info.id_number})` : ''}</h1>
              <p className="detail-meta">
                {s.personal_info.email} &middot; {s.personal_info.phone}
              </p>
              <p className="detail-meta">
                {s.education.degree} in {s.education.branch} at {s.education.college}
                &middot; CGPA {s.education.cgpa} &middot; {s.education.graduation_year}
              </p>
              <div className="detail-links" style={{ display: 'flex', gap: '1rem', marginTop: '0.75rem', flexWrap: 'wrap' }}>
                {s.personal_info.github_url && (
                  <a href={s.personal_info.github_url.startsWith('http') ? s.personal_info.github_url : `https://${s.personal_info.github_url}`} target="_blank" rel="noreferrer" style={{ textDecoration: 'underline' }}>GitHub</a>
                )}
                {s.personal_info.linkedin_url && (
                  <a href={s.personal_info.linkedin_url.startsWith('http') ? s.personal_info.linkedin_url : `https://${s.personal_info.linkedin_url}`} target="_blank" rel="noreferrer" style={{ textDecoration: 'underline' }}>LinkedIn</a>
                )}
                {s.personal_info.portfolio_url && (
                  <a href={s.personal_info.portfolio_url.startsWith('http') ? s.personal_info.portfolio_url : `https://${s.personal_info.portfolio_url}`} target="_blank" rel="noreferrer" style={{ textDecoration: 'underline' }}>Portfolio</a>
                )}
                {s.personal_info.leetcode_username && (
                  <a href={`https://leetcode.com/u/${s.personal_info.leetcode_username}`} target="_blank" rel="noreferrer" style={{ textDecoration: 'underline' }}>LeetCode</a>
                )}
                {s.personal_info.codeforces_username && (
                  <a href={`https://codeforces.com/profile/${s.personal_info.codeforces_username}`} target="_blank" rel="noreferrer" style={{ textDecoration: 'underline' }}>Codeforces</a>
                )}
                {s.personal_info.codechef_username && (
                  <a href={`https://www.codechef.com/users/${s.personal_info.codechef_username}`} target="_blank" rel="noreferrer" style={{ textDecoration: 'underline' }}>CodeChef</a>
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

        </div>

        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', marginTop: '0.5rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>Open Source Profile</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
            <div className="detail-card">
              <h3>GitHub</h3>
              <div className="score-row">
                <div className="score-stats">
                  <div><strong>URL:</strong> {s.personal_info.github_url || 'Not provided'}</div>
                  {s.metadata.sources_collected.includes('github') ? (
                    <>
                      <div>Repos: {s.github.public_repos}</div>
                      <div>Stars: {s.github.total_stars}</div>
                      <div>Followers: {s.github.followers}</div>
                      <div>Consistency: {s.github.contribution_consistency.toFixed(1)}%</div>
                    </>
                  ) : (
                    <div style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderLeft: '4px solid #f59e0b', borderRadius: '4px', color: '#fcd34d', fontSize: '0.85rem' }}>
                      <strong>Pending Extraction:</strong> Click "Extract Recent Platform Data" above to sync live repositories, stars, and consistency scores.
                    </div>
                  )}
                </div>
              </div>
              {s.github.languages && s.github.languages.length > 0 && (
                <div className="skill-tags" style={{ marginTop: '0.5rem' }}>
                  {s.github.languages.map((l) => (
                    <span key={l} className="tag tag-lang">{l}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', marginTop: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>Coding Platforms</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
            <div className="detail-card">
              <h3>LeetCode</h3>
              <div className="score-row">
                <div className="score-stats">
                  <div><strong>Username:</strong> {s.personal_info.leetcode_username || 'Not provided'}</div>
                  {s.metadata.sources_collected.includes('leetcode') ? (
                    <>
                      <div>Rating: {s.leetcode.rating.toFixed(0)}</div>
                      <div>Solved: {s.leetcode.total_solved} (E: {s.leetcode.easy_solved}, M: {s.leetcode.medium_solved}, H: {s.leetcode.hard_solved})</div>
                    </>
                  ) : (
                    <div style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderLeft: '4px solid #f59e0b', borderRadius: '4px', color: '#fcd34d', fontSize: '0.85rem' }}>
                      <strong>Pending Extraction:</strong> Click "Extract Recent Platform Data" above to sync live problem solving counts and ratings.
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="detail-card">
              <h3>Codeforces</h3>
              <div className="score-row">
                <div className="score-stats">
                  <div><strong>Username:</strong> {s.personal_info.codeforces_username || 'Not provided'}</div>
                  {s.metadata.sources_collected.includes('codeforces') ? (
                    <>
                      <div>Rating: {s.codeforces.rating} (Max: {s.codeforces.max_rating})</div>
                      <div>Rank: {s.codeforces.rank || 'Unrated'}</div>
                      <div>Solved: {s.codeforces.solved_count}</div>
                    </>
                  ) : (
                    <div style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderLeft: '4px solid #f59e0b', borderRadius: '4px', color: '#fcd34d', fontSize: '0.85rem' }}>
                      <strong>Pending Extraction:</strong> Click "Extract Recent Platform Data" above to sync live ratings and rankings.
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="detail-card">
              <h3>CodeChef</h3>
              <div className="score-row">
                <div className="score-stats">
                  <div><strong>Username:</strong> {s.personal_info.codechef_username || 'Not provided'}</div>
                  {s.metadata.sources_collected.includes('codechef') ? (
                    <>
                      <div>Rating: {s.codechef.rating} ({s.codechef.stars || 'Unrated'})</div>
                      <div>Solved: {s.codechef.solved_count}</div>
                    </>
                  ) : (
                    <div style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderLeft: '4px solid #f59e0b', borderRadius: '4px', color: '#fcd34d', fontSize: '0.85rem' }}>
                      <strong>Pending Extraction:</strong> Click "Extract Recent Platform Data" above to sync live ratings and rankings.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', marginTop: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>System Metadata</h2>
          <div className="detail-card">
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
