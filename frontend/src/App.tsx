import { useState, useEffect } from 'react';
import type { PageView } from './types';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import JDInput from './pages/JDInput';
import Candidates from './pages/Candidates';
import StudentDetail from './pages/StudentDetail';
import Analytics from './pages/Analytics';
import ResumeUpload from './pages/ResumeUpload';
import ScoringConfig from './pages/ScoringConfig';
import type { ScoringMode, CustomWeights } from './components/ScoringSettings';
import './App.css';

function getInitialTheme(): 'light' | 'dark' {
  const stored = localStorage.getItem('theme');
  if (stored === 'light' || stored === 'dark') return stored;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export default function App() {
  const [page, setPage] = useState<PageView>('upload');
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>(getInitialTheme);
  const [scoringMode, setScoringMode] = useState<ScoringMode>('dsa_mode');
  const [customWeights, setCustomWeights] = useState<CustomWeights>({ lc: 25, cc: 25, cf: 25, gh: 25 });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'light' ? 'dark' : 'light'));

  return (
    <Layout
      activePage={page}
      onNavigate={setPage}
      theme={theme}
      onToggleTheme={toggleTheme}
    >
      {page === 'upload' && <ResumeUpload />}
      {page === 'dashboard' && <Dashboard />}
      {page === 'jd-input' && <JDInput onParsed={() => setPage('dashboard')} />}
      {page === 'candidates' && (
        <Candidates
          onSelect={(id) => setSelectedStudent(id)}
          onNavigate={setPage}
          scoringMode={scoringMode}
          customWeights={customWeights}
        />
      )}
      {page === 'student' && (
        <StudentDetail
          studentId={selectedStudent}
          onNavigate={setPage}
          scoringMode={scoringMode}
          onScoringModeChange={setScoringMode}
          customWeights={customWeights}
        />
      )}
      {page === 'scoring-config' && (
        <ScoringConfig
          scoringMode={scoringMode}
          onScoringModeChange={setScoringMode}
          customWeights={customWeights}
          onCustomWeightsChange={setCustomWeights}
        />
      )}
      {page === 'analytics' && <Analytics />}
    </Layout>
  );
}
