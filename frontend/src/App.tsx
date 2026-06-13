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

function getInitialScoringMode(): ScoringMode {
  const stored = localStorage.getItem('scoringMode');
  if (stored === 'dsa_mode' || stored === 'dev_mode' || stored === 'custom_mode') return stored;
  return 'dsa_mode';
}

function getInitialCustomWeights(): CustomWeights {
  const stored = localStorage.getItem('customWeights');
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch (e) {
      // ignore parse error
    }
  }
  return { lc: 25, cc: 25, cf: 25, gh: 25 };
}

export default function App() {
  const [page, setPage] = useState<PageView>('upload');
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>(getInitialTheme);
  const [scoringMode, setScoringMode] = useState<ScoringMode>(getInitialScoringMode);
  const [customWeights, setCustomWeights] = useState<CustomWeights>(getInitialCustomWeights);

  useEffect(() => {
    fetch('http://localhost:9090/api/config')
      .then(r => r.json())
      .then(res => {
        if (res.data) {
          if (res.data.SCORING_MODE) {
            setScoringMode(res.data.SCORING_MODE as ScoringMode);
          }
          if (res.data.CUSTOM_WEIGHTS) {
            try {
              setCustomWeights(JSON.parse(res.data.CUSTOM_WEIGHTS));
            } catch (e) {}
          }
        }
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    localStorage.setItem('scoringMode', scoringMode);
    fetch('http://localhost:9090/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ SCORING_MODE: scoringMode })
    }).catch(console.error);
  }, [scoringMode]);

  useEffect(() => {
    localStorage.setItem('customWeights', JSON.stringify(customWeights));
    fetch('http://localhost:9090/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ CUSTOM_WEIGHTS: JSON.stringify(customWeights) })
    }).catch(console.error);
  }, [customWeights]);
  
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    const jwt = localStorage.getItem('jwt');
    const expires = localStorage.getItem('jwt_expires');
    if (jwt && expires && Date.now() < Number(expires)) {
      return true;
    }
    localStorage.removeItem('jwt');
    localStorage.removeItem('jwt_expires');
    return false;
  });
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');

  const handleLogin = () => {
    if (password === 'Mpc@99949') {
      const dummyJwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYWRtaW4iLCJpYXQiOjE2ODAwMDAwMDB9.x_some_dummy_signature";
      const expires = Date.now() + 60 * 60 * 1000; // 1 hour from now
      localStorage.setItem('jwt', dummyJwt);
      localStorage.setItem('jwt_expires', expires.toString());
      setIsAuthenticated(true);
      setAuthError('');
    } else {
      setAuthError('Invalid Admin Password');
    }
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'light' ? 'dark' : 'light'));

  const isProtectedPage = page !== 'upload';
  const showAuthOverlay = isProtectedPage && !isAuthenticated;

  return (
    <Layout
      activePage={page}
      onNavigate={setPage}
      theme={theme}
      onToggleTheme={toggleTheme}
    >
      <div style={{ position: 'relative', width: '100%', height: '100%' }}>
        <div style={{ 
          filter: showAuthOverlay ? 'blur(8px)' : 'none', 
          pointerEvents: showAuthOverlay ? 'none' : 'auto',
          transition: 'filter 0.3s ease',
          height: '100%'
        }}>
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
        </div>
        
        {showAuthOverlay && (
          <div style={{
            position: 'absolute',
            top: 0, left: 0, right: 0, bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}>
            <div style={{
               background: 'var(--bg-secondary)',
               border: '1px solid var(--border)',
               borderRadius: '16px',
               padding: '2.5rem',
               boxShadow: 'var(--shadow-lg)',
               width: '360px',
               textAlign: 'center'
            }}>
              <div style={{
                width: '56px',
                height: '56px',
                borderRadius: '50%',
                backgroundColor: 'var(--accent-bg)',
                color: 'var(--accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1.25rem',
              }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
              </div>
              <h2 style={{ marginBottom: '0.5rem', fontSize: '1.25rem' }}>Admin Access Required</h2>
              <p style={{ color: 'var(--text-tertiary)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                Please enter the admin password to unlock analytics and candidate rankings.
              </p>
              <input 
                type="password" 
                className="form-input" 
                placeholder="Admin Password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                onKeyDown={e => { if(e.key === 'Enter') handleLogin(); }}
                style={{ marginBottom: '1rem', textAlign: 'center' }}
              />
              {authError && (
                <div style={{ color: 'var(--color-danger)', fontSize: '0.8rem', marginBottom: '1rem' }}>
                  {authError}
                </div>
              )}
              <button className="btn btn-primary" style={{ width: '100%', padding: '0.75rem', fontSize: '0.9rem' }} onClick={handleLogin}>
                Unlock Features
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
