const devices = [
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

export default function Devices() {
  return (
    <div className="organization-section">
      <header className="organization-section-header">
        <div>
          <span className="organization-section-eyebrow">
            ORGANIZATION MANAGEMENT
          </span>

          <h1>Devices</h1>

          <p>
            Monitor registered devices and maintain visibility across your
            organization's security environment.
          </p>
        </div>

        <button type="button" className="button button-primary">
          Register Device
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

      <section className="organization-panel device-panel">
        <div className="organization-panel-header">
          <div>
            <span>DEVICE INVENTORY</span>
            <h2>Registered devices</h2>
          </div>

          <span className="organization-panel-meta">93 devices</span>
        </div>

        <div className="device-table-header">
          <span>Device</span>
          <span>Employee</span>
          <span>Platform</span>
          <span>Last Active</span>
          <span>Score</span>
          <span>Status</span>
        </div>

        <div className="device-list">
          {devices.map((device) => (
            <article className="device-row" key={device.name}>
              <div className="device-identity">
                <div className="device-icon" aria-hidden="true">
                  {device.type === "Laptop" ? "▣" : "▤"}
                </div>

                <div>
                  <strong>{device.name}</strong>
                  <span>{device.type}</span>
                </div>
              </div>

              <span className="device-employee">
                {device.employee}
              </span>

              <div className="device-platform">
                <strong>{device.os}</strong>
              </div>

              <span className="device-last-active">
                {device.lastActive}
              </span>

              <strong className="device-score">
                {device.score}
              </strong>

              <span
                className={`device-status ${
                  device.status === "Protected"
                    ? "protected"
                    : device.status === "At Risk"
                      ? "at-risk"
                      : "review"
                }`}
              >
                {device.status}
              </span>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}