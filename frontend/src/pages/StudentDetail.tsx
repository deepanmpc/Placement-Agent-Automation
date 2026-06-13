import { useEffect, useState } from 'react';
import type { PageView } from '../types';
import type { Profile } from '../api';
import type { ScoringMode, CustomWeights } from '../components/ScoringSettings';

interface Props {
  studentId: string | null;
  onNavigate: (page: PageView) => void;
  scoringMode: ScoringMode;
  customWeights: CustomWeights;
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

export default function StudentDetail({ studentId, onNavigate, scoringMode, customWeights }: Props) {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);

  useEffect(() => {
    if (!studentId) return;
    fetch(`http://localhost:8000/profiles/${studentId}`, { cache: 'no-store' })
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
      const response = await fetch(`http://localhost:8000/candidates/${studentId}/sync-platforms`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to enrich');
      const data = await response.json();
      
      // Merge the newly collected data into the existing profile state
      setProfile(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          github: data.github_profile || prev.github,
          leetcode: data.leetcode_profile || prev.leetcode,
          codeforces: data.codeforces_profile || prev.codeforces,
          codechef: data.codechef_profile || prev.codechef,
          metadata: {
            ...prev.metadata,
            sources_collected: [
              ...new Set([
                ...prev.metadata.sources_collected,
                ...(data.github_profile ? ['github'] : []),
                ...(data.leetcode_profile ? ['leetcode'] : []),
                ...(data.codeforces_profile ? ['codeforces'] : []),
                ...(data.codechef_profile ? ['codechef'] : [])
              ])
            ]
          }
        };
      });
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
          <div className="detail-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h1>{s.personal_info.name || 'No Name'} {s.personal_info.id_number ? `(${s.personal_info.id_number})` : ''}</h1>
              <p className="detail-meta">
                {s.personal_info.email} &middot; {s.personal_info.phone}
              </p>
              <p className="detail-meta">
                {s.education.degree} in {s.education.branch} at {s.education.college}
                &middot; CGPA {s.education.cgpa} &middot; {s.education.graduation_year}
              </p>
            </div>
            {s.ranking && (
              <div style={{ padding: '1rem', background: 'var(--bg)', border: '1px solid var(--primary)', borderRadius: '12px', textAlign: 'right' }}>
                <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em', marginBottom: '0.2rem' }}>Intelligence Score</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)' }}>
                  {s.ranking.total_technical_score}<span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/100</span>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                  {s.ranking.github_score.total_score > 0 && <span>GH: {s.ranking.github_score.total_score}</span>}
                  {s.ranking.leetcode_score.total_score > 0 && <span>LC: {s.ranking.leetcode_score.total_score}</span>}
                  {s.ranking.codeforces_score.total_score > 0 && <span>CF: {s.ranking.codeforces_score.total_score}</span>}
                  {s.ranking.codechef_score.total_score > 0 && <span>CC: {s.ranking.codechef_score.total_score}</span>}
                </div>
              </div>
            )}
          </div>
          <div style={{ padding: '0 1.5rem 1.5rem' }}>
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

          <div className="detail-skills">
            <h3>Skills</h3>
            <SkillSection label="Programming" items={s.skills.programming_languages} />
            <SkillSection label="Frameworks" items={s.skills.frameworks} />
            <SkillSection label="All Extracted Skills" items={s.skills.all_skills} />
          </div>

        </div>

        {s.ranking && (() => {
          const r = s.ranking;
          const activeScore = scoringMode === 'dsa_mode' ? r.overall_dsa_mode
            : scoringMode === 'github_mode' ? r.overall_github_mode
            : r.custom_score ?? r.total_technical_score;
          const activeLabel = scoringMode === 'dsa_mode' ? 'DSA Mode'
            : scoringMode === 'github_mode' ? 'GitHub Mode' : 'Custom Mode';
          const activeColor = scoringMode === 'dsa_mode' ? '#60A5FA'
            : scoringMode === 'github_mode' ? '#A78BFA' : '#34D399';
          const activeFormula = scoringMode === 'dsa_mode'
            ? `DSA(${r.dsa_score}) × 0.60  +  GH(${r.github_score_total}) × 0.40`
            : scoringMode === 'github_mode'
            ? `GH(${r.github_score_total}) × 0.60  +  DSA(${r.dsa_score}) × 0.40`
            : `(LC×${customWeights.lc} + CC×${customWeights.cc} + CF×${customWeights.cf} + GH×${customWeights.gh}) / 100`;

          return (
            <div style={{ marginTop: '2rem' }}>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', marginTop: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>
                Intelligence & Capability Analysis
              </h2>

              {/* Row 1: Active mode score + all 3 modes comparison */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.25rem', marginBottom: '1.25rem' }}>
                {/* Active Mode Big Score */}
                <div className="detail-card" style={{ background: `linear-gradient(135deg, ${activeColor}18 0%, transparent 100%)`, borderColor: `${activeColor}40`, textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: activeColor, marginBottom: '0.4rem' }}>{activeLabel} Score</div>
                  <div style={{ fontSize: '3rem', fontWeight: 900, color: activeColor, lineHeight: 1 }}>
                    {activeScore}<span style={{ fontSize: '1.3rem', opacity: 0.6 }}>/100</span>
                  </div>
                  <div style={{ fontSize: '0.68rem', fontFamily: 'monospace', color: 'var(--text-muted)', marginTop: '0.75rem', lineHeight: 1.6 }}>
                    {activeFormula}
                  </div>
                </div>

                {/* All 3 Mode Comparison */}
                <div className="detail-card">
                  <h3 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>All Scoring Modes</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {[
                      { key: 'dsa_mode', label: 'Overall DSA Mode', score: r.overall_dsa_mode, color: '#60A5FA',
                        formula: `(DSA×0.60) + (GH×0.40)` },
                      { key: 'github_mode', label: 'Overall GitHub Mode', score: r.overall_github_mode, color: '#A78BFA',
                        formula: `(GH×0.60) + (DSA×0.40)` },
                      { key: 'custom', label: 'Custom Score', score: r.custom_score, color: '#34D399',
                        formula: `(LC×${customWeights.lc}+CC×${customWeights.cc}+CF×${customWeights.cf}+GH×${customWeights.gh})/100` },
                    ].map(item => (
                      <div key={item.key} style={{
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        padding: '0.5rem 0.75rem', borderRadius: '8px',
                        background: scoringMode === item.key ? `${item.color}12` : 'var(--bg)',
                        border: `1px solid ${scoringMode === item.key ? item.color : 'var(--border)'}`,
                      }}>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.82rem', color: item.color }}>{item.label}</div>
                          <div style={{ fontSize: '0.65rem', fontFamily: 'monospace', color: 'var(--text-muted)', marginTop: '0.1rem' }}>{item.formula}</div>
                        </div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: scoringMode === item.key ? item.color : 'var(--text)' }}>
                          {item.score ?? '—'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Row 2: Platform scores in detail */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem', marginBottom: '1.25rem' }}>

                {/* DSA Aggregate */}
                <div className="detail-card" style={{ borderColor: 'rgba(96,165,250,0.3)' }}>
                  <h3 style={{ color: '#60A5FA', borderBottom: '1px solid rgba(96,165,250,0.2)', paddingBottom: '0.5rem' }}>DSA Score</h3>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, textAlign: 'center', margin: '0.4rem 0 0' }}>{r.dsa_score}<span style={{ fontSize: '0.9rem', opacity: 0.6 }}>/100</span></div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'monospace', color: 'var(--text-muted)', textAlign: 'center', marginBottom: '0.75rem' }}>LC×0.33 + CC×0.34 + CF×0.33</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.82rem' }}>
                    {[
                      { name: 'LeetCode (33%)', val: r.lc_score, color: '#F59E0B' },
                      { name: 'CodeChef (34%)', val: r.cc_score, color: '#EF4444' },
                      { name: 'Codeforces (33%)', val: r.cf_score, color: '#3B82F6' },
                    ].map(p => (
                      <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: p.color }}>{p.name}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div style={{ width: 60, height: 6, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${Math.min(p.val ?? 0, 100)}%`, background: p.color, borderRadius: 3 }} />
                          </div>
                          <strong style={{ minWidth: 28, textAlign: 'right' }}>{p.val ?? 0}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* GitHub Score */}
                <div className="detail-card" style={{ borderColor: 'rgba(167,139,250,0.3)' }}>
                  <h3 style={{ color: '#A78BFA', borderBottom: '1px solid rgba(167,139,250,0.2)', paddingBottom: '0.5rem' }}>GitHub Score</h3>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, textAlign: 'center', margin: '0.4rem 0 0' }}>{r.github_score_total}<span style={{ fontSize: '0.9rem', opacity: 0.6 }}>/100</span></div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'monospace', color: 'var(--text-muted)', textAlign: 'center', marginBottom: '0.75rem' }}>Repos+Stars+Commits+Activity+…</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.82rem' }}>
                    {Object.entries(r.github_score?.breakdown ?? {}).map(([key, bd]: [string, any]) => (
                      <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>{key.replace(/_/g,' ')}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div style={{ width: 50, height: 5, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${Math.min((bd.contribution / (r.github_score?.total_score || 1)) * 100, 100)}%`, background: '#A78BFA', borderRadius: 3 }} />
                          </div>
                          <strong style={{ minWidth: 28, textAlign: 'right' }}>{bd.contribution}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* LeetCode Detail */}
                <div className="detail-card" style={{ borderColor: 'rgba(245,158,11,0.3)' }}>
                  <h3 style={{ color: '#F59E0B', borderBottom: '1px solid rgba(245,158,11,0.2)', paddingBottom: '0.5rem' }}>LeetCode Breakdown</h3>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, textAlign: 'center', margin: '0.4rem 0 0' }}>{r.lc_score}<span style={{ fontSize: '0.9rem', opacity: 0.6 }}>/100</span></div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'monospace', color: 'var(--text-muted)', textAlign: 'center', marginBottom: '0.75rem' }}>DiffScore(60)+Contest(25)+Part(5)+Activity(10)</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.82rem' }}>
                    {Object.entries(r.leetcode_score?.breakdown ?? {}).map(([key, bd]: [string, any]) => (
                      <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>{key.replace(/_/g,' ')}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <span style={{ fontSize: '0.65rem', opacity: 0.5, fontFamily: 'monospace' }}>{bd.formula}</span>
                          <strong>{bd.contribution}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

              {/* Row 3: CodeChef + Codeforces */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
                <div className="detail-card" style={{ borderColor: 'rgba(239,68,68,0.3)' }}>
                  <h3 style={{ color: '#EF4444', borderBottom: '1px solid rgba(239,68,68,0.2)', paddingBottom: '0.5rem' }}>CodeChef Breakdown</h3>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, textAlign: 'center', margin: '0.4rem 0 0' }}>{r.cc_score}<span style={{ fontSize: '0.9rem', opacity: 0.6 }}>/100</span></div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'monospace', color: 'var(--text-muted)', textAlign: 'center', marginBottom: '0.75rem' }}>Stars(40)+Rating(30)+Solved(15)+Contests(10)+Activity(5)</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.82rem' }}>
                    {Object.entries(r.codechef_score?.breakdown ?? {}).map(([key, bd]: [string, any]) => (
                      <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>{key.replace(/_/g,' ')}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <span style={{ fontSize: '0.65rem', opacity: 0.5, fontFamily: 'monospace' }}>{bd.formula}</span>
                          <strong>{bd.contribution}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="detail-card" style={{ borderColor: 'rgba(59,130,246,0.3)' }}>
                  <h3 style={{ color: '#3B82F6', borderBottom: '1px solid rgba(59,130,246,0.2)', paddingBottom: '0.5rem' }}>Codeforces Breakdown</h3>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, textAlign: 'center', margin: '0.4rem 0 0' }}>{r.cf_score}<span style={{ fontSize: '0.9rem', opacity: 0.6 }}>/100</span></div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'monospace', color: 'var(--text-muted)', textAlign: 'center', marginBottom: '0.75rem' }}>Rating(50)+MaxRating(20)+Solved(15)+Contests(10)+Activity(5)</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.82rem' }}>
                    {Object.entries(r.codeforces_score?.breakdown ?? {}).map(([key, bd]: [string, any]) => (
                      <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>{key.replace(/_/g,' ')}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <span style={{ fontSize: '0.65rem', opacity: 0.5, fontFamily: 'monospace' }}>{bd.formula}</span>
                          <strong>{bd.contribution}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          );
        })()}


        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', marginTop: '0.5rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>Open Source Profile</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
            <div className="detail-card detail-card-full">
              <h3>GitHub</h3>
              <div className="score-row">
                <div className="score-stats" style={{ width: '100%' }}>
                  <div style={{ marginBottom: '1rem' }}><strong>URL:</strong> {s.personal_info.github_url || 'Not provided'}</div>
                  {s.metadata.sources_collected.includes('github') ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '100%' }}>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.75rem', backgroundColor: 'var(--bg)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
                        <div><span style={{ color: 'var(--text-muted)' }}>Repos:</span> {s.github.public_repos}</div>
                        <div><span style={{ color: 'var(--text-muted)' }}>Stars:</span> {s.github.total_stars}</div>
                        <div><span style={{ color: 'var(--text-muted)' }}>Followers:</span> {s.github.followers}</div>
                        <div><span style={{ color: 'var(--text-muted)' }}>Consistency:</span> {s.github.contribution_consistency.toFixed(1)}%</div>
                      </div>
                      
                      {s.github.github_strength && (
                        <div style={{ backgroundColor: '#111827', borderRadius: '8px', padding: '1.25rem', border: '1px solid #374151', overflowX: 'auto', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                          <div style={{ color: '#9CA3AF', marginBottom: '0.75rem' }}>// GitHub Intelligence Evaluation</div>
                          <div style={{ color: '#E5E7EB' }}>{"{"}</div>
                          <div style={{ color: '#E5E7EB', paddingLeft: '1rem' }}>"github_strength": {"{"}</div>
                          <div style={{ color: '#A78BFA', paddingLeft: '2rem' }}>"activity_score": <span style={{ color: '#34D399' }}>{s.github.github_strength.activity_score}</span>,</div>
                          <div style={{ color: '#A78BFA', paddingLeft: '2rem' }}>"repository_score": <span style={{ color: '#34D399' }}>{s.github.github_strength.repository_score}</span>,</div>
                          <div style={{ color: '#A78BFA', paddingLeft: '2rem' }}>"collaboration_score": <span style={{ color: '#34D399' }}>{s.github.github_strength.collaboration_score}</span>,</div>
                          <div style={{ color: '#A78BFA', paddingLeft: '2rem' }}>"documentation_score": <span style={{ color: '#34D399' }}>{s.github.github_strength.documentation_score}</span>,</div>
                          <div style={{ color: '#A78BFA', paddingLeft: '2rem' }}>"community_score": <span style={{ color: '#34D399' }}>{s.github.github_strength.community_score}</span>,</div>
                          <div style={{ color: '#A78BFA', paddingLeft: '2rem' }}>"engineering_score": <span style={{ color: '#FCD34D' }}>{s.github.github_strength.engineering_score}</span></div>
                          <div style={{ color: '#E5E7EB', paddingLeft: '1rem' }}>{"}"}</div>
                          <div style={{ color: '#E5E7EB' }}>{"}"}</div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div style={{ padding: '0.75rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderLeft: '4px solid #f59e0b', borderRadius: '4px', color: '#fcd34d', fontSize: '0.85rem' }}>
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
                      <div>Rating: {s.leetcode.rating?.toFixed(0) || '0'}</div>
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
