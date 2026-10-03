import { useState, type CSSProperties } from "react";

interface Employee {
  name: string;
  email: string;
  department: string;
  devices: number;
  score: number;
  status: "Protected" | "Review";
}

const employees: Employee[] = [
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

const riskDistribution = [
  {
    label: "Excellent",
    range: "80–100",
    count: employees.filter((employee) => employee.score >= 80).length,
  },
  {
    label: "Good",
    range: "60–79",
    count: employees.filter(
      (employee) => employee.score >= 60 && employee.score < 80,
    ).length,
  },
  {
    label: "Needs Review",
    range: "40–59",
    count: employees.filter(
      (employee) => employee.score >= 40 && employee.score < 60,
    ).length,
  },
  {
    label: "Critical",
    range: "0–39",
    count: employees.filter((employee) => employee.score < 40).length,
  },
];

export default function Employees() {
  const [selectedEmployee, setSelectedEmployee] =
    useState<Employee | null>(null);

  const [showInvitePanel, setShowInvitePanel] = useState(false);

  const averageScore = Math.round(
    employees.reduce(
      (total, employee) => total + employee.score,
      0,
    ) / employees.length,
  );

  const protectedCount = employees.filter(
    (employee) => employee.status === "Protected",
  ).length;

  const reviewCount = employees.filter(
    (employee) => employee.status === "Review",
  ).length;

  const totalDevices = employees.reduce(
    (total, employee) => total + employee.devices,
    0,
  );

  return (
    <div className="employees-page organization-section">
      <header className="organization-section-header employees-header">
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

        <button
          type="button"
          className="button button-primary"
          onClick={() => setShowInvitePanel(true)}
        >
          <span>Invite Employee</span>
          <span aria-hidden="true">+</span>
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

      <section className="employees-analytics-grid">
        <article className="organization-panel employee-risk-panel">
          <div className="organization-panel-header">
            <div>
              <span>EMPLOYEE SECURITY</span>

              <h2>Risk distribution</h2>
            </div>

            <span className="organization-panel-meta">
              {averageScore} AVG
            </span>
          </div>

          <div className="employee-risk-overview">
            <div className="employee-average-score">
              <span>AVERAGE SECURITY SCORE</span>

              <strong>{averageScore}</strong>

              <div className="employee-average-bar">
                <span
                  style={{
                    width: `${averageScore}%`,
                  }}
                />
              </div>
            </div>

            <div className="employee-risk-summary">
              <div>
                <span>PROTECTED</span>
                <strong>{protectedCount}</strong>
              </div>

              <div>
                <span>REVIEW</span>
                <strong>{reviewCount}</strong>
              </div>

              <div>
                <span>DEVICES</span>
                <strong>{totalDevices}</strong>
              </div>
            </div>
          </div>

          <div className="employee-risk-distribution">
            {riskDistribution.map((item) => (
              <div
                className="employee-risk-distribution-row"
                key={item.label}
              >
                <div>
                  <strong>{item.label}</strong>
                  <span>{item.range}</span>
                </div>

                <div className="employee-risk-distribution-bar">
                  <span
                    style={{
                      width: `${
                        employees.length
                          ? (item.count / employees.length) * 100
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

        <article className="organization-panel employee-attention-panel">
          <div className="organization-panel-header">
            <div>
              <span>ATTENTION REQUIRED</span>

              <h2>Employees for review</h2>
            </div>

            <span className="organization-panel-meta">
              {String(reviewCount).padStart(2, "0")}
            </span>
          </div>

          <div className="employee-attention-list">
            {employees
              .filter((employee) => employee.status === "Review")
              .map((employee) => (
                <button
                  type="button"
                  className="employee-attention-item"
                  key={employee.email}
                  onClick={() => setSelectedEmployee(employee)}
                >
                  <div>
                    <strong>{employee.name}</strong>

                    <span>
                      {employee.department} · Score {employee.score}
                    </span>
                  </div>

                  <span>REVIEW</span>
                </button>
              ))}
          </div>
        </article>
      </section>

      <section className="organization-panel employee-directory-panel">
        <div className="organization-panel-header">
          <div>
            <span>EMPLOYEE DIRECTORY</span>

            <h2>Organization members</h2>
          </div>

          <span className="organization-panel-meta">
            98 MEMBERS
          </span>
        </div>

        <div className="employee-table-header">
          <span>Employee</span>
          <span>Department</span>
          <span>Devices</span>
          <span>Score</span>
          <span>Status</span>
          <span />
        </div>

        <div className="employee-list">
          {employees.map((employee) => (
            <article
              className="employee-row"
              key={employee.email}
              style={
                {
                  "--employee-score": employee.score,
                } as CSSProperties
              }
            >
              <div className="employee-identity">
                <div
                  className="employee-avatar"
                  aria-hidden="true"
                >
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

              <div className="employee-score">
                <strong>{employee.score}</strong>

                <span className="employee-score-bar">
                  <span />
                </span>
              </div>

              <span
                className={`employee-status ${
                  employee.status === "Protected"
                    ? "protected"
                    : "review"
                }`}
              >
                <span aria-hidden="true" />
                {employee.status}
              </span>

              <button
                type="button"
                className="employee-view-button"
                aria-label={`View ${employee.name}`}
                onClick={() => setSelectedEmployee(employee)}
              >
                →
              </button>
            </article>
          ))}
        </div>
      </section>

      {(selectedEmployee || showInvitePanel) && (
        <div
          className="employee-modal-backdrop"
          role="presentation"
          onClick={() => {
            setSelectedEmployee(null);
            setShowInvitePanel(false);
          }}
        >
          <section
            className="employee-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="employee-modal-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="employee-modal-header">
              <div>
                <span>
                  {selectedEmployee
                    ? "EMPLOYEE SECURITY PROFILE"
                    : "ORGANIZATION MANAGEMENT"}
                </span>

                <h2 id="employee-modal-title">
                  {selectedEmployee
                    ? selectedEmployee.name
                    : "Invite Employee"}
                </h2>
              </div>

              <button
                type="button"
                className="employee-modal-close"
                onClick={() => {
                  setSelectedEmployee(null);
                  setShowInvitePanel(false);
                }}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            {selectedEmployee ? (
              <div className="employee-modal-content">
                <div className="employee-profile-heading">
                  <div className="employee-modal-avatar">
                    {selectedEmployee.name
                      .split(" ")
                      .map((part) => part[0])
                      .join("")
                      .slice(0, 2)}
                  </div>

                  <div>
                    <strong>{selectedEmployee.name}</strong>

                    <span>{selectedEmployee.email}</span>
                  </div>
                </div>

                <div className="employee-modal-score">
                  <span>SECURITY SCORE</span>

                  <strong>{selectedEmployee.score}</strong>

                  <div>
                    <span
                      style={{
                        width: `${selectedEmployee.score}%`,
                      }}
                    />
                  </div>

                  <small>{selectedEmployee.status}</small>
                </div>

                <div className="employee-modal-stats">
                  <div>
                    <span>DEPARTMENT</span>

                    <strong>
                      {selectedEmployee.department}
                    </strong>
                  </div>

                  <div>
                    <span>DEVICES</span>

                    <strong>
                      {selectedEmployee.devices}
                    </strong>
                  </div>

                  <div>
                    <span>STATUS</span>

                    <strong>
                      {selectedEmployee.status}
                    </strong>
                  </div>
                </div>
              </div>
            ) : (
              <div className="employee-modal-content">
                <p className="employee-modal-message">
                  Employee invitations will be connected to the organization
                  backend when the employee invitation API is available.
                </p>

                <button
                  type="button"
                  className="button button-primary"
                  onClick={() => setShowInvitePanel(false)}
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