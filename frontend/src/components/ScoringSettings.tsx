import { useState } from 'react';

export type ScoringMode = 'dsa_mode' | 'github_mode' | 'fitment_mode' | 'custom';

export interface CustomWeights {
  lc: number;
  cc: number;
  cf: number;
  gh: number;
  sm?: number;
}

interface Props {
  mode: ScoringMode;
  onModeChange: (m: ScoringMode) => void;
  weights: CustomWeights;
  onWeightsChange: (w: CustomWeights) => void;
  onSave?: () => void;
}

const FORMULAS: Record<ScoringMode, { title: string; color: string; lines: string[] }> = {
  dsa_mode: {
    title: 'DSA Mode',
    color: 'var(--accent)',
    lines: [
      'OVERALL_DSA_MODE =',
      '  (DSA_SCORE × 0.60)',
      '+ (GITHUB_SCORE × 0.40)',
      '',
      'DSA_SCORE =',
      '  LC × 0.33',
      '+ CC × 0.34',
      '+ CF × 0.33',
    ],
  },
  github_mode: {
    title: 'GitHub Mode',
    color: 'var(--accent)',
    lines: [
      'OVERALL_GITHUB_MODE =',
      '  (GITHUB_SCORE × 0.60)',
      '+ (DSA_SCORE × 0.40)',
      '',
      'GITHUB_SCORE =',
      '  Repos(10) + Depth(10) + Momentum(15)',
      '+ Stars(3) + Commits(15) + ContribDays(21)',
      '+ PRs(10) + Issues(5) + ActiveDays(11)',
    ],
  },
  fitment_mode: {
    title: 'Semantic Mode',
    color: '#a855f7',
    lines: [
      'SEMANTIC_MODE =',
      '  (DSA_SCORE × 0.35)',
      '+ (GITHUB_SCORE × 0.40)',
      '+ (SEMANTIC_SCORE × 0.25)',
      '',
      'SEMANTIC_SCORE =',
      '  Skills chunk × 0.30',
      '+ Project chunks × 0.35 each',
      '+ Education chunk × 0.10',
      '+ GitHub langs chunk × 0.25',
    ],
  },
  custom: {
    title: 'Custom Mode',
    color: 'var(--accent)',
    lines: [
      'CUSTOM_SCORE =',
      '  (LC×LC_W + CC×CC_W',
      '  + CF×CF_W + GH×GH_W',
      '  + SM×SM_W) / 100',
      '',
      'Set weights below (must = 100)',
    ],
  },
};

const PLATFORM_FORMULAS = [
  {
    name: 'LeetCode (LC)',
    color: 'var(--accent)',
    formula: [
      'DiffPts = (Easy×1)+(Med×3)+(Hard×8)',
      'DiffScore = MIN(DiffPts/1500,1)×30',
      'ContestScore = MIN(Rating/2500,1)×30',
      'Participation = MIN(Contests/50,1)×20',
      'GlobalRank = MAX(0, (4M - rank)/4M)×20',
      'LC_SCORE = Diff+Contest+Part+GlobalRank',
    ],
  },
  {
    name: 'CodeChef (CC)',
    color: 'var(--accent)',
    formula: [
      '1★=10  2★=25  3★=40  4★=60',
      '5★=80  6★=95  7★=100',
      'StarScore (10%) + Rating/3000×20 (20%)',
      'HighestRating/3000×10 (10%)',
      'Solved/1000×30 (30%) + Contests/50×30 (30%)',
    ],
  },
  {
    name: 'Codeforces (CF)',
    color: 'var(--accent)',
    formula: [
      'Rating/3500×45 (45%)',
      'MaxRating/3500×15 (15%)',
      'TitleScore from rank tier (10%)',
      'Solved/3000×20 (20%)',
      'Contests/100×10 (10%)',
    ],
  },
  {
    name: 'GitHub (GH)',
    color: 'var(--accent)',
    formula: [
      'OriginalRepos/30×10 (10%)',
      'ProjectDepth/50×10 (10%)',
      'Momentum/30×15 (15%)',
      'Stars/30×3 (3%)',
      'Commits365/1500×15 (15%)',
      'ContribDays/365×21 (21%)',
      'MergedPRs/15×10 (10%)',
      'IssuesClosed/20×5 (5%)',
      'ActiveDays90/90×11 (11%)',
    ],
  },
  {
    name: 'Semantic / JD Match (SM)',
    color: '#a855f7',
    formula: [
      'Model: sentence-transformers/all-MiniLM-L6-v2',
      'Embed JD → query vector',
      '',
      'Chunks from StudentProfile:',
      '  Skills chunk      → weight 0.30',
      '  Project chunks    → weight 0.35 each',
      '  Education chunk   → weight 0.10',
      '  GitHub langs chunk→ weight 0.25',
      '',
      'similarity = cosine(jd_vec, chunk_vec)',
      'match_pct  = max(0, min(similarity×100, 100))',
      'weighted   = match_pct × chunk_weight',
      'SM_SCORE   = Σ(weighted) / Σ(weights)',
    ],
  },
];

export default function ScoringSettings({ mode, onModeChange, weights, onWeightsChange, onSave }: Props) {
  const [expanded, setExpanded] = useState(true);
  const [expandedPlatform, setExpandedPlatform] = useState<string | null>(null);

  const sm = weights.sm ?? 0;
  const weightSum = weights.lc + weights.cc + weights.cf + weights.gh + sm;
  const validWeights = Math.abs(weightSum - 100) < 0.01;

  const setWeight = (key: keyof CustomWeights, val: number) => {
    onWeightsChange({ ...weights, [key]: val });
  };

  const handleModeChange = (m: ScoringMode) => {
    onModeChange(m);
    // Auto-save when mode changes
    if (onSave) setTimeout(onSave, 100);
  };

  return (
    <div style={{ borderTop: '1px solid var(--border)', marginTop: '1rem', paddingTop: '1rem' }}>
      {/* Header toggle widget */}
      <button
        onClick={() => setExpanded(e => !e)}
        style={{
          width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          background: expanded ? 'var(--bg-secondary)' : 'transparent',
          border: '1px solid var(--border)', cursor: 'pointer', padding: '0.6rem 0.75rem',
          color: 'var(--text)', fontWeight: 700, fontSize: '0.78rem', letterSpacing: '0.06em',
          textTransform: 'uppercase', borderRadius: '8px', transition: 'all 0.15s ease'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ fontSize: '0.95rem' }}>⚙</span>
          <span>Scoring Settings</span>
        </div>
        <span style={{ opacity: 0.7, fontSize: '0.65rem' }}>{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>

          {/* Ranking Mode Headline */}
          <div style={{
            fontSize: '0.74rem', fontWeight: 700, letterSpacing: '0.08em', color: 'var(--text)',
            textTransform: 'uppercase', marginTop: '0.4rem', marginBottom: '0.1rem',
            borderLeft: '3px solid var(--accent)', paddingLeft: '0.5rem', display: 'flex', alignItems: 'center'
          }}>
            Ranking Mode
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {(['dsa_mode', 'github_mode', 'fitment_mode', 'custom'] as ScoringMode[]).map(m => {
              const f = FORMULAS[m];
              const isActive = mode === m;
              const isSemantic = m === 'fitment_mode';
              const borderColor = isActive ? (isSemantic ? '#a855f7' : f.color) : 'var(--border)';
              return (
                <button
                  key={m}
                  onClick={() => handleModeChange(m)}
                  style={{
                    background: isActive ? (isSemantic ? 'rgba(168,85,247,0.08)' : `${f.color}12`) : 'transparent',
                    border: `1px solid ${borderColor}`,
                    borderRadius: '8px', padding: '0.6rem 0.75rem',
                    cursor: 'pointer', textAlign: 'left', width: '100%',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: isActive ? '0.35rem' : '0' }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: isActive ? f.color : 'var(--text-muted)', flexShrink: 0 }} />
                    <span style={{ fontWeight: 700, fontSize: '0.78rem', color: isActive ? f.color : 'var(--text)' }}>{f.title}</span>
                    {isSemantic && (
                      <span style={{ fontSize: '0.6rem', padding: '0.1rem 0.35rem', background: 'rgba(168,85,247,0.15)', color: '#a855f7', borderRadius: '4px', fontWeight: 700 }}>
                        RAG
                      </span>
                    )}
                  </div>
                  {isActive && (
                    <pre style={{
                      margin: 0, fontFamily: 'monospace', fontSize: '0.67rem',
                      color: 'var(--text-muted)', lineHeight: 1.55, whiteSpace: 'pre-wrap',
                    }}>
                      {f.lines.join('\n')}
                    </pre>
                  )}
                </button>
              );
            })}
          </div>

          {/* Custom weight sliders */}
          {mode === 'custom' && (
            <div style={{ padding: '0.75rem', background: 'var(--bg)', borderRadius: '8px', border: '1px solid var(--border)' }}>
              <div style={{
                fontSize: '0.74rem', fontWeight: 700, letterSpacing: '0.08em', color: 'var(--text)',
                textTransform: 'uppercase', marginBottom: '0.6rem', borderLeft: '3px solid var(--accent)',
                paddingLeft: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between'
              }}>
                <span>Custom Weights</span>
                <span style={{ color: validWeights ? 'var(--accent)' : 'var(--color-danger)', fontWeight: 800 }}>{weightSum}%</span>
              </div>

              {([
                { key: 'lc' as keyof CustomWeights, label: 'LeetCode' },
                { key: 'cc' as keyof CustomWeights, label: 'CodeChef' },
                { key: 'cf' as keyof CustomWeights, label: 'Codeforces' },
                { key: 'gh' as keyof CustomWeights, label: 'GitHub' },
                { key: 'sm' as keyof CustomWeights, label: 'Semantic / JD Match' },
              ]).map(({ key, label }) => (
                <div key={key} style={{ marginBottom: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginBottom: '0.2rem' }}>
                    <span style={{ color: key === 'sm' ? '#a855f7' : 'var(--text-muted)', fontWeight: key === 'sm' ? 700 : 400 }}>{label}</span>
                    <span style={{ color: 'var(--text)', fontWeight: 600 }}>{weights[key] ?? 0}%</span>
                  </div>
                  <input
                    type="range" min={0} max={100} step={1}
                    value={weights[key] ?? 0}
                    onChange={e => setWeight(key, Number(e.target.value))}
                    style={{ width: '100%', accentColor: key === 'sm' ? '#a855f7' : 'var(--accent)' }}
                  />
                </div>
              ))}
              {!validWeights && (
                <div style={{ fontSize: '0.68rem', color: 'var(--color-danger)', marginTop: '0.25rem' }}>
                  ⚠ Weights must sum to exactly 100
                </div>
              )}
            </div>
          )}

          {/* Collapsible platform formula reference */}
          <div style={{ marginTop: '0.3rem', borderTop: '1px solid var(--border)', paddingTop: '0.75rem' }}>
            <div style={{
              fontSize: '0.74rem', fontWeight: 700, letterSpacing: '0.08em', color: 'var(--text)',
              textTransform: 'uppercase', marginBottom: '0.5rem', borderLeft: '3px solid var(--text-muted)',
              paddingLeft: '0.5rem', display: 'flex', alignItems: 'center'
            }}>
              DETAILED PLATFORM EVALUATION FORMULAS
            </div>

            {PLATFORM_FORMULAS.map(pf => (
              <div key={pf.name} style={{ marginBottom: '0.3rem' }}>
                <button
                  onClick={() => setExpandedPlatform(p => p === pf.name ? null : pf.name)}
                  style={{
                    width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    background: expandedPlatform === pf.name ? `${pf.color}08` : 'var(--bg)',
                    cursor: 'pointer', padding: '0.45rem 0.6rem',
                    borderRadius: '6px',
                    border: `1px solid ${expandedPlatform === pf.name ? pf.color : 'var(--border)'}`,
                    borderLeft: `3px solid ${pf.color}`,
                    transition: 'all 0.15s ease'
                  }}
                >
                  <span style={{ fontSize: '0.74rem', fontWeight: 700, color: pf.color }}>{pf.name}</span>
                  <span style={{ opacity: 0.6, fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                    {expandedPlatform === pf.name ? '▲' : '▼'}
                  </span>
                </button>
                {expandedPlatform === pf.name && (
                  <pre style={{
                    margin: '0.2rem 0 0', padding: '0.5rem', borderRadius: '6px',
                    background: 'var(--bg)', border: `1px solid ${pf.color}30`,
                    fontSize: '0.64rem', fontFamily: 'monospace', color: 'var(--text-muted)',
                    lineHeight: 1.6, whiteSpace: 'pre-wrap', wordBreak: 'break-word',
                  }}>
                    {pf.formula.join('\n')}
                  </pre>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
