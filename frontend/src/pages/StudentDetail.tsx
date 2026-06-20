import { useEffect, useState, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { ChevronDown, ChevronUp, Activity } from 'lucide-react';
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
  const [showDetailedMetrics, setShowDetailedMetrics] = useState(false);

  useEffect(() => {
    if (!studentId) return;
    let query = `?lc_w=${customWeights.lc}&cc_w=${customWeights.cc}&cf_w=${customWeights.cf}&gh_w=${customWeights.gh}&sm_w=${customWeights.sm || 0}`;
    const activeJd = localStorage.getItem('active_jd');
    if (activeJd) {
      query += `&job_description=${encodeURIComponent(activeJd)}`;
    }
    fetch(`http://localhost:8000/profiles/${studentId}${query}`, { cache: 'no-store' })
      .then(res => res.json())
      .then(data => {
        setProfile(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [studentId, customWeights]);

  const handleEnrich = async () => {
    if (!studentId) return;
    setEnriching(true);
    try {
      let query = `?lc_w=${customWeights.lc}&cc_w=${customWeights.cc}&cf_w=${customWeights.cf}&gh_w=${customWeights.gh}&sm_w=${customWeights.sm || 0}`;
      const activeJd = localStorage.getItem('active_jd');
      if (activeJd) {
        query += `&job_description=${encodeURIComponent(activeJd)}`;
      }
      const response = await fetch(`http://localhost:8000/candidates/${studentId}/sync-platforms${query}`, { method: 'POST' });
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
          ranking: data.ranking || prev.ranking,
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

  const aggregatedSemanticBreakdown = useMemo(() => {
    if (!profile?.ranking?.semantic_breakdown?.breakdown) return null;
    
    const breakdown = profile.ranking.semantic_breakdown.breakdown;
    const skills = breakdown.skills || { similarity_score: 0, weight: 0.3, text_snippet: 'No skills found' };
    
    const projectKeys = Object.keys(breakdown).filter(k => k.startsWith('project_'));
    let projectTotalScore = 0;
    let projectTotalWeight = 0;
    let projectSnippets: string[] = [];
    
    projectKeys.forEach(k => {
      const p = breakdown[k];
      if (!p.error) {
        projectTotalScore += p.similarity_score * p.weight;
        projectTotalWeight += p.weight;
        if (p.text_snippet) projectSnippets.push(p.text_snippet);
      }
    });
    
    const projectAvgScore = projectTotalWeight > 0 ? (projectTotalScore / projectTotalWeight) : 0;
    
    return {
      skills: {
        similarity_score: skills.similarity_score || 0,
        weight: skills.weight || 0,
        text_snippet: skills.text_snippet || ''
      },
      projects: {
        similarity_score: Math.round(projectAvgScore * 100) / 100,
        weight: Math.round(projectTotalWeight * 100) / 100,
        text_snippet: projectSnippets.length > 0 ? projectSnippets.join(' | ') : 'No projects found'
      }
    };
  }, [profile?.ranking?.semantic_breakdown]);

  if (!studentId) {
    return <div className="page"><div className="page-header"><h1>No student selected. Please go back to the dashboard.</h1></div></div>;
  }

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
          style={{ 
            fontSize: '0.85rem', 
            background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%)', 
            border: 'none',
            boxShadow: '0 4px 15px rgba(168, 85, 247, 0.4)',
            color: 'white',
            fontWeight: 800,
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}
        >
          {enriching ? 'Extracting...' : 'Extract Recent Platform Data'}
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div className="detail-main">
          <div className="detail-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '2rem' }}>
            <div style={{ flex: 1, minWidth: '300px' }}>
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
              <div style={{ padding: '1.5rem 2.5rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minWidth: '280px', boxShadow: '0 8px 24px rgba(0,0,0,0.08)' }}>
                <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.08em', marginBottom: '0.4rem', fontWeight: 600, textAlign: 'center' }}>
                  {scoringMode === 'dsa_mode' ? 'DSA Mode'
                   : scoringMode === 'github_mode' ? 'GitHub Mode'
                   : scoringMode === 'fitment_mode' ? 'Semantic Mode'
                   : 'Custom Weights'} Score
                </div>
                <div style={{ fontSize: '3rem', fontWeight: 900, color: scoringMode === 'fitment_mode' ? '#a855f7' : 'var(--accent)', lineHeight: 1, textAlign: 'center' }}>
                  {scoringMode === 'dsa_mode' ? s.ranking.overall_dsa_mode
                   : scoringMode === 'github_mode' ? s.ranking.overall_github_mode
                   : scoringMode === 'fitment_mode' ? (s.ranking.fitment_score ?? 0)
                   : (s.ranking.custom_score ?? s.ranking.total_technical_score)}<span style={{ fontSize: '1.2rem', color: 'var(--text-muted)', fontWeight: 600, marginLeft: '0.2rem' }}>/100</span>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.85rem', fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, flexWrap: 'wrap', justifyContent: 'center' }}>
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

          {s.projects && s.projects.length > 0 && (
            <div className="detail-projects" style={{ marginTop: '2rem' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '1rem', color: 'var(--text-primary)' }}>Projects & Experience</h3>
              <div style={{ display: 'grid', gap: '1rem' }}>
                {s.projects.map((proj, idx) => (
                  <div key={idx} style={{ padding: '1.25rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                      <h4 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--primary)', fontWeight: 700 }}>{proj.title}</h4>
                      {proj.github_link && (
                        <a href={proj.github_link.startsWith('http') ? proj.github_link : `https://${proj.github_link}`} target="_blank" rel="noreferrer" style={{ fontSize: '0.8rem', color: '#fff', background: 'var(--accent)', padding: '0.2rem 0.6rem', borderRadius: '4px', textDecoration: 'none', fontWeight: 600 }}>
                          View
                        </a>
                      )}
                    </div>
                    {proj.description && <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1rem', lineHeight: 1.6 }}>{proj.description}</p>}

                    {proj.technologies && proj.technologies.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.5rem' }}>
                        {proj.technologies.map((t, i) => (
                          <span key={i} style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontWeight: 500 }}>{t}</span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {s.ranking && (() => {
          const r = s.ranking;
          const isFitmentActive = scoringMode === 'fitment_mode';

          const activeScore = isFitmentActive ? (r.fitment_score ?? 0)
            : scoringMode === 'dsa_mode' ? r.overall_dsa_mode
            : scoringMode === 'github_mode' ? r.overall_github_mode
            : (r.custom_score ?? r.total_technical_score);

          const activeLabel = scoringMode === 'fitment_mode' ? 'Semantic Mode'
            : scoringMode === 'dsa_mode' ? 'DSA Mode'
            : scoringMode === 'github_mode' ? 'GitHub Mode' : 'Custom Mode';

          const activeColor = isFitmentActive ? '#a855f7' : 'var(--accent)';

          const activeFormula = scoringMode === 'fitment_mode'
            ? `DSA(${r.dsa_score}) × 0.35  +  GH(${r.github_score_total}) × 0.40  +  Semantic(${r.semantic_score ?? 0}) × 0.25`
            : scoringMode === 'dsa_mode'
            ? `DSA(${r.dsa_score}) × 0.60  +  GH(${r.github_score_total}) × 0.40`
            : scoringMode === 'github_mode'
            ? `GH(${r.github_score_total}) × 0.60  +  DSA(${r.dsa_score}) × 0.40`
            : `(LC×${customWeights.lc}+CC×${customWeights.cc}+CF×${customWeights.cf}+GH×${customWeights.gh}+SM×${customWeights.sm ?? 0})/100 = ${r.custom_score ?? 0}`;

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
                      { key: 'dsa_mode', label: 'DSA Mode', score: r.overall_dsa_mode,
                        formula: `DSA(${r.dsa_score})×0.60 + GH(${r.github_score_total})×0.40` },
                      { key: 'github_mode', label: 'GitHub Mode', score: r.overall_github_mode,
                        formula: `GH(${r.github_score_total})×0.60 + DSA(${r.dsa_score})×0.40` },
                      { key: 'fitment_mode', label: '🧠 Semantic Mode', score: r.fitment_score ?? 0,
                        formula: `DSA(35%) + GH(40%) + SM(${r.semantic_score ?? 0})(25%)` },
                      { key: 'custom', label: 'Custom Score', score: r.custom_score ?? 0,
                        formula: `LC×${customWeights.lc}+CC×${customWeights.cc}+CF×${customWeights.cf}+GH×${customWeights.gh}+SM×${customWeights.sm ?? 0}` },
                      { key: '_semantic_raw', label: 'Raw Semantic Score', score: r.semantic_score ?? 0,
                        formula: `JD cosine-similarity match across skills+projects+edu+gh` },
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
                            <div style={{ height: '100%', width: `${Math.min(bd.contribution / (bd.weight || 1), 100)}%`, background: 'var(--accent)', borderRadius: 3 }} />
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
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div style={{ width: 40, height: 5, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${Math.min(bd.contribution / (bd.weight || 1), 100)}%`, background: 'var(--accent)', borderRadius: 3 }} />
                          </div>
                          <strong style={{ color: 'var(--accent)', minWidth: 28, textAlign: 'right' }}>{bd.contribution}</strong>
                        </div>
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
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div style={{ width: 40, height: 5, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${Math.min(bd.contribution / (bd.weight || 1), 100)}%`, background: 'var(--accent)', borderRadius: 3 }} />
                          </div>
                          <strong style={{ color: 'var(--accent)', minWidth: 28, textAlign: 'right' }}>{bd.contribution}</strong>
                        </div>
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
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div style={{ width: 40, height: 5, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${Math.min(bd.contribution / (bd.weight || 1), 100)}%`, background: 'var(--accent)', borderRadius: 3 }} />
                          </div>
                          <strong style={{ color: 'var(--accent)', minWidth: 28, textAlign: 'right' }}>{bd.contribution}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Semantic/Fitment Score Card */}
              {(r.fitment_score !== undefined || r.semantic_score !== undefined) && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.25rem' }}>
                  <div className="detail-card" style={{ borderColor: 'rgba(168,85,247,0.4)' }}>
                    <h3 style={{ color: '#a855f7', borderBottom: '1px solid rgba(168,85,247,0.2)', paddingBottom: '0.5rem' }}>🧠 Semantic / JD Fitment</h3>
                    <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', margin: '0.75rem 0 1rem' }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 900, color: '#a855f7' }}>{r.semantic_score ?? 0}<span style={{ fontSize: '0.8rem', opacity: 0.6 }}>/100</span></div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>Raw Semantic</div>
                      </div>
                      <div style={{ width: '1px', background: 'var(--border)' }} />
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 900, color: '#a855f7' }}>{r.fitment_score ?? 0}<span style={{ fontSize: '0.8rem', opacity: 0.6 }}>/100</span></div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>Semantic Mode Score</div>
                      </div>
                    </div>
                    <div style={{ fontSize: '0.72rem', fontFamily: 'monospace', background: 'rgba(168,85,247,0.05)', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid rgba(168,85,247,0.2)', marginBottom: '0.75rem', color: 'var(--text-muted)' }}>
                      Semantic Mode = DSA({r.dsa_score})×0.35 + GH({r.github_score_total})×0.40 + SM({r.semantic_score ?? 0})×0.25
                    </div>
                    {aggregatedSemanticBreakdown && Object.keys(aggregatedSemanticBreakdown).length > 0 && !s.ranking?.semantic_breakdown?.error && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.78rem' }}>
                        <div style={{ fontSize: '0.68rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>JD Match by Chunk</div>
                        {Object.entries(aggregatedSemanticBreakdown).map(([chunkKey, bd]: [string, any]) => (
                          <div key={chunkKey} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.25rem 0' }}>
                            <span style={{ color: 'var(--text-primary)', textTransform: 'capitalize', fontWeight: 500 }}>
                              {chunkKey.replace(/_/g, ' ')}
                              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginLeft: '0.35rem' }}>×{bd.weight}</span>
                            </span>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <div style={{ width: 60, height: 5, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
                                <div style={{ height: '100%', width: `${Math.min(bd.similarity_score ?? 0, 100)}%`, background: '#a855f7', borderRadius: 3 }} />
                              </div>
                              <strong style={{ color: '#a855f7', minWidth: 32, textAlign: 'right' }}>{bd.similarity_score ?? 0}%</strong>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    {(!aggregatedSemanticBreakdown || s.ranking?.semantic_breakdown?.error || Object.keys(aggregatedSemanticBreakdown || {}).length === 0) && (
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textAlign: 'center', padding: '0.5rem' }}>
                        {r.semantic_breakdown?.error || 'Paste a Job Description in the JD page to activate semantic scoring.'}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Row 4: Detailed Extracted Live Metrics Container */}
              <div style={{ marginTop: '2rem' }}>
                <div 
                  onClick={() => setShowDetailedMetrics(!showDetailedMetrics)}
                  style={{ 
                    background: 'linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg) 100%)',
                    border: '1px solid var(--border)',
                    borderRadius: '12px',
                    padding: '1.25rem 1.5rem',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ padding: '0.5rem', background: 'var(--accent-bg)', borderRadius: '8px', color: 'var(--accent)' }}>
                      <Activity size={24} />
                    </div>
                    <div>
                      <h2 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0, color: 'var(--text-primary)' }}>
                        View Criteria and Data Collected
                      </h2>
                      <p style={{ margin: '0.2rem 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        Detailed breakdown of scoring formulas, extracted values, and category performances.
                      </p>
                    </div>
                  </div>
                  <div style={{ color: 'var(--text-muted)' }}>
                    {showDetailedMetrics ? <ChevronUp size={24} /> : <ChevronDown size={24} />}
                  </div>
                </div>

                {showDetailedMetrics && (
                  <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '2rem', animation: 'fadeIn 0.3s ease-out' }}>
                    
                    {/* LEETCODE SECTION */}
                    {s.metadata.sources_collected.includes('leetcode') && r.leetcode_score?.breakdown && (
                      <div className="detail-card" style={{ borderColor: 'var(--border)', display: 'flex', flexDirection: 'column' }}>
                        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.75rem', marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                          <span>LeetCode Extracted Metrics</span>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>@{s.personal_info.leetcode_username}</span>
                        </h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem', alignItems: 'center' }}>
                          <div style={{ height: 380, width: '100%' }}>
                            <ResponsiveContainer width="100%" height="100%">
                              <BarChart data={[
                                { name: 'Difficulty', score: r.leetcode_score.breakdown.difficulty_score?.contribution || 0, max: 30 },
                                { name: 'Rating', score: r.leetcode_score.breakdown.contest_score?.contribution || 0, max: 30 },
                                { name: 'Contests', score: r.leetcode_score.breakdown.participation_score?.contribution || 0, max: 20 },
                                { name: 'Global Rank', score: r.leetcode_score.breakdown.global_rank_score?.contribution || 0, max: 20 },
                              ].map(d => ({ ...d, percent: (d.score / d.max) * 100 }))} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
                                <XAxis type="number" domain={[0, 100]} hide />
                                <YAxis dataKey="name" type="category" width={90} axisLine={false} tickLine={false} tick={{fill: 'var(--text-primary)', fontSize: 12}} />
                                <RechartsTooltip 
                                  cursor={{fill: 'var(--bg-secondary)'}} 
                                  contentStyle={{backgroundColor: 'var(--bg)', borderColor: 'var(--border)', borderRadius: '8px'}} 
                                  formatter={(_value: any, _name: any, props: any) => [`${props.payload.score} / ${props.payload.max}`, 'Score']}
                                />
                                <Bar dataKey="percent" fill="var(--accent)" radius={[0, 4, 4, 0]} barSize={28} />
                              </BarChart>
                            </ResponsiveContainer>
                          </div>
                          <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
                              <thead>
                                <tr style={{ borderBottom: '2px solid var(--border)', color: 'var(--text-muted)' }}>
                                  <th style={{ padding: '0.75rem 0.5rem', fontWeight: 600 }}>Metric</th>
                                  <th style={{ padding: '0.75rem 0.5rem', fontWeight: 600, textAlign: 'right' }}>Raw Value</th>
                                  <th style={{ padding: '0.75rem 0.5rem', fontWeight: 600, textAlign: 'right' }}>Score</th>
                                  <th style={{ padding: '0.75rem 0.5rem', fontWeight: 600, paddingLeft: '1rem' }}>Formula</th>
                                </tr>
                              </thead>
                              <tbody>
                                {[
                                  { name: 'Total Solved', val: s.leetcode.total_solved?.toString() || '0', score: '-', formula: 'Informational', isSub: true },
                                  { name: 'Easy Solved', val: s.leetcode.easy_solved?.toString() || '0', score: '-', formula: '1 point per problem', isSub: true },
                                  { name: 'Medium Solved', val: s.leetcode.medium_solved?.toString() || '0', score: '-', formula: '5 points per problem', isSub: true },
                                  { name: 'Hard Solved', val: s.leetcode.hard_solved?.toString() || '0', score: '-', formula: '15 points per problem', isSub: true },
                                  { name: 'Difficulty Points', val: `${r.leetcode_score?.breakdown?.difficulty_score?.raw_value || 0}`, score: `${r.leetcode_score?.breakdown?.difficulty_score?.contribution || 0} / 30`, formula: r.leetcode_score?.breakdown?.difficulty_score?.formula },
                                  { name: 'Contest Rating', val: s.leetcode.rating?.toFixed(0) || '0', score: `${r.leetcode_score?.breakdown?.contest_score?.contribution || 0} / 30`, formula: r.leetcode_score?.breakdown?.contest_score?.formula },
                                  { name: 'Contests Attended', val: s.leetcode.contests_participated?.toString() || '0', score: `${r.leetcode_score?.breakdown?.participation_score?.contribution || 0} / 20`, formula: r.leetcode_score?.breakdown?.participation_score?.formula },
                                  { name: 'Global Ranking', val: r.leetcode_score?.breakdown?.global_rank_score?.raw_value || 'Unranked', score: `${r.leetcode_score?.breakdown?.global_rank_score?.contribution || 0} / 20`, formula: r.leetcode_score?.breakdown?.global_rank_score?.formula },
                                ].map((row, idx) => (
                                  <tr key={idx} style={{ 
                                    borderBottom: '1px solid var(--border)', 
                                    backgroundColor: row.isSub ? 'rgba(0,0,0,0.015)' : 'transparent',
                                    opacity: row.isSub ? 0.85 : 1
                                  }}>
                                    <td style={{ padding: '0.65rem 0.5rem', fontWeight: 500, paddingLeft: row.isSub ? '1.5rem' : '0.5rem', borderLeft: row.isSub ? '2px solid var(--accent)' : 'none' }}>{row.name}</td>
                                    <td style={{ padding: '0.65rem 0.5rem', textAlign: 'right', fontWeight: 700, color: 'var(--text-primary)', fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.02em' }}>{row.val}</td>
                                    <td style={{ padding: '0.65rem 0.5rem', textAlign: 'right', fontWeight: 800, color: row.isSub ? 'var(--text-muted)' : 'var(--accent)', fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.03em' }}>{row.score}</td>
                                    <td style={{ padding: '0.65rem 0.5rem', paddingLeft: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>{row.formula}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* CODECHEF SECTION */}
                    {s.metadata.sources_collected.includes('codechef') && r.codechef_score?.breakdown && (
                      <div className="detail-card" style={{ borderColor: 'var(--border)', display: 'flex', flexDirection: 'column' }}>
                        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.75rem', marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                          <span>CodeChef Extracted Metrics</span>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>@{s.personal_info.codechef_username}</span>
                        </h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem', alignItems: 'start' }}>
                          <div style={{ height: 250, width: '100%' }}>
                            <ResponsiveContainer width="100%" height="100%">
                              <BarChart data={[
                                { name: 'Stars', score: r.codechef_score.breakdown.star_score?.contribution || 0, max: 10 },
                                { name: 'Curr Rating', score: r.codechef_score.breakdown.rating_score?.contribution || 0, max: 20 },
                                { name: 'High Rating', score: r.codechef_score.breakdown.highest_rating_score?.contribution || 0, max: 10 },
                                { name: 'Problems', score: r.codechef_score.breakdown.solved_score?.contribution || 0, max: 30 },
                                { name: 'Contests', score: r.codechef_score.breakdown.contest_score?.contribution || 0, max: 30 },
                              ].map(d => ({ ...d, percent: (d.score / d.max) * 100 }))} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
                                <XAxis type="number" domain={[0, 100]} hide />
                                <YAxis dataKey="name" type="category" width={80} axisLine={false} tickLine={false} tick={{fill: 'var(--text-primary)', fontSize: 11}} />
                                <RechartsTooltip 
                                  cursor={{fill: 'var(--bg-secondary)'}} 
                                  contentStyle={{backgroundColor: 'var(--bg)', borderColor: 'var(--border)', borderRadius: '8px'}} 
                                  formatter={(_value: any, _name: any, props: any) => [`${props.payload.score} / ${props.payload.max}`, 'Score']}
                                />
                                <Bar dataKey="percent" fill="#8b5cf6" radius={[0, 4, 4, 0]} barSize={20} />
                              </BarChart>
                            </ResponsiveContainer>
                          </div>
                          <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
                              <thead>
                                <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                                  <th style={{ padding: '0.5rem', fontWeight: 500 }}>Metric</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500, textAlign: 'right' }}>Raw Value</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500, textAlign: 'right' }}>Score</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500, paddingLeft: '1rem' }}>Formula</th>
                                </tr>
                              </thead>
                              <tbody>
                                {[
                                  { name: 'Stars Rating', val: s.codechef.stars || 'Unrated', score: `${r.codechef_score?.breakdown?.star_score?.contribution || 0} / 10`, formula: r.codechef_score?.breakdown?.star_score?.formula },
                                  { name: 'Current Rating', val: s.codechef.rating || '0', score: `${r.codechef_score?.breakdown?.rating_score?.contribution || 0} / 20`, formula: r.codechef_score?.breakdown?.rating_score?.formula },
                                  { name: 'Highest Rating', val: r.codechef_score?.breakdown?.highest_rating_score?.raw_value || '0', score: `${r.codechef_score?.breakdown?.highest_rating_score?.contribution || 0} / 10`, formula: r.codechef_score?.breakdown?.highest_rating_score?.formula },
                                  { name: 'Problems Solved', val: s.codechef.solved_count || '0', score: `${r.codechef_score?.breakdown?.solved_score?.contribution || 0} / 30`, formula: r.codechef_score?.breakdown?.solved_score?.formula },
                                  { name: 'Contests Count', val: r.codechef_score?.breakdown?.contest_score?.raw_value || '0', score: `${r.codechef_score?.breakdown?.contest_score?.contribution || 0} / 30`, formula: r.codechef_score?.breakdown?.contest_score?.formula },
                                ].map((row, idx) => (
                                  <tr key={idx} style={{ borderBottom: '1px solid var(--border)' }}>
                                    <td style={{ padding: '0.5rem', fontWeight: 500 }}>{row.name}</td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 700, color: 'var(--text-primary)', fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.02em' }}>{row.val}</td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 800, color: '#8b5cf6', fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.03em' }}>{row.score}</td>
                                    <td style={{ padding: '0.5rem', paddingLeft: '1rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>{row.formula}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* CODEFORCES SECTION */}
                    {s.metadata.sources_collected.includes('codeforces') && r.codeforces_score?.breakdown && (
                      <div className="detail-card" style={{ borderColor: 'var(--border)', display: 'flex', flexDirection: 'column' }}>
                        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.75rem', marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                          <span>Codeforces Extracted Metrics</span>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>@{s.personal_info.codeforces_username}</span>
                        </h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem', alignItems: 'start' }}>
                          <div style={{ height: 250, width: '100%' }}>
                            <ResponsiveContainer width="100%" height="100%">
                              <BarChart data={[
                                { name: 'Curr Rating', score: r.codeforces_score.breakdown.rating_score?.contribution || 0, max: 45 },
                                { name: 'Max Rating', score: r.codeforces_score.breakdown.max_rating_score?.contribution || 0, max: 15 },
                                { name: 'Title/Rank', score: r.codeforces_score.breakdown.title_score?.contribution || 0, max: 10 },
                                { name: 'Problems', score: r.codeforces_score.breakdown.solved_score?.contribution || 0, max: 20 },
                                { name: 'Contests', score: r.codeforces_score.breakdown.contest_score?.contribution || 0, max: 10 },
                              ].map(d => ({ ...d, percent: (d.score / d.max) * 100 }))} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
                                <XAxis type="number" domain={[0, 100]} hide />
                                <YAxis dataKey="name" type="category" width={80} axisLine={false} tickLine={false} tick={{fill: 'var(--text-primary)', fontSize: 11}} />
                                <RechartsTooltip 
                                  cursor={{fill: 'var(--bg-secondary)'}} 
                                  contentStyle={{backgroundColor: 'var(--bg)', borderColor: 'var(--border)', borderRadius: '8px'}} 
                                  formatter={(_value: any, _name: any, props: any) => [`${props.payload.score} / ${props.payload.max}`, 'Score']}
                                />
                                <Bar dataKey="percent" fill="#f59e0b" radius={[0, 4, 4, 0]} barSize={20} />
                              </BarChart>
                            </ResponsiveContainer>
                          </div>
                          <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
                              <thead>
                                <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                                  <th style={{ padding: '0.5rem', fontWeight: 500 }}>Metric</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500, textAlign: 'right' }}>Raw Value</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500, textAlign: 'right' }}>Score</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500, paddingLeft: '1rem' }}>Formula</th>
                                </tr>
                              </thead>
                              <tbody>
                                {[
                                  { name: 'Current Rating', val: s.codeforces.rating || '0', score: `${r.codeforces_score?.breakdown?.rating_score?.contribution || 0} / 45`, formula: r.codeforces_score?.breakdown?.rating_score?.formula },
                                  { name: 'Max Rating', val: s.codeforces.max_rating || '0', score: `${r.codeforces_score?.breakdown?.max_rating_score?.contribution || 0} / 15`, formula: r.codeforces_score?.breakdown?.max_rating_score?.formula },
                                  { name: 'Title / Rank', val: r.codeforces_score?.breakdown?.title_score?.raw_value || 'Unranked', score: `${r.codeforces_score?.breakdown?.title_score?.contribution || 0} / 10`, formula: r.codeforces_score?.breakdown?.title_score?.formula },
                                  { name: 'Problems Solved', val: s.codeforces.solved_count || '0', score: `${r.codeforces_score?.breakdown?.solved_score?.contribution || 0} / 20`, formula: r.codeforces_score?.breakdown?.solved_score?.formula },
                                  { name: 'Contests Count', val: r.codeforces_score?.breakdown?.contest_score?.raw_value || '0', score: `${r.codeforces_score?.breakdown?.contest_score?.contribution || 0} / 10`, formula: r.codeforces_score?.breakdown?.contest_score?.formula },
                                ].map((row, idx) => (
                                  <tr key={idx} style={{ borderBottom: '1px solid var(--border)' }}>
                                    <td style={{ padding: '0.5rem', fontWeight: 500 }}>{row.name}</td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 700, color: 'var(--text-primary)', fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.02em' }}>{row.val}</td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 800, color: '#f59e0b', fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.03em' }}>{row.score}</td>
                                    <td style={{ padding: '0.5rem', paddingLeft: '1rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>{row.formula}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* GITHUB SECTION */}
                    {s.metadata.sources_collected.includes('github') && r.github_score?.breakdown && (
                      <div className="detail-card" style={{ borderColor: 'var(--border)', display: 'flex', flexDirection: 'column' }}>
                        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.75rem', marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                          <span>GitHub Extracted Metrics</span>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{s.personal_info.github_url ? '@' + s.personal_info.github_url.split('/').pop() : 'n/a'}</span>
                        </h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem', alignItems: 'start' }}>
                          <div style={{ height: 350, width: '100%' }}>
                            <ResponsiveContainer width="100%" height="100%">
                              <BarChart data={[
                                { name: 'Orig Repos', score: r.github_score.breakdown.original_repos_score?.contribution || 0, max: 10 },
                                { name: 'Proj Depth', score: r.github_score.breakdown.project_depth_score?.contribution || 0, max: 10 },
                                { name: 'Momentum', score: r.github_score.breakdown.momentum_score?.contribution || 0, max: 15 },
                                { name: 'Stars', score: r.github_score.breakdown.stars_score?.contribution || 0, max: 3 },
                                { name: 'Commits', score: r.github_score.breakdown.commits_score?.contribution || 0, max: 15 },
                                { name: 'Consistency', score: r.github_score.breakdown.contribution_days_score?.contribution || 0, max: 21 },
                                { name: 'Merged PRs', score: r.github_score.breakdown.merged_prs_score?.contribution || 0, max: 10 },
                                { name: 'Issues', score: r.github_score.breakdown.issues_score?.contribution || 0, max: 5 },
                                { name: 'Recent Act.', score: r.github_score.breakdown.activity_score?.contribution || 0, max: 11 },
                              ].map(d => ({ ...d, percent: (d.score / d.max) * 100 }))} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
                                <XAxis type="number" domain={[0, 100]} hide />
                                <YAxis dataKey="name" type="category" width={80} axisLine={false} tickLine={false} tick={{fill: 'var(--text-primary)', fontSize: 11}} />
                                <RechartsTooltip 
                                  cursor={{fill: 'var(--bg-secondary)'}} 
                                  contentStyle={{backgroundColor: 'var(--bg)', borderColor: 'var(--border)', borderRadius: '8px'}}
                                  formatter={(_value: any, _name: any, props: any) => [`${props.payload.score} / ${props.payload.max}`, 'Score']}
                                />
                                <Bar dataKey="percent" fill="#10b981" radius={[0, 4, 4, 0]} barSize={16} />
                              </BarChart>
                            </ResponsiveContainer>
                          </div>
                          <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
                              <thead>
                                <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                                  <th style={{ padding: '0.5rem', fontWeight: 500 }}>Metric</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500, textAlign: 'right' }}>Raw Value</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500, textAlign: 'right' }}>Score</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500, paddingLeft: '1rem' }}>Formula</th>
                                </tr>
                              </thead>
                              <tbody>
                                {[
                                  { name: 'Original Repos', val: r.github_score?.breakdown?.original_repos_score?.raw_value || '0', score: `${r.github_score?.breakdown?.original_repos_score?.contribution || 0} / 10`, formula: r.github_score?.breakdown?.original_repos_score?.formula },
                                  { name: 'Proj Depth', val: r.github_score?.breakdown?.project_depth_score?.raw_value?.toString() || '0', score: `${r.github_score?.breakdown?.project_depth_score?.contribution || 0} / 10`, formula: r.github_score?.breakdown?.project_depth_score?.formula },
                                  { name: 'Momentum', val: r.github_score?.breakdown?.momentum_score?.raw_value?.toString() || '0', score: `${r.github_score?.breakdown?.momentum_score?.contribution || 0} / 15`, formula: r.github_score?.breakdown?.momentum_score?.formula },
                                  { name: 'Stars', val: s.github.total_stars || '0', score: `${r.github_score?.breakdown?.stars_score?.contribution || 0} / 3`, formula: r.github_score?.breakdown?.stars_score?.formula },
                                  { name: 'Commits', val: r.github_score?.breakdown?.commits_score?.raw_value?.toString() || '0', score: `${r.github_score?.breakdown?.commits_score?.contribution || 0} / 15`, formula: r.github_score?.breakdown?.commits_score?.formula },
                                  { name: 'Consistency', val: `${r.github_score?.breakdown?.contribution_days_score?.raw_value || 0} days`, score: `${r.github_score?.breakdown?.contribution_days_score?.contribution || 0} / 21`, formula: r.github_score?.breakdown?.contribution_days_score?.formula },
                                  { name: 'Merged PRs', val: r.github_score?.breakdown?.merged_prs_score?.raw_value?.toString() || '0', score: `${r.github_score?.breakdown?.merged_prs_score?.contribution || 0} / 10`, formula: r.github_score?.breakdown?.merged_prs_score?.formula },
                                  { name: 'Issues', val: r.github_score?.breakdown?.issues_score?.raw_value?.toString() || '0', score: `${r.github_score?.breakdown?.issues_score?.contribution || 0} / 5`, formula: r.github_score?.breakdown?.issues_score?.formula },
                                  { name: 'Active (90d)', val: `${r.github_score?.breakdown?.activity_score?.raw_value || 0} days`, score: `${r.github_score?.breakdown?.activity_score?.contribution || 0} / 11`, formula: r.github_score?.breakdown?.activity_score?.formula },
                                ].map((row, idx) => (
                                  <tr key={idx} style={{ borderBottom: '1px solid var(--border)' }}>
                                    <td style={{ padding: '0.5rem', fontWeight: 500 }}>{row.name}</td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 700, color: 'var(--text-primary)', fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.02em' }}>{row.val}</td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 800, color: '#10b981', fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.03em' }}>{row.score}</td>
                                    <td style={{ padding: '0.5rem', paddingLeft: '1rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>{row.formula}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    )}
                    {/* SEMANTIC / FITMENT SECTION */}
                    {aggregatedSemanticBreakdown && Object.keys(aggregatedSemanticBreakdown).length > 0 && (
                      <div className="detail-card" style={{ borderColor: 'var(--border)', display: 'flex', flexDirection: 'column' }}>
                        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '0.75rem', marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                          <span>Semantic Fitment Match (RAG)</span>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Job Description Analysis</span>
                        </h3>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem', alignItems: 'start' }}>
                          <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
                              <thead>
                                <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                                  <th style={{ padding: '0.5rem', fontWeight: 500 }}>Category</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500 }}>Extracted Snippet</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500, textAlign: 'right' }}>Similarity Score</th>
                                  <th style={{ padding: '0.5rem', fontWeight: 500, textAlign: 'right' }}>Weight</th>
                                </tr>
                              </thead>
                              <tbody>
                                {Object.entries(aggregatedSemanticBreakdown).map(([key, data]: [string, any], idx) => (
                                  <tr key={idx} style={{ borderBottom: '1px solid var(--border)' }}>
                                    <td style={{ padding: '0.5rem', fontWeight: 600, textTransform: 'capitalize' }}>{key.replace('_', ' ')}</td>
                                    <td style={{ padding: '0.5rem', color: 'var(--text-primary)', maxWidth: '400px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{data.text_snippet}</td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 800, color: data.similarity_score > 70 ? '#10b981' : data.similarity_score > 40 ? '#f59e0b' : '#ef4444' }}>
                                      {data.similarity_score}%
                                    </td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', color: 'var(--text-muted)' }}>{data.weight}x</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

            </div>
          );
        })()}
      </div>
    </div>
  );
}
