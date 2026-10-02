const policies = [
  {
    name: "Password Security",
    description: "Enforces organization password requirements.",
    category: "Authentication",
    status: "Active",
    updated: "2 days ago",
  },
  {
    name: "Device Protection",
    description: "Defines minimum security requirements for registered devices.",
    category: "Device Security",
    status: "Active",
    updated: "5 days ago",
  },
  {
    name: "Phishing Protection",
    description: "Controls organizational response to detected phishing threats.",
    category: "Threat Protection",
    status: "Active",
    updated: "1 week ago",
  },
  {
    name: "Incident Response",
    description: "Defines procedures for handling detected security incidents.",
    category: "Incident Management",
    status: "Active",
    updated: "2 weeks ago",
  },
  {
    name: "Employee Access",
    description: "Controls access permissions for organization members.",
    category: "Access Control",
    status: "Draft",
    updated: "3 weeks ago",
  },
];

export default function Policies() {
  return (
    <div className="organization-section">
      <header className="organization-section-header">
        <div>
          <span className="organization-section-eyebrow">
            ORGANIZATION MANAGEMENT
          </span>

          <h1>Policies</h1>

          <p>
            Define and manage security policies that govern your
            organization's cybersecurity environment.
          </p>
        </div>

        <button type="button" className="button button-primary">
          Create Policy
        </button>
      </header>

      <section className="policy-stat-grid">
        <article className="organization-stat-card">
          <span>Total Policies</span>
          <strong>05</strong>
          <p>Configured policies</p>
        </article>

        <article className="organization-stat-card">
          <span>Active</span>
          <strong>04</strong>
          <p>Currently enforced</p>
        </article>

        <article className="organization-stat-card">
          <span>Drafts</span>
          <strong>01</strong>
          <p>Pending activation</p>
        </article>

        <article className="organization-stat-card">
          <span>Compliance</span>
          <strong>92%</strong>
          <p>Organization compliance</p>
        </article>
      </section>

      <section className="organization-panel policy-panel">
        <div className="organization-panel-header">
          <div>
            <span>SECURITY POLICY DIRECTORY</span>
            <h2>Organization policies</h2>
          </div>

          <span className="organization-panel-meta">05 policies</span>
        </div>

        <div className="policy-list">
          {policies.map((policy) => (
            <article className="policy-row" key={policy.name}>
              <div className="policy-icon" aria-hidden="true">
                ◈
              </div>

              <div className="policy-information">
                <strong>{policy.name}</strong>
                <p>{policy.description}</p>
              </div>

              <span className="policy-category">
                {policy.category}
              </span>

              <span
                className={`policy-status ${
                  policy.status === "Active" ? "active" : "draft"
                }`}
              >
                {policy.status}
              </span>

              <span className="policy-updated">
                {policy.updated}
              </span>

              <button
                type="button"
                className="policy-action"
                aria-label={`View ${policy.name}`}
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