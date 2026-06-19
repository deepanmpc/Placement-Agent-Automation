import { useState, useEffect } from 'react';
import type { JDRequirements } from '../types';
import { MOCK_JD } from '../data/mockData';
import type { ScoringMode, CustomWeights } from '../components/ScoringSettings';
import ScoringConfig from './ScoringConfig';

interface Props {
  onParsed: (jd: JDRequirements | null) => void;
  scoringMode: ScoringMode;
  onScoringModeChange: (m: ScoringMode) => void;
  customWeights: CustomWeights;
  onCustomWeightsChange: (w: CustomWeights) => void;
  onSave: () => void;
}

export default function JDInput({ 
  onParsed, 
  scoringMode, 
  onScoringModeChange, 
  customWeights, 
  onCustomWeightsChange, 
  onSave 
}: Props) {
  const [jdText, setJdText] = useState('');
  const [showMock, setShowMock] = useState(false);

  useEffect(() => {
    const savedJd = localStorage.getItem('active_jd');
    if (savedJd) {
      setJdText(savedJd);
    }
  }, []);

  const handleClear = () => {
    localStorage.removeItem('active_jd');
    setJdText('');
    onParsed(null);
    alert('Job Description cleared. Reverting to technical skill ranking.');
  };

  const handleParse = () => {
    if (!jdText.trim()) return;
    localStorage.setItem('active_jd', jdText);
    alert('Job Description saved! Candidates will now be ranked by Fitment Score.');
    onParsed({
      title: 'Parsed Job Description',
      company: 'Imported Company',
      description: jdText,
      minCGPA: 7.0,
      allowedBranches: ['CSE', 'IT', 'ECE'],
      maxBacklogs: 0,
      graduationYear: 2026,
      mandatorySkills: ['Python', 'JavaScript', 'SQL'],
      preferredSkills: ['React', 'Node.js'],
      minCodingScore: 40,
    });
  };

  return (
    <div className="page" style={{ overflowY: 'auto' }}>
      <div className="page-header">
        <h1>Job Description</h1>
        <p className="page-subtitle">
          Paste a job description to extract hiring requirements and set active matching.
        </p>
      </div>

      <div className="jd-input-card">
        <label className="jd-label">Job Description Text</label>
        <textarea
          className="jd-textarea"
          rows={10}
          placeholder="Paste the job description here..."
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
        />
        <div className="jd-actions">
          <button className="btn btn-primary" onClick={handleParse} disabled={!jdText.trim()}>
            Save & Apply JD
          </button>
          <button className="btn btn-danger" onClick={handleClear} disabled={!jdText.trim()} style={{ backgroundColor: '#dc3545', color: 'white' }}>
            Clear JD
          </button>
          <button className="btn btn-secondary" onClick={() => setShowMock(!showMock)}>
            {showMock ? 'Hide' : 'Show'} Sample
          </button>
        </div>
      </div>

      {showMock && (
        <div className="jd-preview">
          <h3>Sample: {MOCK_JD.title} at {MOCK_JD.company}</h3>
          <p>{MOCK_JD.description}</p>
          <div className="jd-badges">
            <span className="jd-badge">Min CGPA: {MOCK_JD.minCGPA}</span>
            <span className="jd-badge">Grad Year: {MOCK_JD.graduationYear}</span>
            <span className="jd-badge">Skills: {MOCK_JD.mandatorySkills.join(', ')}</span>
          </div>
        </div>
      )}

      {/* Render Scoring Engine Here */}
      <div style={{ marginTop: '3rem', borderTop: '1px solid var(--border)', paddingTop: '2rem' }}>
        <div className="page-header" style={{ marginBottom: '1.5rem' }}>
          <h2>Scoring Engine Settings</h2>
          <p className="page-subtitle">Configure baseline rule-based platform weights (overridden partially by Fitment Score when active).</p>
        </div>
        <div style={{ paddingBottom: '3rem' }}>
          <ScoringConfig 
            scoringMode={scoringMode}
            onScoringModeChange={onScoringModeChange}
            customWeights={customWeights}
            onCustomWeightsChange={onCustomWeightsChange}
            onSave={onSave}
          />
        </div>
      </div>
    </div>
  );
}
