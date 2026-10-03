import { NavLink } from "react-router-dom";

const platforms = [
  {
    label: "Mobile",
    title: "Protect Me",
    description:
      "A personal cybersecurity experience designed to help users identify and respond to potential digital threats.",
    status: "Available",
  },
  {
    label: "Web",
    title: "Protect My Organization",
    description:
      "A centralized web workspace for organizations to monitor threats, manage security, and understand their cybersecurity posture.",
    status: "Web Platform",
  },
];

const requirements = [
  "Internet connection",
  "Modern supported browser",
  "Organization account for the web portal",
];

export default function Download() {
  return (
    <div className="download-page">
      <section className="download-hero">
        <div className="download-hero-content">
          <span className="home-eyebrow">
            CYBERGUARD ACCESS
          </span>

          <h1>
            Security wherever
            <span>you need it.</span>
          </h1>

          <p>
            Access CyberGuard through the platform designed for your
            security needs. Protect personal devices with the mobile
            experience or manage organizational security through the
            web platform.
          </p>

          <div className="download-counter">
            <span className="download-counter-label">
              PLATFORM ACTIVITY
            </span>

            <div className="download-counter-value">
              <span className="download-counter-number">
                10,000
              </span>

              <span className="download-counter-plus">
                +
              </span>
            </div>

            <span className="download-counter-caption">
              SECURITY CONNECTIONS
            </span>
          </div>
        </div>

        <div className="download-hero-stat">
          <span className="download-hero-stat-label">
            CYBERGUARD
          </span>

          <strong>ONE</strong>

          <span>
            UNIFIED SECURITY
            <br />
            ECOSYSTEM
          </span>
        </div>
      </section>

      <section className="download-platforms">
        <div className="download-section-heading">
          <span className="home-eyebrow">
            CHOOSE YOUR PLATFORM
          </span>

          <h2>
            One ecosystem. Two experiences.
          </h2>
        </div>

        <div className="download-platform-grid">
          {platforms.map((platform) => (
            <article
              className="download-platform-card"
              key={platform.title}
            >
              <div className="download-platform-top">
                <span className="download-platform-label">
                  {platform.label}
                </span>

                <span className="download-platform-status">
                  {platform.status}
                </span>
              </div>

              <h3>{platform.title}</h3>

              <p>{platform.description}</p>

              {platform.label === "Web" ? (
                <NavLink
                  to="/login"
                  className="button button-primary download-platform-button"
                >
                  Open Web Platform
                </NavLink>
              ) : (
                <button
                  type="button"
                  className="button button-secondary download-platform-button"
                  disabled
                >
                  Coming Soon
                </button>
              )}
            </article>
          ))}
        </div>
      </section>

      <section className="download-requirements">
        <div>
          <span className="home-eyebrow">
            REQUIREMENTS
          </span>

          <h2>
            Simple to get started.
          </h2>

          <p>
            CyberGuard is designed to keep access straightforward
            while providing the infrastructure required for
            cybersecurity analysis and organizational monitoring.
          </p>
        </div>

        <ul>
          {requirements.map((requirement, index) => (
            <li key={requirement}>
              <span>
                {String(index + 1).padStart(2, "0")}
              </span>

              {requirement}
            </li>
          ))}
        </ul>
      </section>

      <section className="download-cta">
        <span className="home-eyebrow">
          ORGANIZATIONS
        </span>

        <h2>
          Ready to secure your organization?
        </h2>

        <p>
          Create an organization workspace and start building a
          centralized view of your cybersecurity environment.
        </p>

        <NavLink
          to="/register"
          className="button button-primary"
        >
          Create Organization
        </NavLink>
      </section>
    </div>
  );
}