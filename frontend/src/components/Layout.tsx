import type { ReactNode } from 'react';
import type { PageView } from '../types';
import Sidebar from './Sidebar';
import type { ScoringMode, CustomWeights } from './ScoringSettings';

interface Props {
  children: ReactNode;
  activePage: PageView;
  onNavigate: (page: PageView) => void;
  selectedStudentId: string | null;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  scoringMode: ScoringMode;
  onScoringModeChange: (m: ScoringMode) => void;
  customWeights: CustomWeights;
  onCustomWeightsChange: (w: CustomWeights) => void;
}

export default function Layout({
  children, activePage, onNavigate, selectedStudentId, theme, onToggleTheme,
  scoringMode, onScoringModeChange, customWeights, onCustomWeightsChange
}: Props) {
  return (
    <div className="layout">
      <Sidebar
        active={activePage}
        onNavigate={onNavigate}
        selectedStudentId={selectedStudentId}
        theme={theme}
        onToggleTheme={onToggleTheme}
        scoringMode={scoringMode}
        onScoringModeChange={onScoringModeChange}
        customWeights={customWeights}
        onCustomWeightsChange={onCustomWeightsChange}
      />
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
