import { PIPELINE_STAGES, MOCK_JD } from '../data/mockData';
import StageCard from '../components/StageCard';

export default function Dashboard() {
  return (
    <div className="page">
      <div className="page-header">
        <h1>Ranking Pipeline</h1>
        <p className="page-subtitle">
          Current phase: <strong>Phase 1</strong> &mdash; Student Intelligence Platform
        </p>
      </div>

      <div className="jd-summary">
        <div className="jd-summary-header">
          <h3>{MOCK_JD.title}</h3>
          <span className="company">{MOCK_JD.company}</span>
        </div>
        <div className="jd-summary-body">
          <p>{MOCK_JD.description}</p>
          <div className="jd-badges">
            <span className="jd-badge">Min CGPA: {MOCK_JD.minCGPA}</span>
            <span className="jd-badge">Branches: {MOCK_JD.allowedBranches.join(', ')}</span>
            <span className="jd-badge">Grad Year: {MOCK_JD.graduationYear}</span>
            <span className="jd-badge">Mandatory Skills: {MOCK_JD.mandatorySkills.join(', ')}</span>
          </div>
        </div>
      </div>

      <div className="pipeline-flow">
        {PIPELINE_STAGES.map((stage, idx) => (
          <div key={stage.id} className="pipeline-stage-wrapper">
            <StageCard stage={stage} index={idx} />
            {idx < PIPELINE_STAGES.length - 1 && (
              <div className={`pipeline-connector connector-${stage.status}`} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
