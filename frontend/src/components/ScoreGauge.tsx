interface Props {
  score: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
}

export default function ScoreGauge({ score, size = 80, strokeWidth = 6, label }: Props) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.min(100, Math.max(0, score)) / 100) * circumference;

  const color =
    score >= 80 ? 'var(--color-success)' : score >= 60 ? 'var(--color-warning)' : 'var(--color-danger)';

  return (
    <div className="score-gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--color-track)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>
      <div className="score-gauge-value">
        {Math.round(score)}
      </div>
      {label && <div className="score-gauge-label">{label}</div>}
    </div>
  );
}
