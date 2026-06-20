import { MOCK_JD } from '../data/mockData';

export default function Dashboard() {
  return (
    <div className="page" style={{ paddingBottom: '3rem' }}>
      <div className="page-header" style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>Ranking Pipeline</h1>
        <p className="page-subtitle" style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          Current phase: <strong style={{ color: 'var(--accent)' }}>Phase 1</strong> &mdash; Student Intelligence & Automated Screening
        </p>
      </div>

      <div style={{ maxWidth: '800px' }}>
        {/* Job Description Summary */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border)',
          borderLeft: '4px solid var(--accent)',
          borderRadius: '16px',
          padding: '1.5rem',
          boxShadow: 'var(--shadow-sm)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem', flexWrap: 'wrap' }}>
              <span style={{
                fontSize: '0.68rem',
                fontWeight: 700,
                color: 'var(--accent)',
                background: 'var(--accent-bg)',
                padding: '0.2rem 0.5rem',
                borderRadius: '4px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Target Role</span>
              <span style={{
                fontSize: '0.72rem',
                color: 'var(--text-secondary)',
                background: 'var(--bg-secondary)',
                padding: '0.15rem 0.45rem',
                borderRadius: '4px',
                border: '1px solid var(--border)'
              }}>{MOCK_JD.company}</span>
            </div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
              {MOCK_JD.title}
            </h2>
          </div>

          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
            {MOCK_JD.description}
          </p>

          <hr style={{ border: 0, borderTop: '1px solid var(--border)', margin: 0 }} />

          {/* Metric Grid */}
          <div>
            <h4 style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: '0.75rem' }}>
              Core Requirements
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div style={{ padding: '0.75rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '10px' }}>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)', display: 'block', textTransform: 'uppercase', marginBottom: '0.15rem' }}>Min CGPA</span>
                <strong style={{ fontSize: '1rem', color: 'var(--text-primary)', fontWeight: 700 }}>{MOCK_JD.minCGPA} / 10</strong>
              </div>
              <div style={{ padding: '0.75rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '10px' }}>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)', display: 'block', textTransform: 'uppercase', marginBottom: '0.15rem' }}>Graduation Year</span>
                <strong style={{ fontSize: '1rem', color: 'var(--text-primary)', fontWeight: 700 }}>{MOCK_JD.graduationYear} Batch</strong>
              </div>
              <div style={{ padding: '0.75rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '10px' }}>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)', display: 'block', textTransform: 'uppercase', marginBottom: '0.15rem' }}>Backlogs Limit</span>
                <strong style={{ fontSize: '1rem', color: 'var(--text-primary)', fontWeight: 700 }}>{MOCK_JD.maxBacklogs} Active</strong>
              </div>
              <div style={{ padding: '0.75rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '10px' }}>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)', display: 'block', textTransform: 'uppercase', marginBottom: '0.15rem' }}>Min Coding Score</span>
                <strong style={{ fontSize: '1rem', color: 'var(--text-primary)', fontWeight: 700 }}>{MOCK_JD.minCodingScore || 50} pts</strong>
              </div>
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
              Eligible Branches
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
              {MOCK_JD.allowedBranches.map(branch => (
                <span key={branch} style={{
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  color: 'var(--accent)',
                  background: 'var(--accent-bg)',
                  padding: '0.2rem 0.6rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)'
                }}>{branch}</span>
              ))}
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
              Mandatory Skills
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
              {MOCK_JD.mandatorySkills.map(skill => (
                <span key={skill} style={{
                  fontSize: '0.72rem',
                  fontWeight: 500,
                  color: '#10B981',
                  background: 'rgba(16, 185, 129, 0.08)',
                  padding: '0.2rem 0.6rem',
                  borderRadius: '6px',
                  border: '1px solid rgba(16, 185, 129, 0.2)'
                }}>{skill}</span>
              ))}
            </div>
          </div>

          {MOCK_JD.preferredSkills && MOCK_JD.preferredSkills.length > 0 && (
            <div>
              <h4 style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
                Preferred Skills
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                {MOCK_JD.preferredSkills.map(skill => (
                  <span key={skill} style={{
                    fontSize: '0.72rem',
                    fontWeight: 500,
                    color: 'var(--text-primary)',
                    background: 'var(--bg-secondary)',
                    padding: '0.2rem 0.6rem',
                    borderRadius: '6px',
                    border: '1px solid var(--border)'
                  }}>{skill}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
