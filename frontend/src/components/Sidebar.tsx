import type { PageView } from '../types';
import ScoringSettings, { type ScoringMode, type CustomWeights } from './ScoringSettings';

interface Props {
  active: PageView;
  onNavigate: (page: PageView) => void;
  selectedStudentId: string | null;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  scoringMode: ScoringMode;
  onScoringModeChange: (m: ScoringMode) => void;
  customWeights: CustomWeights;
  onCustomWeightsChange: (w: CustomWeights) => void;
}

const NAV_ITEMS: { id: PageView; label: string }[] = [
  { id: 'upload', label: 'Upload Resume' },
  { id: 'dashboard', label: 'Pipeline' },
  { id: 'jd-input', label: 'Job Description' },
  { id: 'candidates', label: 'Candidates' },
  { id: 'analytics', label: 'Analytics' },
];

export default function Sidebar({
  active, onNavigate, selectedStudentId, theme, onToggleTheme,
  scoringMode, onScoringModeChange, customWeights, onCustomWeightsChange
}: Props) {
  return (
    <aside className="sidebar" style={{ overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
      <div className="sidebar-brand">
        <div className="sidebar-logo">PA</div>
        <div>
          <div className="sidebar-title">Placement Agent</div>
          <div className="sidebar-sub">AI Recruitment Platform</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            className={`sidebar-link ${active === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      {/* ⚙ Scoring Settings panel */}
      <div style={{ padding: '0 1rem', flex: 1 }}>
        <ScoringSettings
          mode={scoringMode}
          onModeChange={onScoringModeChange}
          weights={customWeights}
          onWeightsChange={onCustomWeightsChange}
        />
      </div>

      <div className="sidebar-footer">
        <div className="theme-toggle-row">
          <span className="theme-toggle-label">Dark Mode</span>
          <button
            className={`theme-switch ${theme === 'dark' ? 'active' : ''}`}
            onClick={onToggleTheme}
            role="switch"
            aria-checked={theme === 'dark'}
          >
            <span className="theme-switch-knob" />
          </button>
        </div>
        <div className="sidebar-phase">
          <span className="phase-badge">Phase 1</span>
          <span>Student Intelligence</span>
        </div>
      </div>
    </aside>
  );
}
