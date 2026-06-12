import type { PipelineStage } from '../types';

interface Props {
  stage: PipelineStage;
  index: number;
}

const STATUS_LABEL: Record<string, string> = {
  completed: 'Completed',
  active: 'In Progress',
  pending: 'Pending',
  future: 'Planned',
};

export default function StageCard({ stage, index }: Props) {
  return (
    <div className={`stage-card stage-${stage.status}`}>
      <div className={`stage-number stage-${stage.status}`}>
        {index + 1}
      </div>
      <div className="stage-body">
        <div className="stage-header">
          <h3 className="stage-name">{stage.name}</h3>
          <span className={`stage-badge badge-${stage.status}`}>
            {STATUS_LABEL[stage.status]}
          </span>
        </div>
        <p className="stage-desc">{stage.description}</p>
      </div>
      {stage.status === 'active' && <div className="stage-pulse" />}
    </div>
  );
}
