import { NavLink } from "react-router-dom";

import CyberGuardLogo from "../components/CyberGuardLogo";
import introVideo from "../assets/intro.mp4";

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
          <div className="home-hero-intro">
            <span className="home-eyebrow">
              ORGANIZATIONAL CYBERSECURITY
            </span>

            <h1>
              Security that keeps
              <span>your organization ahead.</span>
            </h1>

            <p>
              CyberGuard is a unified cybersecurity platform designed
              to detect threats, monitor organizational security, and
              provide a clearer view of your digital risk.
            </p>

            <div className="home-hero-actions">
              <NavLink
                to="/register"
                className="button button-primary"
              >
                Protect Your Organization
              </NavLink>

              <NavLink
                to="/how-it-works"
                className="button button-secondary"
              >
                See How It Works
              </NavLink>
            </div>
          </div>

          <div className="home-hero-meta">
            <span>ONE PLATFORM</span>
            <span className="home-hero-meta-line" />
            <span>CONTINUOUS VISIBILITY</span>
          </div>
        </div>

        <div className="home-hero-visual home-hero-video">
          <video
            className="home-intro-video"
            src={introVideo}
            autoPlay
            muted
            loop
            playsInline
            preload="auto"
            aria-hidden="true"
          />

          <div className="home-video-overlay" />

          <div className="home-video-brand">
            <div className="home-video-brand-logo">
              <CyberGuardLogo className="home-video-logo" />
            </div>

            <div className="home-video-brand-text">
              <span>CYBERGUARD</span>
              <strong>SECURITY SYSTEM</strong>
            </div>
          </div>

          <div className="home-video-status">
            <span className="home-video-status-dot" />
            LIVE PROTECTION
          </div>

          <div className="home-video-frame-line home-video-frame-line-top" />
          <div className="home-video-frame-line home-video-frame-line-bottom" />
        </div>
      </section>

      <section className="home-highlights">
        <div className="home-section-heading">
          <span className="home-eyebrow">
            WHY CYBERGUARD
          </span>

          <h2>
            A single view of your security landscape.
          </h2>
        </div>

        <div className="home-highlight-grid">
          {highlights.map((item) => (
            <article
              className="home-highlight-card"
              key={item.number}
            >
              <div className="home-highlight-top">
                <span className="home-highlight-number">
                  {item.number}
                </span>

                <span className="home-highlight-arrow">
                  ↗
                </span>
              </div>

              <div>
                <h3>{item.title}</h3>

                <p>{item.description}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="home-cta">
        <div className="home-cta-content">
          <span className="home-eyebrow">
            GET STARTED
          </span>

          <h2>
            Build a stronger security posture.
          </h2>

          <p>
            Explore the CyberGuard platform and prepare your
            organization for modern cybersecurity challenges.
          </p>
        </div>

        <NavLink
          to="/register"
          className="button button-primary home-cta-button"
        >
          Create Organization
        </NavLink>
      </section>
    </div>
  );
}