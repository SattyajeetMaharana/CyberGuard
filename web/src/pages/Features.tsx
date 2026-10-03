const features = [
  {
    number: "01",
    title: "Multi-Layer Detection",
    description:
      "Analyze different cybersecurity threats through specialized detection capabilities working together as one platform.",
  },
  {
    number: "02",
    title: "Threat Center",
    description:
      "Centralize detected threats and security events so your organization can maintain a clear view of emerging risks.",
  },
  {
    number: "03",
    title: "Incident Management",
    description:
      "Organize security incidents, understand their status, and maintain visibility throughout the response process.",
  },
  {
    number: "04",
    title: "Cyber Score",
    description:
      "Track your organization's security posture through a centralized cybersecurity scoring and analytics interface.",
  },
  {
    number: "05",
    title: "Organization Management",
    description:
      "Manage departments, employees, devices, and organizational security policies from one workspace.",
  },
  {
    number: "06",
    title: "Explainable Security",
    description:
      "Present security analysis with understandable explanations so users can better understand why a threat was detected.",
  },
];

export default function Features() {
  return (
    <div className="features-page">
      <section className="features-hero">
        <div className="features-hero-content">
          <span className="home-eyebrow">CYBERGUARD PLATFORM</span>

          <h1>
            Everything your organization needs
            <span> to understand its security.</span>
          </h1>

          <p>
            CyberGuard brings detection, monitoring, analysis, and organization
            management together in a unified cybersecurity workspace.
          </p>
        </div>

        <div className="features-hero-marker" aria-hidden="true">
          <span>06</span>
          <small>CORE CAPABILITIES</small>
        </div>
      </section>

      <section className="features-list-section">
        <div className="features-section-heading">
          <div>
            <span className="home-eyebrow">CAPABILITIES</span>
            <h2>Built around your organization's security workflow.</h2>
          </div>

          <span className="features-heading-index">/ 06</span>
        </div>

        <div className="features-grid">
          {features.map((feature) => (
            <article className="feature-card" key={feature.number}>
              <div className="feature-card-top">
                <span className="feature-number">{feature.number}</span>

                <span className="feature-arrow" aria-hidden="true">
                  ↗
                </span>
              </div>

              <div className="feature-card-content">
                <h3>{feature.title}</h3>

                <p>{feature.description}</p>
              </div>

              <div className="feature-card-line" aria-hidden="true" />
            </article>
          ))}
        </div>
      </section>

      <section className="features-bottom">
        <div className="features-bottom-panel">
          <div className="features-bottom-content">
            <span className="home-eyebrow">ONE PLATFORM</span>

            <h2>
              From detection
              <span> to response.</span>
            </h2>

            <p>
              Connect security information across your organization and create
              one consistent view of your cybersecurity environment.
            </p>
          </div>

          <div className="features-bottom-index" aria-hidden="true">
            <span>CG</span>
            <strong>01</strong>
          </div>
        </div>
      </section>
    </div>
  );
}