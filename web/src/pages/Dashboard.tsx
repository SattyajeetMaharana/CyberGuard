import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const quickActions = [
  {
    label: "Threat Center",
    description: "Review active security threats",
    path: "/threats",
    icon: "◈",
  },
  {
    label: "Incidents",
    description: "Manage security incidents",
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
    label: "Settings",
    description: "Manage your security preferences",
    path: "/settings",
    icon: "⚙",
  },
];

export default function Dashboard() {
  const { user } = useAuth();

  const displayName =
    user?.full_name?.trim() || "Organization User";

  const accountStatus = user?.is_active
    ? "ACTIVE"
    : "INACTIVE";

  const verificationStatus = user?.is_verified
    ? "VERIFIED"
    : "UNVERIFIED";

  return (
    <div className="dashboard-page">
      <section className="dashboard-heading">
        <div>
          <span className="dashboard-eyebrow">
            SECURITY COMMAND CENTER
          </span>

          <h1>Welcome, {displayName}</h1>

          <p>
            Monitor your organization's cybersecurity
            posture and access security analysis from one
            centralized workspace.
          </p>
        </div>

        <div className="dashboard-status-block">
          <span className="dashboard-status-indicator">
            <span />
            SESSION ACTIVE
          </span>

          <strong>Secure workspace online</strong>

          <span>
            {user?.email ?? "Authenticated user"}
          </span>
        </div>
      </section>

      <section className="dashboard-metrics">
        <article className="dashboard-metric-card">
          <div className="dashboard-metric-top">
            <span>Cyber Score</span>

            <span className="dashboard-metric-arrow">
              ↗
            </span>
          </div>

          <div className="dashboard-metric-value">
            <strong>—</strong>
            <small>/100</small>
          </div>

          <div className="dashboard-metric-bottom">
            <span>Backend score</span>

            <span>
              <strong>UNAVAILABLE</strong>
            </span>
          </div>
        </article>

        <article className="dashboard-metric-card">
          <div className="dashboard-metric-top">
            <span>Account</span>

            <span className="dashboard-metric-arrow">
              ↗
            </span>
          </div>

          <div className="dashboard-metric-value">
            <strong>01</strong>
          </div>

          <div className="dashboard-metric-bottom">
            <span>Authenticated user</span>

            <span>
              <strong>{accountStatus}</strong>
            </span>
          </div>
        </article>

        <article className="dashboard-metric-card">
          <div className="dashboard-metric-top">
            <span>Verification</span>

            <span className="dashboard-metric-arrow">
              ↗
            </span>
          </div>

          <div className="dashboard-metric-value">
            <strong>
              {user?.is_verified ? "YES" : "NO"}
            </strong>
          </div>

          <div className="dashboard-metric-bottom">
            <span>Organization account</span>

            <span>
              <strong>{verificationStatus}</strong>
            </span>
          </div>
        </article>

        <article className="dashboard-metric-card">
          <div className="dashboard-metric-top">
            <span>Security</span>

            <span className="dashboard-metric-arrow">
              ↗
            </span>
          </div>

          <div className="dashboard-metric-value">
            <strong>READY</strong>
          </div>

          <div className="dashboard-metric-bottom">
            <span>Security workspace</span>

            <span>
              <strong>ONLINE</strong>
            </span>
          </div>
        </article>
      </section>

      <section className="dashboard-command-grid">
        <article
          className="dashboard-panel dashboard-score-panel"
          id="security-context"
        >
          <div className="dashboard-panel-header">
            <div>
              <span>SECURITY CONTEXT</span>
              <h2>Current security posture</h2>
            </div>

            <span className="dashboard-panel-period">
              LIVE
            </span>
          </div>

          <div className="dashboard-score-content">
            <div className="dashboard-score-circle">
              <strong>—</strong>
              <span>API</span>
            </div>

            <div className="dashboard-score-details">
              <span>CYBER SCORE</span>

              <strong>
                Waiting for backend score
              </strong>

              <p>
                CyberGuard displays the authoritative
                security score supplied by the backend.
                The web application does not calculate or
                estimate this value.
              </p>

              <Link to="/cyber-score">
                View score analysis
                <span>↗</span>
              </Link>
            </div>
          </div>
        </article>

        <article
          className="dashboard-panel dashboard-threat-panel"
          id="security-overview"
        >
          <div className="dashboard-panel-header">
            <div>
              <span>SECURITY OVERVIEW</span>
              <h2>Security operations</h2>
            </div>

            <span className="dashboard-panel-period">
              READY
            </span>
          </div>

          <div className="dashboard-threat-content">
            <div className="dashboard-threat-total">
              <strong>03</strong>
              <span>SECURITY MODULES</span>
            </div>

            <div className="dashboard-score-details">
              <span>THREAT MANAGEMENT</span>

              <strong>
                Security modules are ready
              </strong>

              <p>
                Threat Center, incident management and
                Cyber Score modules are available through
                the security navigation.
              </p>

              <Link to="/threats">
                Open Threat Center
                <span>↗</span>
              </Link>
            </div>
          </div>
        </article>
      </section>

      <section className="dashboard-analysis-grid">
        <article className="dashboard-panel dashboard-activity-panel">
          <div className="dashboard-panel-header">
            <div>
              <span>ACCOUNT CONTEXT</span>
              <h2>Authenticated identity</h2>
            </div>

            <span className="dashboard-panel-period">
              CURRENT
            </span>
          </div>

          <div className="dashboard-activity-list">
            <div className="dashboard-activity-row">
              <span className="dashboard-activity-time">
                USER
              </span>

              <div className="dashboard-activity-event">
                <strong>{displayName}</strong>
                <span>{user?.email}</span>
              </div>

              <span className="dashboard-activity-status status-safe">
                {accountStatus}
              </span>
            </div>

            <div className="dashboard-activity-row">
              <span className="dashboard-activity-time">
                ACCOUNT
              </span>

              <div className="dashboard-activity-event">
                <strong>Verification status</strong>

                <span>
                  Backend authentication state
                </span>
              </div>

              <span className="dashboard-activity-status status-info">
                {verificationStatus}
              </span>
            </div>
          </div>
        </article>

        <article className="dashboard-panel dashboard-department-panel">
          <div className="dashboard-panel-header">
            <div>
              <span>SECURITY ACTIVITY</span>
              <h2>Recent events</h2>
            </div>

            <span className="dashboard-panel-period">
              API
            </span>
          </div>

          <div className="dashboard-department-list">
            <div className="dashboard-department-row">
              <div className="dashboard-department-name">
                <strong>Activity API</strong>

                <span>
                  No activity endpoint connected
                </span>
              </div>

              <strong className="dashboard-department-score">
                —
              </strong>
            </div>

            <div className="dashboard-department-row">
              <div className="dashboard-department-name">
                <strong>Threat data</strong>

                <span>
                  Backend integration pending
                </span>
              </div>

              <strong className="dashboard-department-score">
                —
              </strong>
            </div>

            <div className="dashboard-department-row">
              <div className="dashboard-department-name">
                <strong>Incident data</strong>

                <span>
                  Backend integration pending
                </span>
              </div>

              <strong className="dashboard-department-score">
                —
              </strong>
            </div>
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
            <Link
              className="dashboard-quick-card"
              to={action.path}
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
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}