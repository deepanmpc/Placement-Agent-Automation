import { useState } from 'react';

export type ScoringMode = 'dsa_mode' | 'github_mode' | 'custom';

export interface CustomWeights {
  lc: number;
  cc: number;
  cf: number;
  gh: number;
}

interface Props {
  mode: ScoringMode;
  onModeChange: (m: ScoringMode) => void;
  weights: CustomWeights;
  onWeightsChange: (w: CustomWeights) => void;
}

const FORMULAS: Record<ScoringMode, { title: string; color: string; lines: string[] }> = {
  dsa_mode: {
    title: 'DSA Mode',
    color: '#60A5FA',
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
    color: '#A78BFA',
    lines: [
      'OVERALL_GITHUB_MODE =',
      '  (GITHUB_SCORE × 0.60)',
      '+ (DSA_SCORE × 0.40)',
      '',
      'GITHUB_SCORE =',
      '  Repos(15) + Stars(20)',
      '+ Followers(10) + Commits(20)',
      '+ ContribDays(15) + PRs(10)',
      '+ Issues(5) + ActiveDays(5)',
    ],
  },
  custom: {
    title: 'Custom Mode',
    color: '#34D399',
    lines: [
      'CUSTOM_SCORE =',
      '  (LC×LC_W + CC×CC_W',
      '  + CF×CF_W + GH×GH_W) / 100',
      '',
      'Set weights below (must = 100)',
    ],
  },
};

const PLATFORM_FORMULAS = [
  {
    name: 'LeetCode (LC)',
    color: '#F59E0B',
    formula: [
      'DiffPts = (Easy×1)+(Med×3)+(Hard×8)',
      'DiffScore = MIN(DiffPts/3000,1)×60',
      'ContestScore = MIN(Rating/2500,1)×25',
      'Participation = MIN(Contests/50,1)×5',
      'Activity = MIN(ActiveDays90/90,1)×10',
      'LC_SCORE = Diff+Contest+Part+Activity',
    ],
  },
  {
    name: 'CodeChef (CC)',
    color: '#EF4444',
    formula: [
      '1★=10  2★=25  3★=40  4★=60',
      '5★=80  6★=95  7★=100',
      'CC = (StarScore×0.40)',
      '   + MIN(Rating/3000,1)×30',
      '   + MIN(Solved/1000,1)×15',
      '   + MIN(Contests/50,1)×10',
      '   + MIN(ActiveDays90/90,1)×5',
    ],
  },
  {
    name: 'Codeforces (CF)',
    color: '#3B82F6',
    formula: [
      'CF = MIN(Rating/3500,1)×50',
      '   + MIN(MaxRating/3500,1)×20',
      '   + MIN(Solved/3000,1)×15',
      '   + MIN(Contests/100,1)×10',
      '   + MIN(ActiveDays90/90,1)×5',
    ],
  },
  {
    name: 'GitHub (GH)',
    color: '#10B981',
    formula: [
      'GH = MIN(Repos/50,1)×15',
      '   + MIN(Stars/500,1)×20',
      '   + MIN(Followers/250,1)×10',
      '   + MIN(Commits365/1500,1)×20',
      '   + (ContribDays/365)×15',
      '   + MIN(MergedPRs/100,1)×10',
      '   + MIN(Issues/100,1)×5',
      '   + MIN(ActiveDays90/90,1)×5',
    ],
  },
];

export default function ScoringSettings({ mode, onModeChange, weights, onWeightsChange }: Props) {
  const [expanded, setExpanded] = useState(true);
  const [expandedPlatform, setExpandedPlatform] = useState<string | null>(null);

  const weightSum = weights.lc + weights.cc + weights.cf + weights.gh;
  const validWeights = Math.abs(weightSum - 100) < 0.01;

  const setWeight = (key: keyof CustomWeights, val: number) => {
    onWeightsChange({ ...weights, [key]: val });
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
            fontSize: '0.74rem',
            fontWeight: 700,
            letterSpacing: '0.08em',
            color: 'var(--text)',
            textTransform: 'uppercase',
            marginTop: '0.4rem',
            marginBottom: '0.1rem',
            borderLeft: '3px solid var(--accent)',
            paddingLeft: '0.5rem',
            display: 'flex',
            alignItems: 'center'
          }}>
            Ranking Mode
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {(['dsa_mode', 'github_mode', 'custom'] as ScoringMode[]).map(m => {
              const f = FORMULAS[m];
              const isActive = mode === m;
              return (
                <button
                  key={m}
                  onClick={() => onModeChange(m)}
                  style={{
                    background: isActive ? `${f.color}12` : 'transparent',
                    border: `1px solid ${isActive ? f.color : 'var(--border)'}`,
                    borderRadius: '8px', padding: '0.6rem 0.75rem',
                    cursor: 'pointer', textAlign: 'left', width: '100%',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: isActive ? '0.35rem' : '0' }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: isActive ? f.color : 'var(--text-muted)', flexShrink: 0 }} />
                    <span style={{ fontWeight: 700, fontSize: '0.78rem', color: isActive ? f.color : 'var(--text)' }}>{f.title}</span>
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
                fontSize: '0.74rem',
                fontWeight: 700,
                letterSpacing: '0.08em',
                color: 'var(--text)',
                textTransform: 'uppercase',
                marginBottom: '0.6rem',
                borderLeft: '3px solid #34D399',
                paddingLeft: '0.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <span>Custom Weights</span>
                <span style={{ color: validWeights ? '#34D399' : '#EF4444', fontWeight: 800 }}>{weightSum}%</span>
              </div>
              
              {(['lc', 'cc', 'cf', 'gh'] as (keyof CustomWeights)[]).map(k => {
                const labels: Record<string, string> = { lc: 'LeetCode', cc: 'CodeChef', cf: 'Codeforces', gh: 'GitHub' };
                return (
                  <div key={k} style={{ marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginBottom: '0.2rem' }}>
                      <span style={{ color: 'var(--text-muted)' }}>{labels[k]}</span>
                      <span style={{ color: 'var(--text)', fontWeight: 600 }}>{weights[k]}%</span>
                    </div>
                    <input
                      type="range" min={0} max={100} step={1}
                      value={weights[k]}
                      onChange={e => setWeight(k, Number(e.target.value))}
                      style={{ width: '100%', accentColor: '#34D399' }}
                    />
                  </div>
                );
              })}
              {!validWeights && (
                <div style={{ fontSize: '0.68rem', color: '#EF4444', marginTop: '0.25rem' }}>
                  ⚠ Weights must sum to exactly 100
                </div>
              )}
            </div>
          )}

          {/* Collapsible platform formula reference */}
          <div style={{ marginTop: '0.3rem', borderTop: '1px solid var(--border)', paddingTop: '0.75rem' }}>
            <div style={{
              fontSize: '0.74rem',
              fontWeight: 700,
              letterSpacing: '0.08em',
              color: 'var(--text)',
              textTransform: 'uppercase',
              marginBottom: '0.5rem',
              borderLeft: '3px solid var(--text-muted)',
              paddingLeft: '0.5rem',
              display: 'flex',
              alignItems: 'center'
            }}>
              Formula Reference
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
