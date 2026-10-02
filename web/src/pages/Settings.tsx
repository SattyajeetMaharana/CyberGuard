import { useState } from "react";

export default function Settings() {
  const [notifications, setNotifications] = useState(true);
  const [threatAlerts, setThreatAlerts] = useState(true);
  const [weeklyReport, setWeeklyReport] = useState(false);

  return (
    <div className="organization-section">
      <header className="organization-section-header">
        <div>
          <span className="organization-section-eyebrow">
            ORGANIZATION ADMINISTRATION
          </span>

          <h1>Settings</h1>

          <p>
            Manage organization preferences, notifications, and administrative
            configuration.
          </p>
        </div>
      </header>

      <div className="settings-layout">
        <section className="organization-panel settings-panel">
          <div className="organization-panel-header">
            <div>
              <span>ORGANIZATION</span>
              <h2>Organization settings</h2>
            </div>
          </div>

          <div className="settings-form">
            <div className="settings-field">
              <label htmlFor="organization-name">
                Organization name
              </label>
              <input
                id="organization-name"
                type="text"
                defaultValue="CyberGuard Organization"
              />
            </div>

            <div className="settings-field">
              <label htmlFor="organization-email">
                Organization email
              </label>
              <input
                id="organization-email"
                type="email"
                defaultValue="admin@organization.com"
              />
            </div>

            <div className="settings-field">
              <label htmlFor="organization-id">
                Organization ID
              </label>
              <input
                id="organization-id"
                type="text"
                defaultValue="ORG-001"
                disabled
              />
            </div>

            <div className="settings-actions">
              <button type="button" className="button button-primary">
                Save Changes
              </button>
            </div>
          </div>
        </section>

        <section className="organization-panel settings-panel">
          <div className="organization-panel-header">
            <div>
              <span>NOTIFICATIONS</span>
              <h2>Notification preferences</h2>
            </div>
          </div>

          <div className="settings-options">
            <label className="settings-option">
              <div>
                <strong>Security notifications</strong>
                <span>
                  Receive important organization security notifications.
                </span>
              </div>

              <input
                type="checkbox"
                checked={notifications}
                onChange={() => setNotifications((value) => !value)}
              />

              <span className="settings-switch" />
            </label>

            <label className="settings-option">
              <div>
                <strong>Threat alerts</strong>
                <span>
                  Receive alerts when significant threats are detected.
                </span>
              </div>

              <input
                type="checkbox"
                checked={threatAlerts}
                onChange={() => setThreatAlerts((value) => !value)}
              />

              <span className="settings-switch" />
            </label>

            <label className="settings-option">
              <div>
                <strong>Weekly security report</strong>
                <span>
                  Receive a periodic summary of your organization's security
                  activity.
                </span>
              </div>

              <input
                type="checkbox"
                checked={weeklyReport}
                onChange={() => setWeeklyReport((value) => !value)}
              />

              <span className="settings-switch" />
            </label>
          </div>
        </section>

        <section className="organization-panel settings-panel">
          <div className="organization-panel-header">
            <div>
              <span>ADMINISTRATION</span>
              <h2>Administrative access</h2>
            </div>
          </div>

          <div className="settings-admin-list">
            <div className="settings-admin-row">
              <div>
                <strong>Organization administrators</strong>
                <span>Manage administrators with portal access.</span>
              </div>

              <button type="button" className="settings-secondary-button">
                Manage
              </button>
            </div>

            <div className="settings-admin-row">
              <div>
                <strong>Access control</strong>
                <span>Configure organization access permissions.</span>
              </div>

              <button type="button" className="settings-secondary-button">
                Configure
              </button>
            </div>

            <div className="settings-admin-row">
              <div>
                <strong>Audit activity</strong>
                <span>Review administrative activity and changes.</span>
              </div>

              <button type="button" className="settings-secondary-button">
                View
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}