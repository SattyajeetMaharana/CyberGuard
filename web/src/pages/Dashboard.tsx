const metrics = [
  {
    label: "Cyber Score",
    value: "78",
    suffix: "/100",
    detail: "Current security posture",
  },
  {
    label: "Active Threats",
    value: "12",
    suffix: "",
    detail: "Requires attention",
  },
  {
    label: "Incidents",
    value: "04",
    suffix: "",
    detail: "Open incidents",
  },
  {
    label: "Protected Devices",
    value: "128",
    suffix: "",
    detail: "Organization devices",
  },
];

const threatSummary = [
  { label: "Critical", value: 2 },
  { label: "High", value: 4 },
  { label: "Medium", value: 6 },
];

const activity = [
  {
    time: "10:42 AM",
    event: "Suspicious URL detected",
    source: "Web Analysis",
    status: "High",
  },
  {
    time: "09:18 AM",
    event: "New device registered",
    source: "Device Monitoring",
    status: "Safe",
  },
  {
    time: "08:51 AM",
    event: "Security policy updated",
    source: "Organization",
    status: "Info",
  },
  {
    time: "08:24 AM",
    event: "Potential phishing attempt",
    source: "Threat Detection",
    status: "Critical",
  },
];

export default function Dashboard() {
  return (
    <div className="dashboard-page">
      <section className="dashboard-heading">
        <div>
          <span className="dashboard-eyebrow">OVERVIEW</span>

          <h1>Organization Dashboard</h1>

          <p>
            Monitor your organization's security posture and recent activity
            from one centralized workspace.
          </p>
        </div>

        <div className="dashboard-date">
          <span>SECURITY STATUS</span>
          <strong>Monitoring Active</strong>
        </div>
      </section>

      <section className="dashboard-metrics">
        {metrics.map((metric) => (
          <article className="dashboard-metric-card" key={metric.label}>
            <span>{metric.label}</span>

            <div className="dashboard-metric-value">
              <strong>{metric.value}</strong>
              {metric.suffix && <small>{metric.suffix}</small>}
            </div>

            <p>{metric.detail}</p>
          </article>
        ))}
      </section>

      <section className="dashboard-main-grid">
        <article className="dashboard-panel">
          <div className="dashboard-panel-header">
            <div>
              <span>THREAT OVERVIEW</span>
              <h2>Current threats</h2>
            </div>

            <span className="dashboard-panel-period">Today</span>
          </div>

          <div className="threat-summary">
            {threatSummary.map((threat) => (
              <div className="threat-summary-item" key={threat.label}>
                <div>
                  <span>{threat.label}</span>
                  <strong>{threat.value}</strong>
                </div>

                <div className="threat-summary-bar">
                  <span
                    style={{
                      width: `${Math.min(threat.value * 10, 100)}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="dashboard-panel dashboard-score-panel">
          <div className="dashboard-panel-header">
            <div>
              <span>CYBER SCORE</span>
              <h2>Security posture</h2>
            </div>
          </div>

          <div className="dashboard-score">
            <div className="dashboard-score-circle">
              <strong>78</strong>
              <span>/ 100</span>
            </div>

            <div className="dashboard-score-info">
              <strong>Current Score</strong>
              <p>
                Your organization's security posture is being monitored across
                available security signals.
              </p>
            </div>
          </div>
        </article>
      </section>

      <section className="dashboard-panel dashboard-activity-panel">
        <div className="dashboard-panel-header">
          <div>
            <span>RECENT ACTIVITY</span>
            <h2>Security events</h2>
          </div>

          <span className="dashboard-panel-period">Latest</span>
        </div>

        <div className="dashboard-activity-list">
          {activity.map((item) => (
            <div className="dashboard-activity-row" key={`${item.time}-${item.event}`}>
              <span className="dashboard-activity-time">{item.time}</span>

              <div className="dashboard-activity-event">
                <strong>{item.event}</strong>
                <span>{item.source}</span>
              </div>

              <span
                className={`dashboard-activity-status status-${item.status.toLowerCase()}`}
              >
                {item.status}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}