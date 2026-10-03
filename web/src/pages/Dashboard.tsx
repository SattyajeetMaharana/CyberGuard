const metrics = [
  {
    label: "Cyber Score",
    value: "78",
    suffix: "/100",
    detail: "Current security posture",
    trend: "+4.2%",
    trendLabel: "vs last week",
  },
  {
    label: "Active Threats",
    value: "12",
    suffix: "",
    detail: "Threats requiring attention",
    trend: "03",
    trendLabel: "high priority",
  },
  {
    label: "Open Incidents",
    value: "04",
    suffix: "",
    detail: "Incidents under response",
    trend: "01",
    trendLabel: "critical",
  },
  {
    label: "Protected Devices",
    value: "128",
    suffix: "",
    detail: "Managed organization devices",
    trend: "96%",
    trendLabel: "coverage",
  },
];

const threatLevels = [
  {
    label: "Critical",
    value: 2,
    percentage: 17,
  },
  {
    label: "High",
    value: 4,
    percentage: 33,
  },
  {
    label: "Medium",
    value: 6,
    percentage: 50,
  },
];

const departments = [
  {
    name: "Engineering",
    score: 84,
    status: "Stable",
  },
  {
    name: "Operations",
    score: 76,
    status: "Monitor",
  },
  {
    name: "Finance",
    score: 69,
    status: "Attention",
  },
  {
    name: "Human Resources",
    score: 88,
    status: "Stable",
  },
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

const quickActions = [
  {
    label: "Threat Center",
    description: "Review active threats",
    path: "/threats",
    icon: "◈",
  },
  {
    label: "Incidents",
    description: "Manage open incidents",
    path: "/incidents",
    icon: "◇",
  },
  {
    label: "Cyber Score",
    description: "View security analytics",
    path: "/cyber-score",
    icon: "◉",
  },
  {
    label: "Devices",
    description: "Monitor organization devices",
    path: "/devices",
    icon: "▣",
  },
];

export default function Dashboard() {
  return (
    <div className="dashboard-page">
      <section className="dashboard-heading">
        <div>
          <span className="dashboard-eyebrow">
            SECURITY COMMAND CENTER
          </span>

          <h1>Organization Overview</h1>

          <p>
            Monitor your organization's cybersecurity posture, active threats,
            incidents, and security activity from one centralized workspace.
          </p>
        </div>

        <div className="dashboard-status-block">
          <span className="dashboard-status-indicator">
            <span />
            MONITORING ACTIVE
          </span>

          <strong>Security operations online</strong>

          <span>Last updated just now</span>
        </div>
      </section>

      <section className="dashboard-metrics">
        {metrics.map((metric) => (
          <article
            className="dashboard-metric-card"
            key={metric.label}
          >
            <div className="dashboard-metric-top">
              <span>{metric.label}</span>

              <span className="dashboard-metric-arrow">
                ↗
              </span>
            </div>

            <div className="dashboard-metric-value">
              <strong>{metric.value}</strong>

              {metric.suffix && (
                <small>{metric.suffix}</small>
              )}
            </div>

            <div className="dashboard-metric-bottom">
              <span>{metric.detail}</span>

              <span>
                <strong>{metric.trend}</strong>{" "}
                {metric.trendLabel}
              </span>
            </div>
          </article>
        ))}
      </section>

      <section className="dashboard-command-grid">
        <article className="dashboard-panel dashboard-threat-panel">
          <div className="dashboard-panel-header">
            <div>
              <span>THREAT CENTER</span>
              <h2>Threat distribution</h2>
            </div>

            <span className="dashboard-panel-period">
              TODAY
            </span>
          </div>

          <div className="dashboard-threat-content">
            <div className="dashboard-threat-total">
              <strong>12</strong>
              <span>ACTIVE THREATS</span>
            </div>

            <div className="dashboard-threat-levels">
              {threatLevels.map((threat) => (
                <div
                  className="dashboard-threat-level"
                  key={threat.label}
                >
                  <div className="dashboard-threat-level-heading">
                    <span>{threat.label}</span>
                    <strong>{threat.value}</strong>
                  </div>

                  <div className="dashboard-threat-bar">
                    <span
                      style={{
                        width: `${threat.percentage}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </article>

        <article className="dashboard-panel dashboard-score-panel">
          <div className="dashboard-panel-header">
            <div>
              <span>CYBER SCORE</span>
              <h2>Security posture</h2>
            </div>

            <span className="dashboard-panel-period">
              / 100
            </span>
          </div>

          <div className="dashboard-score-content">
            <div className="dashboard-score-circle">
              <strong>78</strong>
              <span>SECURE</span>
            </div>

            <div className="dashboard-score-details">
              <span>CURRENT SCORE</span>

              <strong>Good security posture</strong>

              <p>
                Your organization's security posture is being monitored
                across available security signals.
              </p>

              <a href="/cyber-score">
                View full analysis
                <span>↗</span>
              </a>
            </div>
          </div>
        </article>
      </section>

      <section className="dashboard-analysis-grid">
        <article className="dashboard-panel dashboard-department-panel">
          <div className="dashboard-panel-header">
            <div>
              <span>ORGANIZATION RISK</span>
              <h2>Department posture</h2>
            </div>

            <span className="dashboard-panel-period">
              04 UNITS
            </span>
          </div>

          <div className="dashboard-department-list">
            {departments.map((department) => (
              <div
                className="dashboard-department-row"
                key={department.name}
              >
                <div className="dashboard-department-name">
                  <strong>{department.name}</strong>
                  <span>{department.status}</span>
                </div>

                <div className="dashboard-department-bar">
                  <span
                    style={{
                      width: `${department.score}%`,
                    }}
                  />
                </div>

                <strong className="dashboard-department-score">
                  {department.score}
                </strong>
              </div>
            ))}
          </div>
        </article>

        <article className="dashboard-panel dashboard-activity-panel">
          <div className="dashboard-panel-header">
            <div>
              <span>SECURITY ACTIVITY</span>
              <h2>Recent events</h2>
            </div>

            <span className="dashboard-panel-period">
              LATEST
            </span>
          </div>

          <div className="dashboard-activity-list">
            {activity.map((item) => (
              <div
                className="dashboard-activity-row"
                key={`${item.time}-${item.event}`}
              >
                <span className="dashboard-activity-time">
                  {item.time}
                </span>

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
        </article>
      </section>

      <section className="dashboard-quick-section">
        <div className="dashboard-section-heading">
          <div>
            <span className="dashboard-eyebrow">
              QUICK ACCESS
            </span>

            <h2>Security operations</h2>
          </div>

          <span>/ 04</span>
        </div>

        <div className="dashboard-quick-grid">
          {quickActions.map((action) => (
            <a
              className="dashboard-quick-card"
              href={action.path}
              key={action.path}
            >
              <span className="dashboard-quick-icon">
                {action.icon}
              </span>

              <div>
                <strong>{action.label}</strong>
                <span>{action.description}</span>
              </div>

              <span
                className="dashboard-quick-arrow"
                aria-hidden="true"
              >
                ↗
              </span>
            </a>
          ))}
        </div>
      </section>
    </div>
  );
}