import { useState, type CSSProperties } from "react";

interface Device {
  name: string;
  employee: string;
  type: "Laptop" | "Desktop";
  os: string;
  lastActive: string;
  score: number;
  status: "Protected" | "At Risk" | "Review" | "Offline";
}

interface LoginEvent {
  employee: string;
  device: string;
  location: string;
  time: string;
  status: "Successful" | "Review";
  type: "Web" | "Desktop";
  ip: string;
  detail: string;
}

const devices: Device[] = [
  {
    name: "Engineering-LT-042",
    employee: "Arjun Sharma",
    type: "Laptop",
    os: "Windows 11",
    lastActive: "2 min ago",
    score: 94,
    status: "Protected",
  },
  {
    name: "Operations-WS-018",
    employee: "Priya Das",
    type: "Desktop",
    os: "Windows 11",
    lastActive: "8 min ago",
    score: 88,
    status: "Protected",
  },
  {
    name: "Finance-LT-011",
    employee: "Rahul Mehta",
    type: "Laptop",
    os: "Windows 10",
    lastActive: "21 min ago",
    score: 61,
    status: "At Risk",
  },
  {
    name: "HR-LT-007",
    employee: "Ananya Patel",
    type: "Laptop",
    os: "Windows 11",
    lastActive: "34 min ago",
    score: 91,
    status: "Protected",
  },
  {
    name: "Engineering-LT-039",
    employee: "Vikram Singh",
    type: "Laptop",
    os: "Windows 11",
    lastActive: "1 hr ago",
    score: 73,
    status: "Review",
  },
];

const loginEvents: LoginEvent[] = [
  {
    employee: "Arjun Sharma",
    device: "Engineering-LT-042",
    location: "Bengaluru, IN",
    time: "2 min ago",
    status: "Successful",
    type: "Desktop",
    ip: "10.24.18.42",
    detail: "Known device · Verified session",
  },
  {
    employee: "Priya Das",
    device: "Operations-WS-018",
    location: "Mumbai, IN",
    time: "8 min ago",
    status: "Successful",
    type: "Web",
    ip: "10.24.21.18",
    detail: "Known device · Verified session",
  },
  {
    employee: "Rahul Mehta",
    device: "Finance-LT-011",
    location: "Delhi, IN",
    time: "21 min ago",
    status: "Review",
    type: "Desktop",
    ip: "10.24.09.11",
    detail: "Device posture requires review",
  },
  {
    employee: "Ananya Patel",
    device: "HR-LT-007",
    location: "Hyderabad, IN",
    time: "34 min ago",
    status: "Successful",
    type: "Web",
    ip: "10.24.31.07",
    detail: "Known device · Verified session",
  },
];

const riskDistribution = [
  {
    label: "Excellent",
    range: "80–100",
    count: devices.filter((device) => device.score >= 80).length,
  },
  {
    label: "Good",
    range: "60–79",
    count: devices.filter(
      (device) => device.score >= 60 && device.score < 80,
    ).length,
  },
  {
    label: "Needs Review",
    range: "40–59",
    count: devices.filter(
      (device) => device.score >= 40 && device.score < 60,
    ).length,
  },
  {
    label: "Critical",
    range: "0–39",
    count: devices.filter((device) => device.score < 40).length,
  },
];

const platformDistribution = [
  {
    label: "Windows 11",
    count: devices.filter((device) => device.os === "Windows 11").length,
  },
  {
    label: "Windows 10",
    count: devices.filter((device) => device.os === "Windows 10").length,
  },
];

const statusDistribution = [
  {
    label: "Protected",
    count: devices.filter((device) => device.status === "Protected").length,
  },
  {
    label: "Review",
    count: devices.filter((device) => device.status === "Review").length,
  },
  {
    label: "At Risk",
    count: devices.filter((device) => device.status === "At Risk").length,
  },
  {
    label: "Offline",
    count: devices.filter((device) => device.status === "Offline").length,
  },
];

export default function Devices() {
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
  const [selectedLogin, setSelectedLogin] = useState<LoginEvent | null>(null);
  const [showRegisterPanel, setShowRegisterPanel] = useState(false);

  const averageScore = Math.round(
    devices.reduce((total, device) => total + device.score, 0) /
      devices.length,
  );

  const protectedCount = devices.filter(
    (device) => device.status === "Protected",
  ).length;

  const reviewCount = devices.filter(
    (device) => device.status === "Review",
  ).length;

  const atRiskCount = devices.filter(
    (device) => device.status === "At Risk",
  ).length;

  const offlineCount = devices.filter(
    (device) => device.status === "Offline",
  ).length;

  const successfulLogins = loginEvents.filter(
    (event) => event.status === "Successful",
  ).length;

  const reviewLogins = loginEvents.filter(
    (event) => event.status === "Review",
  ).length;

  const lowestRiskDevices = [...devices]
    .sort((first, second) => first.score - second.score)
    .slice(0, 3);

  const closeOverlays = () => {
    setSelectedDevice(null);
    setSelectedLogin(null);
    setShowRegisterPanel(false);
  };

  return (
    <div className="devices-page organization-section">
      <header className="organization-section-header devices-header">
        <div>
          <span className="organization-section-eyebrow">
            SECURITY OPERATIONS
          </span>

          <h1>Devices</h1>

          <p>
            Monitor registered devices, review endpoint security posture, and
            maintain visibility across the organization.
          </p>
        </div>

        <button
          type="button"
          className="button button-primary"
          onClick={() => setShowRegisterPanel(true)}
        >
          <span>Register Device</span>
          <span aria-hidden="true">+</span>
        </button>
      </header>

      <section className="device-stat-grid">
        <article className="organization-stat-card">
          <span>Total Devices</span>
          <strong>93</strong>
          <p>Registered devices</p>
        </article>

        <article className="organization-stat-card">
          <span>Protected</span>
          <strong>76</strong>
          <p>Healthy devices</p>
        </article>

        <article className="organization-stat-card">
          <span>At Risk</span>
          <strong>09</strong>
          <p>Require attention</p>
        </article>

        <article className="organization-stat-card">
          <span>Offline</span>
          <strong>08</strong>
          <p>Currently inactive</p>
        </article>
      </section>

      <section className="devices-risk-analytics">
        <article className="organization-panel device-risk-analysis-panel">
          <div className="organization-panel-header">
            <div>
              <span>ENDPOINT RISK ANALYTICS</span>
              <h2>Security score distribution</h2>
            </div>

            <span className="organization-panel-meta">
              {averageScore} AVG
            </span>
          </div>

          <div className="device-risk-analysis-content">
            <div className="device-risk-score-focus">
              <span>AVERAGE DEVICE SCORE</span>

              <div className="device-risk-score-number">
                <strong>{averageScore}</strong>
                <span>/ 100</span>
              </div>

              <div className="device-risk-score-track">
                <span style={{ width: `${averageScore}%` }} />
              </div>

              <div className="device-risk-score-labels">
                <span>0</span>
                <span>50</span>
                <span>100</span>
              </div>
            </div>

            <div className="device-risk-distribution">
              {riskDistribution.map((item) => (
                <div
                  className="device-risk-distribution-row"
                  key={item.label}
                >
                  <div className="device-risk-distribution-label">
                    <strong>{item.label}</strong>
                    <span>{item.range}</span>
                  </div>

                  <div className="device-risk-distribution-track">
                    <span
                      style={{
                        width: `${
                          devices.length
                            ? (item.count / devices.length) * 100
                            : 0
                        }%`,
                      }}
                    />
                  </div>

                  <strong>{item.count}</strong>
                </div>
              ))}
            </div>
          </div>
        </article>

        <article className="organization-panel device-risk-focus-panel">
          <div className="organization-panel-header">
            <div>
              <span>RISK FOCUS</span>
              <h2>Devices requiring attention</h2>
            </div>

            <span className="organization-panel-meta">
              {atRiskCount + reviewCount} DEVICES
            </span>
          </div>

          <div className="device-risk-focus-list">
            {lowestRiskDevices.map((device) => (
              <button
                type="button"
                className="device-risk-focus-item"
                key={device.name}
                onClick={() => setSelectedDevice(device)}
              >
                <div className="device-risk-focus-icon" aria-hidden="true">
                  {device.type === "Laptop" ? "▣" : "▤"}
                </div>

                <div className="device-risk-focus-identity">
                  <strong>{device.name}</strong>
                  <span>{device.employee}</span>
                </div>

                <div className="device-risk-focus-score">
                  <strong>{device.score}</strong>

                  <span
                    className={
                      device.status === "At Risk"
                        ? "at-risk"
                        : device.status === "Review"
                          ? "review"
                          : "protected"
                    }
                  >
                    {device.status}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </article>
      </section>

      <section className="devices-overview-grid">
        <article className="organization-panel device-posture-panel">
          <div className="organization-panel-header">
            <div>
              <span>DEVICE SECURITY</span>
              <h2>Security posture</h2>
            </div>

            <span className="organization-panel-meta">
              {averageScore} AVG
            </span>
          </div>

          <div className="device-posture-overview">
            <div className="device-average-score">
              <span>AVERAGE DEVICE SCORE</span>

              <strong>{averageScore}</strong>

              <div className="device-average-bar">
                <span style={{ width: `${averageScore}%` }} />
              </div>
            </div>

            <div className="device-posture-summary">
              <div>
                <span>PROTECTED</span>
                <strong>{protectedCount}</strong>
              </div>

              <div>
                <span>REVIEW</span>
                <strong>{reviewCount}</strong>
              </div>

              <div>
                <span>AT RISK</span>
                <strong>{atRiskCount}</strong>
              </div>

              <div>
                <span>OFFLINE</span>
                <strong>{offlineCount}</strong>
              </div>
            </div>
          </div>

          <div className="device-status-distribution">
            <div className="device-analytics-label">
              <span>DEVICE STATUS</span>
              <span>LIVE VIEW</span>
            </div>

            {statusDistribution.map((item) => (
              <div
                className="device-distribution-row"
                key={item.label}
              >
                <div>
                  <strong>{item.label}</strong>
                </div>

                <div className="device-distribution-bar">
                  <span
                    style={{
                      width: `${
                        devices.length
                          ? (item.count / devices.length) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>

                <strong>{item.count}</strong>
              </div>
            ))}
          </div>
        </article>

        <article className="organization-panel device-platform-panel">
          <div className="organization-panel-header">
            <div>
              <span>PLATFORM VISIBILITY</span>
              <h2>Operating systems</h2>
            </div>

            <span className="organization-panel-meta">
              {devices.length} DEVICES
            </span>
          </div>

          <div className="device-platform-list">
            {platformDistribution.map((platform) => (
              <div
                className="device-platform-item"
                key={platform.label}
              >
                <div className="device-platform-heading">
                  <div>
                    <span className="device-platform-icon" aria-hidden="true">
                      {platform.label === "Windows 11" ? "▣" : "□"}
                    </span>

                    <strong>{platform.label}</strong>
                  </div>

                  <span>{platform.count}</span>
                </div>

                <div className="device-platform-bar">
                  <span
                    style={{
                      width: `${
                        devices.length
                          ? (platform.count / devices.length) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="device-platform-note">
            <span className="device-platform-note-dot" />
            <span>
              Platform inventory is ready for backend synchronization.
            </span>
          </div>
        </article>
      </section>

      <section className="organization-panel device-login-panel">
        <div className="organization-panel-header">
          <div>
            <span>ACCESS MONITORING</span>
            <h2>Recent login activity</h2>
          </div>

          <div className="device-login-summary">
            <span>
              <strong>{successfulLogins}</strong> VERIFIED
            </span>

            <span>
              <strong>{reviewLogins}</strong> REVIEW
            </span>
          </div>
        </div>

        <div className="device-login-list">
          {loginEvents.map((event) => (
            <button
              type="button"
              className={`device-login-row ${
                event.status === "Review" ? "requires-review" : ""
              }`}
              key={`${event.employee}-${event.time}`}
              onClick={() => setSelectedLogin(event)}
            >
              <div className="device-login-indicator">
                <span
                  className={
                    event.status === "Successful"
                      ? "successful"
                      : "review"
                  }
                />
              </div>

              <div className="device-login-identity">
                <strong>{event.employee}</strong>
                <span>{event.device}</span>
              </div>

              <div className="device-login-location">
                <span>LOCATION</span>
                <strong>{event.location}</strong>
              </div>

              <div className="device-login-type">
                <span>ACCESS</span>
                <strong>{event.type}</strong>
              </div>

              <div className="device-login-time">
                <span>{event.time}</span>

                <strong
                  className={
                    event.status === "Successful"
                      ? "successful"
                      : "review"
                  }
                >
                  {event.status}
                </strong>
              </div>

              <span className="device-login-arrow" aria-hidden="true">
                →
              </span>
            </button>
          ))}
        </div>

        <div className="device-login-footer">
          <span className="device-platform-note-dot" />

          <span>
            Login events shown here are demo monitoring data until the
            authentication activity API is connected.
          </span>
        </div>
      </section>

      <section className="organization-panel device-directory-panel">
        <div className="organization-panel-header">
          <div>
            <span>DEVICE INVENTORY</span>
            <h2>Registered devices</h2>
          </div>

          <div className="device-directory-header-meta">
            <span>93 DEVICES</span>

            <span className="device-directory-live">
              <i aria-hidden="true" />
              MONITORING
            </span>
          </div>
        </div>

        <div className="device-directory-summary">
          <div>
            <span>VISIBLE ENDPOINTS</span>
            <strong>{devices.length}</strong>
          </div>

          <div>
            <span>AVERAGE SCORE</span>
            <strong>{averageScore}</strong>
          </div>

          <div>
            <span>REQUIRING ATTENTION</span>
            <strong>{atRiskCount + reviewCount}</strong>
          </div>

          <div>
            <span>LAST SYNC</span>
            <strong>2 MIN AGO</strong>
          </div>
        </div>

        <div className="device-table-header">
          <span>Device</span>
          <span>Employee</span>
          <span>Platform</span>
          <span>Last Active</span>
          <span>Security Score</span>
          <span>Status</span>
          <span />
        </div>

        <div className="device-list">
          {devices.map((device) => (
            <article
              className={`device-row device-row-${device.status
                .toLowerCase()
                .replace(" ", "-")}`}
              key={device.name}
              style={
                {
                  "--device-score": device.score,
                } as CSSProperties
              }
            >
              <div className="device-identity">
                <div className="device-icon" aria-hidden="true">
                  {device.type === "Laptop" ? "▣" : "▤"}
                </div>

                <div>
                  <strong>{device.name}</strong>
                  <span>{device.type}</span>
                </div>
              </div>

              <div className="device-owner">
                <strong>{device.employee}</strong>
                <span>Organization member</span>
              </div>

              <div className="device-platform">
                <strong>{device.os}</strong>
                <span>{device.type}</span>
              </div>

              <div className="device-last-active">
                <strong>{device.lastActive}</strong>
                <span>
                  {device.lastActive === "1 hr ago"
                    ? "RECENTLY ACTIVE"
                    : "ACTIVE SESSION"}
                </span>
              </div>

              <div className="device-score">
                <div className="device-score-heading">
                  <strong>{device.score}</strong>
                  <span>/ 100</span>
                </div>

                <span className="device-score-bar">
                  <span />
                </span>
              </div>

              <span
                className={`device-status ${
                  device.status === "Protected"
                    ? "protected"
                    : device.status === "At Risk"
                      ? "at-risk"
                      : device.status === "Offline"
                        ? "offline"
                        : "review"
                }`}
              >
                <span aria-hidden="true" />
                {device.status}
              </span>

              <button
                type="button"
                className="device-view-button"
                aria-label={`View ${device.name}`}
                onClick={() => setSelectedDevice(device)}
              >
                <span>View</span>
                <span aria-hidden="true">→</span>
              </button>
            </article>
          ))}
        </div>
      </section>

      {(selectedDevice || selectedLogin || showRegisterPanel) && (
        <div
          className="device-modal-backdrop"
          role="presentation"
          onClick={closeOverlays}
        >
          <section
            className={`device-modal ${
              selectedDevice ? "device-detail-modal" : ""
            }`}
            role="dialog"
            aria-modal="true"
            aria-labelledby="device-modal-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="device-modal-header">
              <div>
                <span>
                  {selectedDevice
                    ? "ENDPOINT SECURITY PROFILE"
                    : selectedLogin
                      ? "LOGIN SECURITY EVENT"
                      : "DEVICE MANAGEMENT"}
                </span>

                <h2 id="device-modal-title">
                  {selectedDevice
                    ? selectedDevice.name
                    : selectedLogin
                      ? selectedLogin.employee
                      : "Register Device"}
                </h2>
              </div>

              <button
                type="button"
                className="device-modal-close"
                onClick={closeOverlays}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            {selectedDevice ? (
              <div className="device-detail-content">
                <div className="device-detail-hero">
                  <div className="device-detail-identity">
                    <div className="device-detail-icon" aria-hidden="true">
                      {selectedDevice.type === "Laptop" ? "▣" : "▤"}
                    </div>

                    <div>
                      <strong>{selectedDevice.name}</strong>
                      <span>{selectedDevice.employee}</span>
                      <small>
                        {selectedDevice.type} · {selectedDevice.os}
                      </small>
                    </div>
                  </div>

                  <span
                    className={`device-detail-status ${
                      selectedDevice.status === "Protected"
                        ? "protected"
                        : selectedDevice.status === "At Risk"
                          ? "at-risk"
                          : selectedDevice.status === "Offline"
                            ? "offline"
                            : "review"
                    }`}
                  >
                    <span aria-hidden="true" />
                    {selectedDevice.status}
                  </span>
                </div>

                <div className="device-detail-score-section">
                  <div className="device-detail-score-heading">
                    <div>
                      <span>ENDPOINT SECURITY SCORE</span>
                      <small>Current device posture</small>
                    </div>

                    <div>
                      <strong>{selectedDevice.score}</strong>
                      <span>/ 100</span>
                    </div>
                  </div>

                  <div className="device-detail-score-track">
                    <span
                      style={{
                        width: `${selectedDevice.score}%`,
                      }}
                    />
                  </div>

                  <div className="device-detail-score-scale">
                    <span>0 CRITICAL</span>
                    <span>50 REVIEW</span>
                    <span>100 PROTECTED</span>
                  </div>
                </div>

                <div className="device-detail-grid">
                  <div>
                    <span>DEVICE OWNER</span>
                    <strong>{selectedDevice.employee}</strong>
                    <small>Organization member</small>
                  </div>

                  <div>
                    <span>DEVICE TYPE</span>
                    <strong>{selectedDevice.type}</strong>
                    <small>Registered endpoint</small>
                  </div>

                  <div>
                    <span>OPERATING SYSTEM</span>
                    <strong>{selectedDevice.os}</strong>
                    <small>Detected platform</small>
                  </div>

                  <div>
                    <span>LAST ACTIVE</span>
                    <strong>{selectedDevice.lastActive}</strong>
                    <small>Endpoint activity</small>
                  </div>
                </div>

                <div className="device-detail-monitoring">
                  <div>
                    <span className="device-detail-monitoring-dot" />
                    <div>
                      <strong>Endpoint monitoring active</strong>
                      <span>
                        Device visibility is ready for backend telemetry.
                      </span>
                    </div>
                  </div>

                  <span>MONITORED</span>
                </div>

                <div className="device-detail-actions">
                  <button
                    type="button"
                    className="button button-primary"
                    onClick={closeOverlays}
                  >
                    Close Profile
                  </button>
                </div>
              </div>
            ) : selectedLogin ? (
              <div className="device-modal-content">
                <div className="device-login-detail-status">
                  <span
                    className={
                      selectedLogin.status === "Successful"
                        ? "successful"
                        : "review"
                    }
                  >
                    {selectedLogin.status}
                  </span>
                </div>

                <div className="device-login-detail-grid">
                  <div>
                    <span>EMPLOYEE</span>
                    <strong>{selectedLogin.employee}</strong>
                  </div>

                  <div>
                    <span>DEVICE</span>
                    <strong>{selectedLogin.device}</strong>
                  </div>

                  <div>
                    <span>LOCATION</span>
                    <strong>{selectedLogin.location}</strong>
                  </div>

                  <div>
                    <span>IP ADDRESS</span>
                    <strong>{selectedLogin.ip}</strong>
                  </div>

                  <div>
                    <span>ACCESS TYPE</span>
                    <strong>{selectedLogin.type}</strong>
                  </div>

                  <div>
                    <span>TIME</span>
                    <strong>{selectedLogin.time}</strong>
                  </div>
                </div>

                <div className="device-login-detail-note">
                  <span>SECURITY NOTE</span>
                  <p>{selectedLogin.detail}</p>
                </div>

                <button
                  type="button"
                  className="button button-primary"
                  onClick={closeOverlays}
                >
                  Close
                </button>
              </div>
            ) : (
              <div className="device-modal-content">
                <p className="device-modal-message">
                  Device registration will be connected to the organization
                  backend when the device management API is available.
                </p>

                <button
                  type="button"
                  className="button button-primary"
                  onClick={closeOverlays}
                >
                  Close
                </button>
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}