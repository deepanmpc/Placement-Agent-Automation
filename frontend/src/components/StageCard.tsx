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

const STATUS_COLORS: Record<string, { text: string; bg: string; border: string }> = {
  completed: { text: '#10B981', bg: 'rgba(16, 185, 129, 0.06)', border: 'rgba(16, 185, 129, 0.18)' },
  active: { text: '#6366F1', bg: 'rgba(99, 102, 241, 0.06)', border: 'rgba(99, 102, 241, 0.3)' },
  pending: { text: 'var(--text-secondary)', bg: 'var(--bg-secondary)', border: 'var(--border)' },
  future: { text: 'var(--text-tertiary)', bg: 'var(--bg-secondary)', border: 'var(--border)' },
};

export default function StageCard({ stage, index }: Props) {
  const colors = STATUS_COLORS[stage.status];
  const isActive = stage.status === 'active';
  const isCompleted = stage.status === 'completed';
  const isFuture = stage.status === 'future';

  return (
    <div
      className={`stage-card stage-${stage.status}`}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1.25rem',
        padding: '1.1rem 1.25rem',
        background: 'var(--card-bg)',
        border: `1px solid ${colors.border}`,
        borderRadius: '14px',
        position: 'relative',
        boxShadow: isActive ? '0 10px 30px -10px rgba(99, 102, 241, 0.25)' : 'var(--shadow-sm)',
        transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
        opacity: isFuture ? 0.65 : 1,
      }}
    >
      {/* Icon/Number indicator */}
      <div
        style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '0.8rem',
          fontWeight: 700,
          background: isCompleted ? 'rgba(16, 185, 129, 0.12)' : colors.bg,
          color: colors.text,
          border: isCompleted ? '1px solid rgba(16, 185, 129, 0.2)' : `1px solid ${colors.border}`,
          flexShrink: 0,
        }}
      >
        {isCompleted ? '✓' : index + 1}
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
          <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
            {stage.name}
          </h3>
          <span
            style={{
              fontSize: '0.6rem',
              fontWeight: 700,
              padding: '0.15rem 0.5rem',
              borderRadius: '20px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              background: colors.bg,
              color: colors.text,
              border: `1px solid ${colors.border}`,
            }}
          >
            {STATUS_LABEL[stage.status]}
          </span>
        </div>
        <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.45 }}>
          {stage.description}
        </p>
      </div>

      {isActive && (
        <div
          className="stage-pulse"
          style={{
            position: 'absolute',
            right: '1.25rem',
            width: '8px',
            height: '8px',
            background: '#6366F1',
            borderRadius: '50%',
            boxShadow: '0 0 0 4px rgba(99, 102, 241, 0.2)',
          }}
        />
      )}
    </div>
  );
}
