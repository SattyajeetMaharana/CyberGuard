const incidents = [
  {
    id: "INC-001",
    title: "Suspicious phishing activity",
    source: "Phishing Detection",
    severity: "Critical",
    status: "Investigating",
    updated: "10:42 AM",
  },
  {
    id: "INC-002",
    title: "Multiple suspicious QR scans",
    source: "QR Detection",
    severity: "High",
    status: "Open",
    updated: "09:36 AM",
  },
  {
    id: "INC-003",
    title: "Potential malicious file",
    source: "File Detection",
    severity: "High",
    status: "Contained",
    updated: "09:12 AM",
  },
  {
    id: "INC-004",
    title: "Unusual device activity",
    source: "Device Monitoring",
    severity: "Medium",
    status: "Resolved",
    updated: "08:48 AM",
  },
];

export default function Incidents() {
  return (
    <div className="organization-section">
      <header className="organization-section-header">
        <div>
          <span className="organization-section-eyebrow">
            INCIDENT RESPONSE
          </span>

          <h1>Incidents</h1>

          <p>
            Review, track, and manage security incidents detected across your
            organization.
          </p>
        </div>

        <button type="button" className="button button-secondary">
          Export Report
        </button>
      </header>

      <section className="incident-stat-grid">
        <article className="organization-stat-card">
          <span>Open</span>
          <strong>04</strong>
          <p>Active incidents</p>
        </article>

        <article className="organization-stat-card">
          <span>Investigating</span>
          <strong>02</strong>
          <p>Under investigation</p>
        </article>

        <article className="organization-stat-card">
          <span>Contained</span>
          <strong>01</strong>
          <p>Threat contained</p>
        </article>

        <article className="organization-stat-card">
          <span>Resolved</span>
          <strong>18</strong>
          <p>Resolved incidents</p>
        </article>
      </section>

      <section className="organization-panel incident-panel">
        <div className="organization-panel-header">
          <div>
            <span>INCIDENT QUEUE</span>
            <h2>Recent incidents</h2>
          </div>

          <span className="organization-panel-meta">Latest</span>
        </div>

        <div className="incident-list">
          {incidents.map((incident) => (
            <article className="incident-row" key={incident.id}>
              <div className="incident-id">{incident.id}</div>

              <div className="incident-main">
                <strong>{incident.title}</strong>
                <span>{incident.source}</span>
              </div>

              <span
                className={`incident-severity incident-${incident.severity.toLowerCase()}`}
              >
                {incident.severity}
              </span>

              <span
                className={`incident-status incident-status-${incident.status.toLowerCase()}`}
              >
                {incident.status}
              </span>

              <span className="incident-updated">
                {incident.updated}
              </span>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}