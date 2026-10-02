const departments = [
  {
    name: "Engineering",
    employees: 42,
    devices: 38,
    score: 84,
    status: "Healthy",
  },
  {
    name: "Operations",
    employees: 28,
    devices: 25,
    score: 76,
    status: "Healthy",
  },
  {
    name: "Finance",
    employees: 16,
    devices: 17,
    score: 68,
    status: "Review",
  },
  {
    name: "Human Resources",
    employees: 12,
    devices: 13,
    score: 81,
    status: "Healthy",
  },
];

export default function Departments() {
  return (
    <div className="organization-section">
      <header className="organization-section-header">
        <div>
          <span className="organization-section-eyebrow">
            ORGANIZATION MANAGEMENT
          </span>

          <h1>Departments</h1>

          <p>
            Organize employees, devices, and security visibility across your
            organization's departments.
          </p>
        </div>

        <button type="button" className="button button-primary">
          Add Department
        </button>
      </header>

      <section className="department-stat-grid">
        <article className="organization-stat-card">
          <span>Total Departments</span>
          <strong>04</strong>
          <p>Active departments</p>
        </article>

        <article className="organization-stat-card">
          <span>Employees</span>
          <strong>98</strong>
          <p>Across departments</p>
        </article>

        <article className="organization-stat-card">
          <span>Devices</span>
          <strong>93</strong>
          <p>Managed devices</p>
        </article>

        <article className="organization-stat-card">
          <span>Average Score</span>
          <strong>77</strong>
          <p>Department security score</p>
        </article>
      </section>

      <section className="organization-panel department-panel">
        <div className="organization-panel-header">
          <div>
            <span>DEPARTMENT DIRECTORY</span>
            <h2>Organization departments</h2>
          </div>

          <span className="organization-panel-meta">Current</span>
        </div>

        <div className="department-list">
          {departments.map((department) => (
            <article className="department-row" key={department.name}>
              <div className="department-identity">
                <div className="department-icon" aria-hidden="true">
                  {department.name.charAt(0)}
                </div>

                <div>
                  <strong>{department.name}</strong>
                  <span>{department.status}</span>
                </div>
              </div>

              <div className="department-metric">
                <span>Employees</span>
                <strong>{department.employees}</strong>
              </div>

              <div className="department-metric">
                <span>Devices</span>
                <strong>{department.devices}</strong>
              </div>

              <div className="department-score">
                <span>Score</span>
                <strong>{department.score}</strong>
              </div>

              <button
                type="button"
                className="department-view-button"
                aria-label={`View ${department.name}`}
              >
                →
              </button>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}