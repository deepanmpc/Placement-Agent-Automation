import type { ScoringMode, CustomWeights } from '../components/ScoringSettings';

interface Props {
  scoringMode: ScoringMode;
  onScoringModeChange: (m: ScoringMode) => void;
  customWeights: CustomWeights;
  onCustomWeightsChange: (w: CustomWeights) => void;
}

interface ModeUIConfig {
  title: string;
  color: string;
  desc: string;
  formula: string;
  components: { name: string; weight: string }[];
}

const FORMULA_CONFIGS: Record<ScoringMode, ModeUIConfig> = {
  dsa_mode: {
    title: 'DSA Mode (Default)',
    color: '#60A5FA',
    desc: 'Prioritizes Data Structures & Algorithms capability with a 60% weight, combined with 40% open source engineering score.',
    formula: 'Score = (DSA × 0.60) + (GitHub × 0.40)',
    components: [
      { name: 'DSA Aggregate (LC, CC, CF)', weight: '60%' },
      { name: 'GitHub Engineering', weight: '40%' },
    ],
  },
  github_mode: {
    title: 'GitHub Mode',
    color: '#A78BFA',
    desc: 'Prioritizes real-world engineering, documentation, and repository activity with a 60% weight, combined with 40% DSA rating.',
    formula: 'Score = (GitHub × 0.60) + (DSA × 0.40)',
    components: [
      { name: 'GitHub Engineering', weight: '60%' },
      { name: 'DSA Aggregate (LC, CC, CF)', weight: '40%' },
    ],
  },
  custom: {
    title: 'Custom Mode',
    color: '#34D399',
    desc: 'Fully customizable scoring weights. Set individual platform weights to customize evaluations according to your requirements.',
    formula: 'Score = LC × W_LC + CC × W_CC + CF × W_CF + GH × W_GH',
    components: [
      { name: 'User Defined Allocations', weight: '100% Total' },
    ],
  },
};

const PLATFORM_FORMULAS = [
  {
    name: 'LeetCode (LC) Formula Details',
    color: '#F59E0B',
    components: [
      { name: 'Difficulty Points (Easy × 1, Med × 3, Hard × 8)', weight: 'Max 60 pts', formula: 'MIN(Points / 3000, 1) × 60' },
      { name: 'Contest Rating Score', weight: 'Max 25 pts', formula: 'MIN(ContestRating / 2500, 1) × 25' },
      { name: 'Participation Consistency', weight: 'Max 5 pts', formula: 'MIN(ContestsAttended / 50, 1) × 5' },
      { name: 'Recent Activity (90 days)', weight: 'Max 10 pts', formula: 'MIN(ActiveDays90 / 90, 1) × 10' },
    ],
  },
  {
    name: 'CodeChef (CC) Formula Details',
    color: '#EF4444',
    components: [
      { name: 'Star Rank Points (1★=10, 2★=25, 3★=40, 4★=60...)', weight: 'Max 40 pts', formula: 'StarMapPoints × 0.40' },
      { name: 'Current Rating Score', weight: 'Max 30 pts', formula: 'MIN(Rating / 3000, 1) × 30' },
      { name: 'Problems Solved Score', weight: 'Max 15 pts', formula: 'MIN(ProblemsSolved / 1000, 1) × 15' },
      { name: 'Contest Count Score', weight: 'Max 10 pts', formula: 'MIN(ContestsCount / 50, 1) × 10' },
      { name: 'Recent Activity (90 days)', weight: 'Max 5 pts', formula: 'MIN(ActiveDays90 / 90, 1) × 5' },
    ],
  },
  {
    name: 'Codeforces (CF) Formula Details',
    color: '#3B82F6',
    components: [
      { name: 'Current Rating Score', weight: 'Max 50 pts', formula: 'MIN(CurrentRating / 3500, 1) × 50' },
      { name: 'Maximum Rating Score', weight: 'Max 20 pts', formula: 'MIN(MaxRating / 3500, 1) × 20' },
      { name: 'Problems Solved Score', weight: 'Max 15 pts', formula: 'MIN(ProblemsSolved / 3000, 1) × 15' },
      { name: 'Contest Count Score', weight: 'Max 10 pts', formula: 'MIN(ContestsCount / 100, 1) × 10' },
      { name: 'Recent Activity (90 days)', weight: 'Max 5 pts', formula: 'MIN(ActiveDays90 / 90, 1) × 5' },
    ],
  },
  {
    name: 'GitHub (GH) Engineering Formula Details',
    color: '#10B981',
    components: [
      { name: 'Public Repositories', weight: 'Max 15 pts', formula: 'MIN(PublicRepos / 50, 1) × 15' },
      { name: 'Total Repository Stars', weight: 'Max 20 pts', formula: 'MIN(TotalStars / 500, 1) × 20' },
      { name: 'Followers count', weight: 'Max 10 pts', formula: 'MIN(Followers / 250, 1) × 10' },
      { name: 'Commit Count (Year)', weight: 'Max 20 pts', formula: 'MIN(Commits365 / 1500, 1) × 20' },
      { name: 'Contribution Consistency (Days)', weight: 'Max 15 pts', formula: '(ContributionDays365 / 365) × 15' },
      { name: 'Merged Pull Requests', weight: 'Max 10 pts', formula: 'MIN(MergedPRs / 100, 1) × 10' },
      { name: 'Closed Issues', weight: 'Max 5 pts', formula: 'MIN(ClosedIssues / 100, 1) × 5' },
      { name: 'Recent Activity (90 days)', weight: 'Max 5 pts', formula: 'MIN(ActiveDays90 / 90, 1) × 5' },
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
    <div className="page" style={{ paddingBottom: '3rem' }}>
      <div className="page-header" style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text)', marginBottom: '0.4rem' }}>Scoring Engine Settings</h1>
        <p className="page-subtitle" style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Configure overall candidate ranking modes, custom platform evaluation weights, and review scoring formulas.</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        
        {/* Section 1: Ranking Modes */}
        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text)', marginBottom: '1.25rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.6rem' }}>
            Overall Ranking Mode Selection
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {(['dsa_mode', 'github_mode', 'custom'] as ScoringMode[]).map(m => {
              const f = FORMULA_CONFIGS[m];
              const isActive = scoringMode === m;
              return (
                <button
                  key={m}
                  onClick={() => onScoringModeChange(m)}
                  style={{
                    background: isActive ? `${f.color}08` : 'var(--bg)',
                    border: isActive ? `2px solid ${f.color}` : '1px solid var(--border)',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    cursor: 'pointer',
                    textAlign: 'left',
                    width: '100%',
                    boxShadow: isActive ? `0 8px 30px -10px ${f.color}35` : 'none',
                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
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
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{ width: 10, height: 10, borderRadius: '50%', background: f.color }} />
                      <strong style={{ fontSize: '1rem', fontWeight: 700, color: isActive ? f.color : 'var(--text)' }}>{f.title}</strong>
                    </div>
                    {isActive && (
                      <span style={{
                        fontSize: '0.65rem', fontWeight: 800, background: f.color, color: '#FFF',
                        padding: '0.25rem 0.6rem', borderRadius: '20px', textTransform: 'uppercase', letterSpacing: '0.06em'
                      }}>
                        Active
                      </span>
                    )}
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1.25rem', lineHeight: 1.5, height: '40px', overflow: 'hidden' }}>{f.desc}</p>
                  
                  {/* Styled Math Equation Block */}
                  <div style={{
                    display: 'flex', flexDirection: 'column', gap: '0.55rem',
                    background: 'var(--bg-secondary)', border: '1px solid var(--border)',
                    borderRadius: '8px', padding: '0.85rem 1rem'
                  }}>
                    <div style={{ fontSize: '0.62rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', borderBottom: '1px solid var(--border)', paddingBottom: '0.35rem', fontFamily: 'monospace' }}>
                      {f.formula}
                    </div>
                    {f.components.map((c, i) => (
                      <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                        <span style={{ color: 'var(--text-secondary)' }}>{c.name}</span>
                        <strong style={{ color: isActive ? f.color : 'var(--text)' }}>{c.weight}</strong>
                      </div>
                    ))}
                  </div>
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
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#34D399', margin: 0 }}>Custom Mode Scoring Allocations</h3>
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
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text)', marginBottom: '1.25rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.6rem', marginTop: '1rem' }}>
            Detailed Platform Evaluation Formulas
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.25rem' }}>
            {PLATFORM_FORMULAS.map(pf => (
              <div key={pf.name} style={{
                background: 'var(--bg)', border: '1px solid var(--border)', borderLeft: `4px solid ${pf.color}`,
                borderRadius: '10px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem',
                boxShadow: 'var(--shadow-sm)'
              }}>
                <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: pf.color, margin: 0, paddingBottom: '0.5rem', borderBottom: `1px solid ${pf.color}20` }}>{pf.name}</h3>
                
                {/* Structured Formula Rows */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {pf.components.map((comp, idx) => (
                    <div key={idx} style={{
                      display: 'flex', flexDirection: 'column', gap: '0.2rem',
                      paddingBottom: idx !== pf.components.length - 1 ? '0.65rem' : '0',
                      borderBottom: idx !== pf.components.length - 1 ? '1px solid var(--border)' : 'none'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                        <span>{comp.name}</span>
                        <span style={{ color: pf.color }}>{comp.weight}</span>
                      </div>
                      <div style={{
                        fontSize: '0.74rem', fontFamily: 'monospace', color: 'var(--text-secondary)',
                        background: 'var(--bg-secondary)', padding: '0.35rem 0.5rem', borderRadius: '4px',
                        marginTop: '0.2rem', border: '1px solid var(--border)', overflowX: 'auto',
                        whiteSpace: 'nowrap'
                      }}>
                        {comp.formula}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
