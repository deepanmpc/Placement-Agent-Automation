import { useState } from 'react';
import type { JDRequirements } from '../types';
import { MOCK_JD } from '../data/mockData';

interface Props {
  onParsed: (jd: JDRequirements) => void;
}

export default function JDInput({ onParsed }: Props) {
  const [jdText, setJdText] = useState('');
  const [showMock, setShowMock] = useState(false);

  const handleParse = () => {
    if (!jdText.trim()) return;
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
    <div className="page">
      <div className="page-header">
        <h1>Job Description</h1>
        <p className="page-subtitle">
          Paste a job description to extract hiring requirements
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
            Parse JD
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
    </div>
  );
}
