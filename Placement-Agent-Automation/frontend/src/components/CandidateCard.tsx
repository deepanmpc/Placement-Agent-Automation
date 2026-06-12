import type { CandidateRanking } from '../types';
import ScoreGauge from './ScoreGauge';

interface Props {
  candidate: CandidateRanking;
  onClick: () => void;
}

export default function CandidateCard({ candidate, onClick }: Props) {
  const { student, scores } = candidate;

  return (
    <div className="candidate-card" onClick={onClick}>
      <div className="candidate-rank">{candidate.rank}</div>
      <div className="candidate-info">
        <h3 className="candidate-name">{student.personalInfo.name}</h3>
        <p className="candidate-meta">
          {student.education.institution} &middot; {student.education.specialization} &middot;
          CGPA {student.education.cgpa}
        </p>
        <div className="candidate-tags">
          {scores.matchedSkills.slice(0, 4).map((s) => (
            <span key={s} className="tag tag-match">{s}</span>
          ))}
          {scores.missingSkills.length > 0 && (
            <span className="tag tag-miss">-{scores.missingSkills[0]}</span>
          )}
        </div>
      </div>
      <div className="candidate-scores">
        <ScoreGauge score={scores.finalScore} size={64} strokeWidth={5} label="Final" />
        <ScoreGauge score={scores.ruleScore} size={48} strokeWidth={4} label="Rule" />
        <ScoreGauge score={scores.semanticScore} size={48} strokeWidth={4} label="Sem" />
      </div>
    </div>
  );
}
