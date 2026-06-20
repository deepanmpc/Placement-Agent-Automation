import type { PageView } from '../types';

interface Props {
  active: PageView;
  onNavigate: (page: PageView) => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

const NAV_ITEMS: { id: PageView; label: string }[] = [
  { id: 'upload', label: 'Upload Resume' },
  { id: 'edit', label: 'Edit Profile' },
  { id: 'jd-input', label: 'Job Description' },
  { id: 'candidates', label: 'Candidates' },
  { id: 'analytics', label: 'Analytics' },
];

export default function Sidebar({
  active, onNavigate, theme, onToggleTheme
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
