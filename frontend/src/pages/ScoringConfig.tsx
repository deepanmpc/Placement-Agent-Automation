import type { ScoringMode, CustomWeights } from '../components/ScoringSettings';

interface Props {
  scoringMode: ScoringMode;
  onScoringModeChange: (m: ScoringMode) => void;
  customWeights: CustomWeights;
  onCustomWeightsChange: (w: CustomWeights) => void;
}

const FORMULAS: Record<ScoringMode, { title: string; color: string; desc: string; lines: string[] }> = {
  dsa_mode: {
    title: 'DSA Mode (Default)',
    color: '#60A5FA',
    desc: 'Prioritizes Data Structures & Algorithms capability with a 60% weight, combined with 40% open source engineering score.',
    lines: [
      'OVERALL_DSA_MODE =',
      '  (DSA_SCORE × 0.60) + (GITHUB_SCORE × 0.40)',
      '',
      'DSA_SCORE =',
      '  LeetCode × 0.33 + CodeChef × 0.34 + Codeforces × 0.33',
    ],
  },
  github_mode: {
    title: 'GitHub Mode',
    color: '#A78BFA',
    desc: 'Prioritizes real-world engineering, documentation, and repository activity with a 60% weight, combined with 40% DSA rating.',
    lines: [
      'OVERALL_GITHUB_MODE =',
      '  (GITHUB_SCORE × 0.60) + (DSA_SCORE × 0.40)',
      '',
      'GITHUB_SCORE =',
      '  Repos(15) + Stars(20) + Followers(10) + Commits(20)',
      '  + ContribDays(15) + PRs(10) + Issues(5) + ActiveDays(5)',
    ],
  },
  custom: {
    title: 'Custom Mode',
    color: '#34D399',
    desc: 'Fully customizable scoring weights. Set individual platform weights to customize evaluations according to your requirements.',
    lines: [
      'CUSTOM_SCORE =',
      '  (LC × LC_W + CC × CC_W + CF × CF_W + GH × GH_W) / 100',
      '',
      'Adjust the sliders below to allocate weights (must sum to 100%).',
    ],
  },
};

const PLATFORM_FORMULAS = [
  {
    name: 'LeetCode (LC) Formula Details',
    color: '#F59E0B',
    formula: [
      '// 1. Difficulty Points (Capped at 3000 pts)',
      'DifficultyPoints = (Easy × 1) + (Medium × 3) + (Hard × 8)',
      'DifficultyScore = MIN(DifficultyPoints / 3000, 1) × 60',
      '',
      '// 2. Contest Rating Score',
      'ContestScore = MIN(ContestRating / 2500, 1) × 25',
      '',
      '// 3. Participation Consistency',
      'ParticipationScore = MIN(ContestsAttended / 50, 1) × 5',
      '',
      '// 4. Recent Activity',
      'ActivityScore = MIN(ActiveDays90 / 90, 1) × 10',
      '',
      '// LC_SCORE Total = Difficulty + Contest + Participation + Activity',
    ],
  },
  {
    name: 'CodeChef (CC) Formula Details',
    color: '#EF4444',
    formula: [
      '// 1. Star Rank Points',
      '1★ = 10  |  2★ = 25  |  3★ = 40  |  4★ = 60',
      '5★ = 80  |  6★ = 95  |  7★ = 100',
      'StarScore = StarMapPoints × 0.40',
      '',
      '// 2. Rating & Problem Solving Counts',
      'RatingScore = MIN(Rating / 3000, 1) × 30',
      'ProblemsScore = MIN(ProblemsSolved / 1000, 1) × 15',
      '',
      '// 3. Contest Participation & Activity',
      'ContestScore = MIN(ContestsCount / 50, 1) × 10',
      'ActivityScore = MIN(ActiveDays90 / 90, 1) × 5',
      '',
      '// CC_SCORE Total = StarScore + Rating + Problems + Contest + Activity',
    ],
  },
  {
    name: 'Codeforces (CF) Formula Details',
    color: '#3B82F6',
    formula: [
      '// 1. Live & Max Ratings',
      'RatingScore = MIN(CurrentRating / 3500, 1) × 50',
      'MaxRatingScore = MIN(MaxRating / 3500, 1) × 20',
      '',
      '// 2. Solved Problems Count',
      'SolvedScore = MIN(ProblemsSolved / 3000, 1) × 15',
      '',
      '// 3. Contest Participation & Activity',
      'ContestScore = MIN(ContestsCount / 100, 1) × 10',
      'ActivityScore = MIN(ActiveDays90 / 90, 1) × 5',
      '',
      '// CF_SCORE Total = Rating + MaxRating + Solved + Contest + Activity',
    ],
  },
  {
    name: 'GitHub (GH) Engineering Formula Details',
    color: '#10B981',
    formula: [
      '// 1. Repo counts, Stars, and Followers',
      'ReposScore = MIN(PublicRepos / 50, 1) × 15',
      'StarsScore = MIN(TotalStars / 500, 1) × 20',
      'FollowersScore = MIN(Followers / 250, 1) × 10',
      '',
      '// 2. Contribution frequency & Consistency',
      'CommitsScore = MIN(CommitsLast365 / 1500, 1) × 20',
      'ConsistencyScore = (ContributionDays365 / 365) × 15',
      '',
      '// 3. Collaboration & Pull Requests',
      'PRsScore = MIN(MergedPRs / 100, 1) × 10',
      'IssuesScore = MIN(ClosedIssues / 100, 1) × 5',
      'ActivityScore = MIN(ActiveDays90 / 90, 1) × 5',
      '',
      '// GITHUB_SCORE Total = Sum of all 8 components',
    ],
  },
];

export default function ScoringConfig({ scoringMode, onScoringModeChange, customWeights, onCustomWeightsChange }: Props) {
  const weightSum = customWeights.lc + customWeights.cc + customWeights.cf + customWeights.gh;
  const validWeights = Math.abs(weightSum - 100) < 0.01;

  const setWeight = (key: keyof CustomWeights, val: number) => {
    onCustomWeightsChange({ ...customWeights, [key]: val });
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Scoring Engine Settings</h1>
        <p className="page-subtitle">Configure overall candidate ranking modes, custom platform evaluation weights, and review scoring formulas.</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        
        {/* Section 1: Ranking Modes */}
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>
            Overall Ranking Mode
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {(['dsa_mode', 'github_mode', 'custom'] as ScoringMode[]).map(m => {
              const f = FORMULAS[m];
              const isActive = scoringMode === m;
              return (
                <button
                  key={m}
                  onClick={() => onScoringModeChange(m)}
                  style={{
                    background: isActive ? `${f.color}12` : 'var(--bg)',
                    border: isActive ? `2px solid ${f.color}` : '1px solid var(--border)',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    cursor: 'pointer',
                    textAlign: 'left',
                    width: '100%',
                    boxShadow: isActive ? `0 4px 20px -5px ${f.color}40` : 'none',
                    transition: 'all 0.2s ease',
                    position: 'relative',
                    outline: 'none',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.borderColor = f.color;
                      e.currentTarget.style.transform = 'translateY(-2px)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.borderColor = 'var(--border)';
                      e.currentTarget.style.transform = 'none';
                    }
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{ width: 10, height: 10, borderRadius: '50%', background: f.color }} />
                      <strong style={{ fontSize: '1rem', color: isActive ? f.color : 'var(--text)' }}>{f.title}</strong>
                    </div>
                    {isActive && (
                      <span style={{
                        fontSize: '0.7rem', fontWeight: 700, background: f.color, color: '#FFF',
                        padding: '0.2rem 0.5rem', borderRadius: '20px', textTransform: 'uppercase'
                      }}>
                        Active
                      </span>
                    )}
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1.25rem', lineHeight: 1.5 }}>{f.desc}</p>
                  <pre style={{
                    margin: 0, padding: '1rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)',
                    borderRadius: '8px', fontFamily: 'monospace', fontSize: '0.74rem', color: 'var(--text-primary)',
                    lineHeight: 1.6, whiteSpace: 'pre-wrap'
                  }}>
                    {f.lines.join('\n')}
                  </pre>
                </button>
              );
            })}
          </div>
        </div>

        {/* Section 2: Custom Weights Adjustments */}
        {scoringMode === 'custom' && (
          <div style={{
            background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '12px', padding: '1.5rem',
            boxShadow: 'var(--shadow-sm)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.75rem' }}>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#34D399', margin: 0 }}>Custom Mode Scoring Allocations</h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>Configure weights for each developer platform. The total allocations must sum to exactly 100%.</p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>Current Total Allocation</span>
                <div style={{ fontSize: '2rem', fontWeight: 900, color: validWeights ? '#34D399' : '#EF4444', lineHeight: 1 }}>
                  {weightSum}<span style={{ fontSize: '1.2rem', fontWeight: 500 }}>%</span>
                </div>
              </div>
            </div>

            {/* Total progress visual bar */}
            <div style={{ width: '100%', height: '8px', background: 'var(--bg-secondary)', borderRadius: '4px', overflow: 'hidden', marginBottom: '1.75rem', border: '1px solid var(--border)' }}>
              <div style={{
                height: '100%', width: `${Math.min(weightSum, 100)}%`,
                background: validWeights ? 'linear-gradient(90deg, #34D399, #10B981)' : '#EF4444',
                borderRadius: '4px', transition: 'width 0.2s ease'
              }} />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem' }}>
              {[
                { key: 'lc', label: 'LeetCode (LC) Weight', color: '#F59E0B' },
                { key: 'cc', label: 'CodeChef (CC) Weight', color: '#EF4444' },
                { key: 'cf', label: 'Codeforces (CF) Weight', color: '#3B82F6' },
                { key: 'gh', label: 'GitHub (GH) Weight', color: '#10B981' }
              ].map(item => (
                <div key={item.key} style={{
                  padding: '1.25rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)',
                  borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '0.75rem'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>{item.label}</span>
                    <strong style={{ fontSize: '1.2rem', fontWeight: 800, color: item.color }}>{customWeights[item.key as keyof CustomWeights]}%</strong>
                  </div>
                  <input
                    type="range" min={0} max={100} step={1}
                    value={customWeights[item.key as keyof CustomWeights]}
                    onChange={e => setWeight(item.key as keyof CustomWeights, Number(e.target.value))}
                    style={{ width: '100%', accentColor: item.color, cursor: 'pointer' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                    <span>0%</span>
                    <span>50%</span>
                    <span>100%</span>
                  </div>
                </div>
              ))}
            </div>

            {!validWeights && (
              <div style={{
                marginTop: '1.25rem', padding: '0.75rem 1rem', background: 'rgba(239,68,68,0.1)',
                border: '1px solid rgba(239,68,68,0.3)', borderRadius: '6px', color: '#F87171',
                fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem'
              }}>
                <span>⚠</span>
                <strong>Validation Warning:</strong> Scoring system allocations must sum to exactly 100% to take effect. Current sum: {weightSum}%.
              </div>
            )}
          </div>
        )}

        {/* Section 3: Full Platform Scoring Formula References */}
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem', marginTop: '1rem' }}>
            Detailed Platform Evaluation Formulas
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.25rem' }}>
            {PLATFORM_FORMULAS.map(pf => (
              <div key={pf.name} style={{
                background: 'var(--bg)', border: '1px solid var(--border)', borderLeft: `4px solid ${pf.color}`,
                borderRadius: '8px', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem'
              }}>
                <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: pf.color, margin: 0 }}>{pf.name}</h3>
                <pre style={{
                  margin: 0, padding: '0.75rem', background: 'var(--bg-secondary)', borderRadius: '6px',
                  fontFamily: 'monospace', fontSize: '0.72rem', color: 'var(--text-muted)',
                  lineHeight: 1.6, overflowX: 'auto', whiteSpace: 'pre'
                }}>
                  {pf.formula.join('\n')}
                </pre>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
