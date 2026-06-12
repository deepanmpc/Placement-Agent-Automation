import type { ScoreBreakdown as SB } from '../types';

interface Props {
  scores: SB;
}

function BreakdownTable({ data, title }: { data: Record<string, number>; title: string }) {
  const entries = Object.entries(data);
  const total = entries.reduce((s, [, v]) => s + v, 0);
  return (
    <div className="breakdown-section">
      <h4>{title}</h4>
      <div className="breakdown-table">
        {entries.map(([key, val]) => (
          <div key={key} className="breakdown-row">
            <span className="breakdown-label">{key}</span>
            <div className="breakdown-bar-track">
              <div
                className="breakdown-bar"
                style={{ width: `${Math.min(100, val)}%` }}
              />
            </div>
            <span className="breakdown-value">{Math.round(val)}</span>
          </div>
        ))}
        <div className="breakdown-row breakdown-total">
          <span className="breakdown-label">Total</span>
          <div className="breakdown-bar-track">
            <div className="breakdown-bar total" style={{ width: `${Math.min(100, total)}%` }} />
          </div>
          <span className="breakdown-value">{Math.round(total)}</span>
        </div>
      </div>
    </div>
  );
}

export default function ScoreBreakdown({ scores }: Props) {
  return (
    <div className="score-breakdown">
      <div className="breakdown-formula">
        <strong>Formula:</strong> Final = {Math.round(scores.w1 * 100)}% x Rule +
        {' '}{Math.round(scores.w2 * 100)}% x Semantic +
        {' '}{Math.round(scores.w3 * 100)}% x ML
      </div>

      <div className="breakdown-grid">
        <BreakdownTable data={scores.ruleScoreBreakdown} title="Rule Score Breakdown" />
        <BreakdownTable data={scores.codingScoreBreakdown} title="Coding Score Breakdown" />
        <BreakdownTable data={scores.githubScoreBreakdown} title="GitHub Score Breakdown" />
        <BreakdownTable data={scores.semanticScoreBreakdown} title="Semantic Score Breakdown" />
      </div>

      <div className="breakdown-explanation">
        <h4>Explanation</h4>
        <p>{scores.explanation}</p>
      </div>
    </div>
  );
}
