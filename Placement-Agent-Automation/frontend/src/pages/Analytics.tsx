import { MOCK_RANKINGS } from '../data/mockData';

export default function Analytics() {
  const scores = MOCK_RANKINGS.map((r) => r.scores.finalScore);
  const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  const maxScore = Math.max(...scores);
  const minScore = Math.min(...scores);

  const ruleScores = MOCK_RANKINGS.map((r) => r.scores.ruleScore);
  const semScores = MOCK_RANKINGS.map((r) => r.scores.semanticScore);
  const avgRule = Math.round(ruleScores.reduce((a, b) => a + b, 0) / ruleScores.length);
  const avgSem = Math.round(semScores.reduce((a, b) => a + b, 0) / semScores.length);

  const bucket3 = scores.filter((s) => s >= 80).length;
  const bucket2 = scores.filter((s) => s >= 60 && s < 80).length;
  const bucket1 = scores.filter((s) => s < 60).length;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Analytics</h1>
        <p className="page-subtitle">Candidate pool statistics and score distribution</p>
      </div>

      <div className="analytics-grid">
        <div className="analytics-card">
          <h3>Score Overview</h3>
          <div className="analytics-stats">
            <div className="analytics-stat">
              <span className="analytics-value">{avgScore}</span>
              <span className="analytics-label">Average Final Score</span>
            </div>
            <div className="analytics-stat">
              <span className="analytics-value">{maxScore}</span>
              <span className="analytics-label">Highest Score</span>
            </div>
            <div className="analytics-stat">
              <span className="analytics-value">{minScore}</span>
              <span className="analytics-label">Lowest Score</span>
            </div>
            <div className="analytics-stat">
              <span className="analytics-value">{MOCK_RANKINGS.length}</span>
              <span className="analytics-label">Eligible Candidates</span>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <h3>Score Distribution</h3>
          <div className="distribution-bars">
            <div className="dist-bar-wrapper">
              <span className="dist-label">80-100</span>
              <div className="dist-track">
                <div
                  className="dist-bar color-green"
                  style={{ width: `${(bucket3 / MOCK_RANKINGS.length) * 100}%` }}
                />
              </div>
              <span className="dist-count">{bucket3}</span>
            </div>
            <div className="dist-bar-wrapper">
              <span className="dist-label">60-79</span>
              <div className="dist-track">
                <div
                  className="dist-bar color-yellow"
                  style={{ width: `${(bucket2 / MOCK_RANKINGS.length) * 100}%` }}
                />
              </div>
              <span className="dist-count">{bucket2}</span>
            </div>
            <div className="dist-bar-wrapper">
              <span className="dist-label">0-59</span>
              <div className="dist-track">
                <div
                  className="dist-bar color-red"
                  style={{ width: `${(bucket1 / MOCK_RANKINGS.length) * 100}%` }}
                />
              </div>
              <span className="dist-count">{bucket1}</span>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <h3>Component Scores</h3>
          <div className="analytics-stats">
            <div className="analytics-stat">
              <span className="analytics-value">{avgRule}</span>
              <span className="analytics-label">Avg Rule Score</span>
            </div>
            <div className="analytics-stat">
              <span className="analytics-value">{avgSem}</span>
              <span className="analytics-label">Avg Semantic Score</span>
            </div>
            <div className="analytics-stat">
              <span className="analytics-value">0</span>
              <span className="analytics-label">Avg ML Score</span>
            </div>
            <div className="analytics-stat">
              <span className="analytics-value">60/40</span>
              <span className="analytics-label">Weight Config (Rule/Sem)</span>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <h3>Top Candidate</h3>
          <div className="top-candidate">
            <div className="top-candidate-rank">{MOCK_RANKINGS[0].rank}</div>
            <div>
              <div className="top-candidate-name">{MOCK_RANKINGS[0].student.personalInfo.name}</div>
              <div className="top-candidate-score">Score: {MOCK_RANKINGS[0].scores.finalScore}</div>
              <div className="top-candidate-meta">
                {MOCK_RANKINGS[0].student.education.institution} &middot; CGPA {MOCK_RANKINGS[0].student.education.cgpa}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
