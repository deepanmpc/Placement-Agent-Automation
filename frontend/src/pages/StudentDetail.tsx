import { useEffect, useState } from 'react';
import type { PageView } from '../types';
import type { Profile } from '../api';
import type { ScoringMode, CustomWeights } from '../components/ScoringSettings';

interface Props {
  studentId: string | null;
  onNavigate: (page: PageView) => void;
  scoringMode: ScoringMode;
  onScoringModeChange: (m: ScoringMode) => void;
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

export default function StudentDetail({ studentId, onNavigate, scoringMode, onScoringModeChange, customWeights }: Props) {
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
              <div style={{ padding: '1rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '12px', textAlign: 'right' }}>
                <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em', marginBottom: '0.2rem' }}>Intelligence Score</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--accent)' }}>
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
          const activeColor = 'var(--accent)';
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
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.25rem' }}>
                {/* Active Mode Big Score */}
                <div className="detail-card" style={{ background: 'var(--accent-bg)', borderColor: 'var(--accent)', textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: '1.5rem' }}>
                  <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: activeColor, marginBottom: '0.5rem' }}>{activeLabel} Score</div>
                  <div style={{ fontSize: '3rem', fontWeight: 900, color: activeColor, lineHeight: 1 }}>
                    {activeScore}<span style={{ fontSize: '1.3rem', opacity: 0.6 }}>/100</span>
                  </div>
                  <div style={{ fontSize: '0.68rem', fontFamily: 'monospace', color: 'var(--text-muted)', marginTop: '0.5rem', background: 'var(--bg-secondary)', padding: '0.2rem 0.5rem', borderRadius: '4px', border: '1px solid var(--border)', maxWidth: '100%', overflowX: 'auto' }}>
                    {activeFormula}
                  </div>
                </div>

                {/* All 3 Mode Comparison */}
                <div className="detail-card">
                  <h3 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>All Scoring Modes</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {[
                      { key: 'dsa_mode', label: 'Overall DSA Mode', score: r.overall_dsa_mode,
                        formula: `(DSA×0.60) + (GH×0.40)` },
                      { key: 'github_mode', label: 'Overall GitHub Mode', score: r.overall_github_mode,
                        formula: `(GH×0.60) + (DSA×0.40)` },
                      { key: 'custom', label: 'Custom Score', score: r.custom_score,
                        formula: `(LC×${customWeights.lc}+CC×${customWeights.cc}+CF×${customWeights.cf}+GH×${customWeights.gh})/100` },
                    ].map(item => (
                      <button
                        key={item.key}
                        onClick={() => onScoringModeChange(item.key as ScoringMode)}
                        style={{
                          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                          padding: '0.5rem 0.75rem', borderRadius: '8px',
                          background: scoringMode === item.key ? 'var(--accent-bg)' : 'var(--bg-secondary)',
                          border: `1px solid ${scoringMode === item.key ? 'var(--accent)' : 'var(--border)'}`,
                          cursor: 'pointer', width: '100%', textAlign: 'left',
                          fontFamily: 'inherit', color: 'inherit',
                          transition: 'all 0.15s ease',
                          outline: 'none',
                        }}
                        onMouseEnter={(e) => {
                          if (scoringMode !== item.key) {
                            e.currentTarget.style.borderColor = 'var(--accent)';
                            e.currentTarget.style.background = 'var(--accent-bg)';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (scoringMode !== item.key) {
                            e.currentTarget.style.borderColor = 'var(--border)';
                            e.currentTarget.style.background = 'var(--bg-secondary)';
                          }
                        }}
                      >
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.82rem', color: scoringMode === item.key ? 'var(--accent)' : 'var(--text-primary)' }}>{item.label}</div>
                          <div style={{ fontSize: '0.65rem', fontFamily: 'monospace', color: 'var(--text-secondary)', marginTop: '0.1rem' }}>{item.formula}</div>
                        </div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: scoringMode === item.key ? 'var(--accent)' : 'var(--text-primary)' }}>
                          {item.score ?? '—'}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Row 2: Platform scores in detail */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.25rem' }}>

                {/* DSA Aggregate */}
                <div className="detail-card">
                  <h3 style={{ color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>DSA Score</h3>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, textAlign: 'center', margin: '0.4rem 0 0.85rem', color: 'var(--text-primary)' }}>{r.dsa_score}<span style={{ fontSize: '0.9rem', opacity: 0.6 }}>/100</span></div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', fontSize: '0.82rem' }}>
                    {[
                      { name: 'LeetCode (33%)', val: r.lc_score },
                      { name: 'CodeChef (34%)', val: r.cc_score },
                      { name: 'Codeforces (33%)', val: r.cf_score },
                    ].map(p => (
                      <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: 'var(--text-primary)' }}>{p.name}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div style={{ width: 60, height: 6, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${Math.min(p.val ?? 0, 100)}%`, background: 'var(--accent)', borderRadius: 3 }} />
                          </div>
                          <strong style={{ minWidth: 28, textAlign: 'right', color: 'var(--text-primary)' }}>{p.val ?? 0}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* GitHub Score */}
                <div className="detail-card">
                  <h3 style={{ color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>GitHub Score</h3>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, textAlign: 'center', margin: '0.4rem 0 0.85rem', color: 'var(--text-primary)' }}>{r.github_score_total}<span style={{ fontSize: '0.9rem', opacity: 0.6 }}>/100</span></div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', fontSize: '0.82rem' }}>
                    {Object.entries(r.github_score?.breakdown ?? {}).map(([key, bd]: [string, any]) => (
                      <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.1rem 0' }}>
                        <span style={{ color: 'var(--text-primary)', textTransform: 'capitalize', fontWeight: 500 }}>
                          {key.replace(/_score/g, '').replace(/_/g, ' ')}
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 400, marginLeft: '0.35rem' }}>
                            ({bd.raw_value})
                          </span>
                        </span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div style={{ width: 40, height: 5, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${Math.min((bd.contribution / (r.github_score?.total_score || 1)) * 100, 100)}%`, background: 'var(--accent)', borderRadius: 3 }} />
                          </div>
                          <strong style={{ color: 'var(--accent)', minWidth: 28, textAlign: 'right' }}>{bd.contribution}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* LeetCode Detail */}
                <div className="detail-card">
                  <h3 style={{ color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>LeetCode Breakdown</h3>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, textAlign: 'center', margin: '0.4rem 0 0.85rem', color: 'var(--text-primary)' }}>{r.lc_score}<span style={{ fontSize: '0.9rem', opacity: 0.6 }}>/100</span></div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', fontSize: '0.82rem' }}>
                    {Object.entries(r.leetcode_score?.breakdown ?? {}).map(([key, bd]: [string, any]) => (
                      <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.1rem 0' }}>
                        <span style={{ color: 'var(--text-primary)', textTransform: 'capitalize', fontWeight: 500 }}>
                          {key.replace(/_score/g, '').replace(/_/g, ' ')}
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 400, marginLeft: '0.35rem' }}>
                            ({bd.raw_value})
                          </span>
                        </span>
                        <strong style={{ color: 'var(--accent)' }}>{bd.contribution}</strong>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

              {/* Row 3: CodeChef + Codeforces */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
                <div className="detail-card">
                  <h3 style={{ color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>CodeChef Breakdown</h3>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, textAlign: 'center', margin: '0.4rem 0 0.85rem', color: 'var(--text-primary)' }}>{r.cc_score}<span style={{ fontSize: '0.9rem', opacity: 0.6 }}>/100</span></div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', fontSize: '0.82rem' }}>
                    {Object.entries(r.codechef_score?.breakdown ?? {}).map(([key, bd]: [string, any]) => (
                      <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.1rem 0' }}>
                        <span style={{ color: 'var(--text-primary)', textTransform: 'capitalize', fontWeight: 500 }}>
                          {key.replace(/_score/g, '').replace(/_/g, ' ')}
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 400, marginLeft: '0.35rem' }}>
                            ({bd.raw_value})
                          </span>
                        </span>
                        <strong style={{ color: 'var(--accent)' }}>{bd.contribution}</strong>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="detail-card">
                  <h3 style={{ color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>Codeforces Breakdown</h3>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, textAlign: 'center', margin: '0.4rem 0 0.85rem', color: 'var(--text-primary)' }}>{r.cf_score}<span style={{ fontSize: '0.9rem', opacity: 0.6 }}>/100</span></div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', fontSize: '0.82rem' }}>
                    {Object.entries(r.codeforces_score?.breakdown ?? {}).map(([key, bd]: [string, any]) => (
                      <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.1rem 0' }}>
                        <span style={{ color: 'var(--text-primary)', textTransform: 'capitalize', fontWeight: 500 }}>
                          {key.replace(/_score/g, '').replace(/_/g, ' ')}
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 400, marginLeft: '0.35rem' }}>
                            ({bd.raw_value})
                          </span>
                        </span>
                        <strong style={{ color: 'var(--accent)' }}>{bd.contribution}</strong>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Row 4: Detailed Extracted Live Metrics Container */}
              <div style={{ marginTop: '2rem' }}>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>
                  Extracted Platform Data Metrics & Calculations
                </h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.25rem' }}>
                  
                  {/* LeetCode Live Card */}
                  <div className="detail-card" style={{ borderColor: 'var(--border)', display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.55rem', marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>LeetCode Extracted Metrics</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>@{s.personal_info.leetcode_username || 'n/a'}</span>
                    </h3>
                    {s.metadata.sources_collected.includes('leetcode') ? (
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem', textAlign: 'left' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500 }}>Metric</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, textAlign: 'right' }}>Raw Value</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, textAlign: 'right', paddingLeft: '0.5rem' }}>Contribution</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, paddingLeft: '0.75rem' }}>Formula & Limits</th>
                            </tr>
                          </thead>
                          <tbody>
                            {[
                              { name: 'Difficulty Points', val: `${r.leetcode_score?.breakdown?.difficulty_score?.raw_value || 0} (E:${s.leetcode.easy_solved}/M:${s.leetcode.medium_solved}/H:${s.leetcode.hard_solved})`, score: `${r.leetcode_score?.breakdown?.difficulty_score?.contribution || 0} / 60`, formula: r.leetcode_score?.breakdown?.difficulty_score?.formula },
                              { name: 'Contest Rating', val: s.leetcode.rating?.toFixed(0) || '0', score: `${r.leetcode_score?.breakdown?.contest_score?.contribution || 0} / 25`, formula: r.leetcode_score?.breakdown?.contest_score?.formula },
                              { name: 'Contests Attended', val: s.leetcode.contests_participated || '0', score: `${r.leetcode_score?.breakdown?.participation_score?.contribution || 0} / 5`, formula: r.leetcode_score?.breakdown?.participation_score?.formula },
                              { name: 'Active Days (90d)', val: r.leetcode_score?.breakdown?.activity_score?.raw_value || '0', score: `${r.leetcode_score?.breakdown?.activity_score?.contribution || 0} / 10`, formula: r.leetcode_score?.breakdown?.activity_score?.formula },
                            ].map((row, idx) => (
                              <tr key={idx} style={{ borderBottom: '1px solid var(--border)', opacity: 0.9 }}>
                                <td style={{ padding: '0.5rem 0.25rem', fontWeight: 500 }}>{row.name}</td>
                                <td style={{ padding: '0.5rem 0.25rem', textAlign: 'right', fontFamily: 'monospace' }}>{row.val}</td>
                                <td style={{ padding: '0.5rem 0.25rem', textAlign: 'right', fontWeight: 600, color: 'var(--accent)', paddingLeft: '0.5rem' }}>{row.score}</td>
                                <td style={{ padding: '0.5rem 0.25rem', paddingLeft: '0.75rem', fontFamily: 'monospace', fontSize: '0.7rem', color: 'var(--text-muted)' }}>{row.formula}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div style={{ padding: '0.75rem', backgroundColor: 'var(--accent-bg)', border: '1px dashed var(--accent)', borderRadius: '6px', color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center' }}>
                        No LeetCode data sync'd.
                      </div>
                    )}
                  </div>

                  {/* CodeChef Live Card */}
                  <div className="detail-card" style={{ borderColor: 'var(--border)', display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.55rem', marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>CodeChef Extracted Metrics</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>@{s.personal_info.codechef_username || 'n/a'}</span>
                    </h3>
                    {s.metadata.sources_collected.includes('codechef') ? (
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem', textAlign: 'left' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500 }}>Metric</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, textAlign: 'right' }}>Raw Value</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, textAlign: 'right', paddingLeft: '0.5rem' }}>Contribution</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, paddingLeft: '0.75rem' }}>Formula & Limits</th>
                            </tr>
                          </thead>
                          <tbody>
                            {[
                              { name: 'Stars Rating', val: s.codechef.stars || 'Unrated', score: `${r.codechef_score?.breakdown?.star_score?.contribution || 0} / 40`, formula: r.codechef_score?.breakdown?.star_score?.formula },
                              { name: 'Current Rating', val: s.codechef.rating || '0', score: `${r.codechef_score?.breakdown?.rating_score?.contribution || 0} / 30`, formula: r.codechef_score?.breakdown?.rating_score?.formula },
                              { name: 'Problems Solved', val: s.codechef.solved_count || '0', score: `${r.codechef_score?.breakdown?.solved_score?.contribution || 0} / 15`, formula: r.codechef_score?.breakdown?.solved_score?.formula },
                              { name: 'Contests Count', val: r.codechef_score?.breakdown?.contest_score?.raw_value || '0', score: `${r.codechef_score?.breakdown?.contest_score?.contribution || 0} / 10`, formula: r.codechef_score?.breakdown?.contest_score?.formula },
                              { name: 'Active Days (90d)', val: r.codechef_score?.breakdown?.activity_score?.raw_value || '0', score: `${r.codechef_score?.breakdown?.activity_score?.contribution || 0} / 5`, formula: r.codechef_score?.breakdown?.activity_score?.formula },
                            ].map((row, idx) => (
                              <tr key={idx} style={{ borderBottom: '1px solid var(--border)', opacity: 0.9 }}>
                                <td style={{ padding: '0.5rem 0.25rem', fontWeight: 500 }}>{row.name}</td>
                                <td style={{ padding: '0.5rem 0.25rem', textAlign: 'right', fontFamily: 'monospace' }}>{row.val}</td>
                                <td style={{ padding: '0.5rem 0.25rem', textAlign: 'right', fontWeight: 600, color: 'var(--accent)', paddingLeft: '0.5rem' }}>{row.score}</td>
                                <td style={{ padding: '0.5rem 0.25rem', paddingLeft: '0.75rem', fontFamily: 'monospace', fontSize: '0.7rem', color: 'var(--text-muted)' }}>{row.formula}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div style={{ padding: '0.75rem', backgroundColor: 'var(--accent-bg)', border: '1px dashed var(--accent)', borderRadius: '6px', color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center' }}>
                        No CodeChef data sync'd.
                      </div>
                    )}
                  </div>

                  {/* Codeforces Live Card */}
                  <div className="detail-card" style={{ borderColor: 'var(--border)', display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.55rem', marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Codeforces Extracted Metrics</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>@{s.personal_info.codeforces_username || 'n/a'}</span>
                    </h3>
                    {s.metadata.sources_collected.includes('codeforces') ? (
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem', textAlign: 'left' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500 }}>Metric</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, textAlign: 'right' }}>Raw Value</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, textAlign: 'right', paddingLeft: '0.5rem' }}>Contribution</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, paddingLeft: '0.75rem' }}>Formula & Limits</th>
                            </tr>
                          </thead>
                          <tbody>
                            {[
                              { name: 'Current Rating', val: s.codeforces.rating || '0', score: `${r.codeforces_score?.breakdown?.rating_score?.contribution || 0} / 50`, formula: r.codeforces_score?.breakdown?.rating_score?.formula },
                              { name: 'Max Rating', val: s.codeforces.max_rating || '0', score: `${r.codeforces_score?.breakdown?.max_rating_score?.contribution || 0} / 20`, formula: r.codeforces_score?.breakdown?.max_rating_score?.formula },
                              { name: 'Problems Solved', val: s.codeforces.solved_count || '0', score: `${r.codeforces_score?.breakdown?.solved_score?.contribution || 0} / 15`, formula: r.codeforces_score?.breakdown?.solved_score?.formula },
                              { name: 'Contests Count', val: r.codeforces_score?.breakdown?.contest_score?.raw_value || '0', score: `${r.codeforces_score?.breakdown?.contest_score?.contribution || 0} / 10`, formula: r.codeforces_score?.breakdown?.contest_score?.formula },
                              { name: 'Active Days (90d)', val: r.codeforces_score?.breakdown?.activity_score?.raw_value || '0', score: `${r.codeforces_score?.breakdown?.activity_score?.contribution || 0} / 5`, formula: r.codeforces_score?.breakdown?.activity_score?.formula },
                            ].map((row, idx) => (
                              <tr key={idx} style={{ borderBottom: '1px solid var(--border)', opacity: 0.9 }}>
                                <td style={{ padding: '0.5rem 0.25rem', fontWeight: 500 }}>{row.name}</td>
                                <td style={{ padding: '0.5rem 0.25rem', textAlign: 'right', fontFamily: 'monospace' }}>{row.val}</td>
                                <td style={{ padding: '0.5rem 0.25rem', textAlign: 'right', fontWeight: 600, color: 'var(--accent)', paddingLeft: '0.5rem' }}>{row.score}</td>
                                <td style={{ padding: '0.5rem 0.25rem', paddingLeft: '0.75rem', fontFamily: 'monospace', fontSize: '0.7rem', color: 'var(--text-muted)' }}>{row.formula}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div style={{ padding: '0.75rem', backgroundColor: 'var(--accent-bg)', border: '1px dashed var(--accent)', borderRadius: '6px', color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center' }}>
                        No Codeforces data sync'd.
                      </div>
                    )}
                  </div>

                  {/* GitHub Live Card */}
                  <div className="detail-card" style={{ borderColor: 'var(--border)', display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.55rem', marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>GitHub Extracted Metrics</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>{s.personal_info.github_url ? '@' + s.personal_info.github_url.split('/').pop() : 'n/a'}</span>
                    </h3>
                    {s.metadata.sources_collected.includes('github') ? (
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem', textAlign: 'left' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500 }}>Metric</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, textAlign: 'right' }}>Raw Value</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, textAlign: 'right', paddingLeft: '0.5rem' }}>Contribution</th>
                              <th style={{ padding: '0.5rem 0.25rem', fontWeight: 500, paddingLeft: '0.75rem' }}>Formula & Limits</th>
                            </tr>
                          </thead>
                          <tbody>
                            {[
                              { name: 'Public Repos', val: s.github.public_repos || '0', score: `${r.github_score?.breakdown?.repos_score?.contribution || 0} / 15`, formula: r.github_score?.breakdown?.repos_score?.formula },
                              { name: 'Total Stars', val: s.github.total_stars || '0', score: `${r.github_score?.breakdown?.stars_score?.contribution || 0} / 20`, formula: r.github_score?.breakdown?.stars_score?.formula },
                              { name: 'Followers', val: s.github.followers || '0', score: `${r.github_score?.breakdown?.followers_score?.contribution || 0} / 10`, formula: r.github_score?.breakdown?.followers_score?.formula },
                              { name: 'Commits (Year)', val: r.github_score?.breakdown?.commits_score?.raw_value || '0', score: `${r.github_score?.breakdown?.commits_score?.contribution || 0} / 20`, formula: r.github_score?.breakdown?.commits_score?.formula },
                              { name: 'Consistency', val: `${r.github_score?.breakdown?.contribution_days_score?.raw_value || 0} days`, score: `${r.github_score?.breakdown?.contribution_days_score?.contribution || 0} / 15`, formula: r.github_score?.breakdown?.contribution_days_score?.formula },
                              { name: 'Merged PRs', val: r.github_score?.breakdown?.merged_prs_score?.raw_value || '0', score: `${r.github_score?.breakdown?.merged_prs_score?.contribution || 0} / 10`, formula: r.github_score?.breakdown?.merged_prs_score?.formula },
                              { name: 'Issues Closed', val: r.github_score?.breakdown?.issues_score?.raw_value || '0', score: `${r.github_score?.breakdown?.issues_score?.contribution || 0} / 5`, formula: r.github_score?.breakdown?.issues_score?.formula },
                              { name: 'Active Days (90d)', val: r.github_score?.breakdown?.activity_score?.raw_value || '0', score: `${r.github_score?.breakdown?.activity_score?.contribution || 0} / 5`, formula: r.github_score?.breakdown?.activity_score?.formula },
                            ].map((row, idx) => (
                              <tr key={idx} style={{ borderBottom: '1px solid var(--border)', opacity: 0.9 }}>
                                <td style={{ padding: '0.5rem 0.25rem', fontWeight: 500 }}>{row.name}</td>
                                <td style={{ padding: '0.5rem 0.25rem', textAlign: 'right', fontFamily: 'monospace' }}>{row.val}</td>
                                <td style={{ padding: '0.5rem 0.25rem', textAlign: 'right', fontWeight: 600, color: 'var(--accent)', paddingLeft: '0.5rem' }}>{row.score}</td>
                                <td style={{ padding: '0.5rem 0.25rem', paddingLeft: '0.75rem', fontFamily: 'monospace', fontSize: '0.7rem', color: 'var(--text-muted)' }}>{row.formula}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div style={{ padding: '0.75rem', backgroundColor: 'var(--accent-bg)', border: '1px dashed var(--accent)', borderRadius: '6px', color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center' }}>
                        No GitHub data sync'd.
                      </div>
                    )}
                  </div>

                </div>
              </div>

            </div>
          );
        })()}
      </div>
    </div>
  );
}
