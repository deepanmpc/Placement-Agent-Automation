import type { PageView } from '../types';
import { MOCK_RANKINGS } from '../data/mockData';
import CandidateCard from '../components/CandidateCard';

interface Props {
  onSelect: (studentId: string) => void;
  onNavigate: (page: PageView) => void;
}

export default function Candidates({ onSelect, onNavigate }: Props) {
  const eligible = MOCK_RANKINGS;
  const ineligibleCount = 2;
  const totalCandidates = eligible.length + ineligibleCount;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Ranked Candidates</h1>
        <p className="page-subtitle">
          {eligible.length} eligible &middot; {ineligibleCount} filtered out &middot; {totalCandidates} total
        </p>
      </div>

      <div className="ranking-summary">
        <div className="summary-stat">
          <span className="stat-value">{totalCandidates}</span>
          <span className="stat-label">Total Students</span>
        </div>
        <div className="summary-stat">
          <span className="stat-value">{eligible.length}</span>
          <span className="stat-label">Eligible</span>
        </div>
        <div className="summary-stat">
          <span className="stat-value">{ineligibleCount}</span>
          <span className="stat-label">Filtered Out</span>
        </div>
        <div className="summary-stat">
          <span className="stat-value">{Math.round(eligible.reduce((s, c) => s + c.scores.finalScore, 0) / eligible.length)}</span>
          <span className="stat-label">Avg Score</span>
        </div>
      </div>

      <div className="candidates-list">
        {eligible.map((c) => (
          <CandidateCard
            key={c.student.id}
            candidate={c}
            onClick={() => {
              onSelect(c.student.id);
              onNavigate('student');
            }}
          />
        ))}
      </div>
    </div>
  );
}
