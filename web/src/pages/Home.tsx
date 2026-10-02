import { NavLink } from "react-router-dom";

const highlights = [
  {
    number: "01",
    title: "Unified Protection",
    description:
      "Bring multiple cybersecurity detection capabilities together through one organization-focused platform.",
  },
  {
    number: "02",
    title: "Threat Visibility",
    description:
      "Monitor security events, incidents, devices, and organizational risk from a centralized workspace.",
  },
  {
    number: "03",
    title: "Actionable Insights",
    description:
      "Turn security analysis into clear information that helps organizations understand their current security posture.",
  },
];

export default function Home() {
  return (
    <div className="home-page">
      <section className="home-hero">
        <div className="home-hero-content">
          <span className="home-eyebrow">ORGANIZATIONAL CYBERSECURITY</span>

          <h1>
            Security that keeps
            <span> your organization ahead.</span>
          </h1>

          <p>
            CyberGuard is a unified cybersecurity platform designed to detect
            threats, monitor organizational security, and provide a clearer
            view of your digital risk.
          </p>

          <div className="home-hero-actions">
            <NavLink to="/register" className="button button-primary">
              Protect Your Organization
            </NavLink>

            <NavLink to="/how-it-works" className="button button-secondary">
              See How It Works
            </NavLink>
          </div>
        </div>

        <div className="home-hero-visual" aria-hidden="true">
          <div className="security-grid" />

          <div className="security-card security-card-main">
            <div className="security-card-header">
              <span>SECURITY STATUS</span>
              <span className="security-status-dot" />
            </div>

            <div className="security-score">SECURE</div>

            <div className="security-line">
              <span />
            </div>

            <div className="security-card-footer">
              <span>Continuous monitoring</span>
              <span>24/7</span>
            </div>
          </div>

          <div className="security-card security-card-small">
            <span className="security-small-label">THREATS</span>
            <strong>MONITORED</strong>
          </div>
        </div>
      </section>

      <section className="home-highlights">
        <div className="home-section-heading">
          <span className="home-eyebrow">WHY CYBERGUARD</span>
          <h2>A single view of your security landscape.</h2>
        </div>

        <div className="home-highlight-grid">
          {highlights.map((item) => (
            <article className="home-highlight-card" key={item.number}>
              <span className="home-highlight-number">{item.number}</span>

              <h3>{item.title}</h3>

              <p>{item.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="home-cta">
        <div>
          <span className="home-eyebrow">GET STARTED</span>
          <h2>Build a stronger security posture.</h2>
          <p>
            Explore the CyberGuard platform and prepare your organization for
            modern cybersecurity challenges.
          </p>
        </div>

        <NavLink to="/register" className="button button-primary">
          Create Organization
        </NavLink>
      </section>
    </div>
  );
}