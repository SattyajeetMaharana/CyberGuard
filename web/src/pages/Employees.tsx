const employees = [
  {
    name: "Arjun Sharma",
    email: "arjun.sharma@organization.com",
    department: "Engineering",
    devices: 2,
    score: 91,
    status: "Protected",
  },
  {
    name: "Priya Das",
    email: "priya.das@organization.com",
    department: "Operations",
    devices: 1,
    score: 84,
    status: "Protected",
  },
  {
    name: "Rahul Mehta",
    email: "rahul.mehta@organization.com",
    department: "Finance",
    devices: 2,
    score: 63,
    status: "Review",
  },
  {
    name: "Ananya Patel",
    email: "ananya.patel@organization.com",
    department: "Human Resources",
    devices: 1,
    score: 88,
    status: "Protected",
  },
  {
    name: "Vikram Singh",
    email: "vikram.singh@organization.com",
    department: "Engineering",
    devices: 3,
    score: 72,
    status: "Review",
  },
];

export default function Employees() {
  return (
    <div className="organization-section">
      <header className="organization-section-header">
        <div>
          <span className="organization-section-eyebrow">
            ORGANIZATION MANAGEMENT
          </span>

          <h1>Employees</h1>

          <p>
            Manage organization members and monitor their security posture
            across the CyberGuard workspace.
          </p>
        </div>

        <button type="button" className="button button-primary">
          Invite Employee
        </button>
      </header>

      <section className="employee-stat-grid">
        <article className="organization-stat-card">
          <span>Total Employees</span>
          <strong>98</strong>
          <p>Organization members</p>
        </article>

        <article className="organization-stat-card">
          <span>Protected</span>
          <strong>81</strong>
          <p>Healthy security status</p>
        </article>

        <article className="organization-stat-card">
          <span>Needs Review</span>
          <strong>17</strong>
          <p>Require attention</p>
        </article>

        <article className="organization-stat-card">
          <span>Invitations</span>
          <strong>06</strong>
          <p>Pending invitations</p>
        </article>
      </section>

      <section className="organization-panel employee-panel">
        <div className="organization-panel-header">
          <div>
            <span>EMPLOYEE DIRECTORY</span>
            <h2>Organization members</h2>
          </div>

          <span className="organization-panel-meta">98 members</span>
        </div>

        <div className="employee-table-header">
          <span>Employee</span>
          <span>Department</span>
          <span>Devices</span>
          <span>Score</span>
          <span>Status</span>
        </div>

        <div className="employee-list">
          {employees.map((employee) => (
            <article className="employee-row" key={employee.email}>
              <div className="employee-identity">
                <div className="employee-avatar" aria-hidden="true">
                  {employee.name
                    .split(" ")
                    .map((part) => part[0])
                    .join("")
                    .slice(0, 2)}
                </div>

                <div>
                  <strong>{employee.name}</strong>
                  <span>{employee.email}</span>
                </div>
              </div>

              <span className="employee-department">
                {employee.department}
              </span>

              <strong className="employee-devices">
                {employee.devices}
              </strong>

              <strong className="employee-score">
                {employee.score}
              </strong>

              <span
                className={`employee-status ${
                  employee.status === "Protected"
                    ? "protected"
                    : "review"
                }`}
              >
                {employee.status}
              </span>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}