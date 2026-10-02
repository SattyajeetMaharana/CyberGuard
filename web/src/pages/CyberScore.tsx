const categories = [
  {
    name: "Threat Detection",
    score: 86,
    description: "Coverage across detected security threats.",
  },
  {
    name: "Incident Response",
    score: 74,
    description: "Organization's incident handling posture.",
  },
  {
    name: "Device Security",
    score: 81,
    description: "Security visibility across managed devices.",
  },
  {
    name: "Policy Compliance",
    score: 69,
    description: "Alignment with organizational security policies.",
  },
  {
    name: "Employee Security",
    score: 78,
    description: "Security posture across organizational users.",
  },
];

const improvements = [
  "Review unresolved high-severity incidents.",
  "Strengthen organization security policies.",
  "Review devices with recent suspicious activity.",
];

export default function CyberScore() {
  return (
    <div className="organization-section">
      <header className="organization-section-header">
        <div>
          <span className="organization-section-eyebrow">
            SECURITY ANALYTICS
          </span>

          <h1>Cyber Score</h1>

          <p>
            Understand your organization's current security posture through a
            centralized cybersecurity score.
          </p>
        </div>

        <button type="button" className="button button-secondary">
          Export Report
        </button>
      </header>

      <section className="cyber-score-overview">
        <div className="cyber-score-main">
          <span className="cyber-score-label">CURRENT SCORE</span>

          <div className="cyber-score-value">
            <strong>78</strong>
            <span>/ 100</span>
          </div>

          <p>
            Overall organizational cybersecurity posture based on available
            security signals.
          </p>
        </div>

        <div className="cyber-score-indicator">
          <div className="cyber-score-ring">
            <div>
              <strong>78</strong>
              <span>SCORE</span>
            </div>
          </div>
        </div>
      </section>

      <section className="cyber-score-grid">
        <article className="organization-panel">
          <div className="organization-panel-header">
            <div>
              <span>SCORE BREAKDOWN</span>
              <h2>Security categories</h2>
            </div>

            <span className="organization-panel-meta">Current</span>
          </div>

          <div className="score-category-list">
            {categories.map((category) => (
              <div className="score-category" key={category.name}>
                <div className="score-category-header">
                  <div>
                    <strong>{category.name}</strong>
                    <span>{category.description}</span>
                  </div>

                  <b>{category.score}</b>
                </div>

                <div className="score-category-bar">
                  <span style={{ width: `${category.score}%` }} />
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="organization-panel">
          <div className="organization-panel-header">
            <div>
              <span>IMPROVEMENT AREAS</span>
              <h2>Recommended attention</h2>
            </div>
          </div>

          <div className="score-improvement-list">
            {improvements.map((item, index) => (
              <div className="score-improvement" key={item}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <p>{item}</p>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="organization-panel score-history-panel">
        <div className="organization-panel-header">
          <div>
            <span>SCORE HISTORY</span>
            <h2>Security posture over time</h2>
          </div>

          <span className="organization-panel-meta">Last 30 days</span>
        </div>

        <div className="score-history">
          <div className="score-history-line">
            <span style={{ height: "48%" }} />
            <span style={{ height: "56%" }} />
            <span style={{ height: "51%" }} />
            <span style={{ height: "64%" }} />
            <span style={{ height: "61%" }} />
            <span style={{ height: "73%" }} />
            <span style={{ height: "78%" }} />
          </div>

          <div className="score-history-labels">
            <span>Week 1</span>
            <span>Week 2</span>
            <span>Week 3</span>
            <span>Week 4</span>
          </div>
        </div>
      </section>
    </div>
  );
}