import { useState } from "react";

interface Department {
  name: string;
  employees: number;
  devices: number;
  score: number;
  status: "Healthy" | "Review";
}

const departments: Department[] = [
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

const scoreDistribution = [
  {
    label: "Excellent",
    range: "80–100",
    count: 2,
  },
  {
    label: "Good",
    range: "60–79",
    count: 2,
  },
  {
    label: "Needs Review",
    range: "40–59",
    count: 0,
  },
  {
    label: "Critical",
    range: "0–39",
    count: 0,
  },
];

export default function Departments() {
  const [selectedDepartment, setSelectedDepartment] =
    useState<Department | null>(null);

  const [showAddPanel, setShowAddPanel] = useState(false);

  const averageScore = Math.round(
    departments.reduce(
      (total, department) => total + department.score,
      0,
    ) / departments.length,
  );

  const reviewCount = departments.filter(
    (department) => department.status === "Review",
  ).length;

  const totalEmployees = departments.reduce(
    (total, department) => total + department.employees,
    0,
  );

  const totalDevices = departments.reduce(
    (total, department) => total + department.devices,
    0,
  );

  return (
    <div className="departments-page organization-section">
      <header className="organization-section-header departments-header">
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

        <button
          type="button"
          className="button button-primary"
          onClick={() => setShowAddPanel(true)}
        >
          <span>Add Department</span>
          <span aria-hidden="true">+</span>
        </button>
      </header>

      <section className="department-stat-grid">
        <article className="organization-stat-card">
          <span>Total Departments</span>

          <strong>
            {String(departments.length).padStart(2, "0")}
          </strong>

          <p>Active departments</p>
        </article>

        <article className="organization-stat-card">
          <span>Employees</span>

          <strong>{totalEmployees}</strong>

          <p>Across departments</p>
        </article>

        <article className="organization-stat-card">
          <span>Devices</span>

          <strong>{totalDevices}</strong>

          <p>Managed devices</p>
        </article>

        <article className="organization-stat-card">
          <span>Average Score</span>

          <strong>{averageScore}</strong>

          <p>Department security score</p>
        </article>
      </section>

      <section className="departments-analytics-grid">
        <article className="organization-panel department-posture-panel">
          <div className="organization-panel-header">
            <div>
              <span>SECURITY POSTURE</span>

              <h2>Department score distribution</h2>
            </div>

            <span className="organization-panel-meta">
              / 04
            </span>
          </div>

          <div className="department-score-distribution">
            {scoreDistribution.map((item) => (
              <div
                className="department-score-distribution-row"
                key={item.label}
              >
                <div className="department-score-distribution-label">
                  <strong>{item.label}</strong>

                  <span>{item.range}</span>
                </div>

                <div className="department-score-distribution-bar">
                  <span
                    style={{
                      width: `${Math.min(
                        item.count * 50,
                        100,
                      )}%`,
                    }}
                  />
                </div>

                <strong className="department-score-distribution-count">
                  {item.count}
                </strong>
              </div>
            ))}
          </div>
        </article>

        <article className="organization-panel department-review-panel">
          <div className="organization-panel-header">
            <div>
              <span>ATTENTION REQUIRED</span>

              <h2>Department monitoring</h2>
            </div>

            <span className="organization-panel-meta">
              {String(reviewCount).padStart(2, "0")}
            </span>
          </div>

          <div className="department-review-content">
            <div className="department-review-number">
              <strong>
                {String(reviewCount).padStart(2, "0")}
              </strong>

              <span>
                DEPARTMENT{reviewCount === 1 ? "" : "S"} FOR REVIEW
              </span>
            </div>

            <div className="department-review-details">
              {departments
                .filter(
                  (department) =>
                    department.status === "Review",
                )
                .map((department) => (
                  <button
                    type="button"
                    className="department-review-item"
                    key={department.name}
                    onClick={() =>
                      setSelectedDepartment(department)
                    }
                  >
                    <div>
                      <strong>{department.name}</strong>

                      <span>
                        Security score {department.score}
                      </span>
                    </div>

                    <span>REVIEW</span>
                  </button>
                ))}

              {reviewCount === 0 && (
                <div className="department-review-empty">
                  <strong>
                    All departments are healthy.
                  </strong>

                  <span>
                    No department currently requires additional review.
                  </span>
                </div>
              )}
            </div>
          </div>
        </article>
      </section>

      <section className="organization-panel department-directory-panel">
        <div className="organization-panel-header">
          <div>
            <span>DEPARTMENT DIRECTORY</span>

            <h2>Organization departments</h2>
          </div>

          <span className="organization-panel-meta">
            CURRENT
          </span>
        </div>

        <div className="department-list">
          {departments.map((department) => (
            <article
              className="department-row"
              key={department.name}
              style={
                {
                  "--department-score": department.score,
                } as React.CSSProperties
              }
            >
              <div className="department-identity">
                <div
                  className="department-icon"
                  aria-hidden="true"
                >
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
                onClick={() =>
                  setSelectedDepartment(department)
                }
              >
                →
              </button>
            </article>
          ))}
        </div>
      </section>

      {(selectedDepartment || showAddPanel) && (
        <div
          className="department-modal-backdrop"
          role="presentation"
          onClick={() => {
            setSelectedDepartment(null);
            setShowAddPanel(false);
          }}
        >
          <section
            className="department-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="department-modal-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="department-modal-header">
              <div>
                <span>
                  {selectedDepartment
                    ? "DEPARTMENT OVERVIEW"
                    : "ORGANIZATION MANAGEMENT"}
                </span>

                <h2 id="department-modal-title">
                  {selectedDepartment
                    ? selectedDepartment.name
                    : "Add Department"}
                </h2>
              </div>

              <button
                type="button"
                className="department-modal-close"
                onClick={() => {
                  setSelectedDepartment(null);
                  setShowAddPanel(false);
                }}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            {selectedDepartment ? (
              <div className="department-modal-content">
                <div className="department-modal-score">
                  <span>SECURITY SCORE</span>

                  <strong>{selectedDepartment.score}</strong>

                  <div>
                    <span
                      style={{
                        width: `${selectedDepartment.score}%`,
                      }}
                    />
                  </div>

                  <small>
                    {selectedDepartment.status}
                  </small>
                </div>

                <div className="department-modal-stats">
                  <div>
                    <span>EMPLOYEES</span>
                    <strong>
                      {selectedDepartment.employees}
                    </strong>
                  </div>

                  <div>
                    <span>DEVICES</span>
                    <strong>
                      {selectedDepartment.devices}
                    </strong>
                  </div>

                  <div>
                    <span>STATUS</span>
                    <strong>
                      {selectedDepartment.status}
                    </strong>
                  </div>
                </div>
              </div>
            ) : (
              <div className="department-modal-content">
                <p className="department-modal-message">
                  Department creation will be connected to the organization
                  backend when the department management API is available.
                </p>

                <button
                  type="button"
                  className="button button-primary"
                  onClick={() => setShowAddPanel(false)}
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