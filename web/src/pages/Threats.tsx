const threats = [
  {
    id: "THR-001",
    type: "Phishing URL",
    source: "Web Analysis",
    severity: "Critical",
    time: "10:42 AM",
  },
  {
    id: "THR-002",
    type: "Suspicious QR Code",
    source: "QR Analysis",
    severity: "High",
    time: "09:36 AM",
  },
  {
    id: "THR-003",
    type: "Malicious File",
    source: "File Analysis",
    severity: "High",
    time: "09:12 AM",
  },
  {
    id: "THR-004",
    type: "Suspicious Activity",
    source: "Behavior Analysis",
    severity: "Medium",
    time: "08:48 AM",
  },
];

export default function Threats() {
  return (
    <div className="organization-section">
      <header className="organization-section-header">
        <div>
          <span className="organization-section-eyebrow">
            SECURITY MONITORING
          </span>

          <h1>Threat Center</h1>

          <p>
            Monitor detected threats and review security events across your
            organization.
          </p>
        </div>

        <button type="button" className="button button-secondary">
          Export Report
        </button>
      </header>

      <section className="threat-stat-grid">
        <article className="organization-stat-card">
          <span>Total Threats</span>
          <strong>12</strong>
          <p>Detected today</p>
        </article>

        <article className="organization-stat-card">
          <span>Critical</span>
          <strong>02</strong>
          <p>Immediate attention</p>
        </article>

        <article className="organization-stat-card">
          <span>High</span>
          <strong>04</strong>
          <p>Requires review</p>
        </article>

        <article className="organization-stat-card">
          <span>Resolved</span>
          <strong>08</strong>
          <p>Handled threats</p>
        </article>
      </section>

      <section className="organization-panel threat-table-panel">
        <div className="organization-panel-header">
          <div>
            <span>DETECTED EVENTS</span>
            <h2>Recent threats</h2>
          </div>

          <span className="organization-panel-meta">Today</span>
        </div>

        <div className="threat-list">
          {threats.map((threat) => (
            <article className="threat-row" key={threat.id}>
              <div className="threat-id">{threat.id}</div>

              <div className="threat-main">
                <strong>{threat.type}</strong>
                <span>{threat.source}</span>
              </div>

              <span
                className={`threat-severity threat-${threat.severity.toLowerCase()}`}
              >
                {threat.severity}
              </span>

              <span className="threat-time">{threat.time}</span>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}