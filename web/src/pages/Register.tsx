import { useState } from "react";
import type { FormEvent } from "react";
import { NavLink } from "react-router-dom";

export default function Register() {
  const [organization, setOrganization] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
  };

  return (
    <div className="auth-page">
      <div className="auth-container register-container">
        <section className="auth-intro">
          <div className="auth-intro-top">
            <span className="home-eyebrow">CYBERGUARD ORGANIZATION</span>

            <span className="auth-system-status">
              <span className="auth-status-dot" />
              SECURE SETUP
            </span>
          </div>

          <div className="auth-intro-main">
            <span className="auth-index">/ 02</span>

            <h1>
              Build your
              <span>security workspace.</span>
            </h1>

            <p>
              Create an organization account to bring your security monitoring,
              threat visibility, and organizational controls together in one
              workspace.
            </p>
          </div>

          <div className="auth-intro-line">
            <span />
            <span />
            <span />
          </div>

          <div className="auth-security-info">
            <div>
              <span>WORKSPACE</span>
              <strong>ORGANIZATION</strong>
            </div>

            <div>
              <span>SETUP</span>
              <strong>SECURE</strong>
            </div>
          </div>
        </section>

        <section className="auth-card">
          <div className="auth-card-heading">
            <div className="auth-card-topline">
              <span className="auth-card-label">CREATE WORKSPACE</span>
              <span className="auth-card-number">CG-REG</span>
            </div>

            <h2>Register</h2>

            <p>
              Set up your organization account to get started.
            </p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-field">
              <label htmlFor="register-organization">
                Organization name
              </label>

              <div className="auth-input-wrapper">
                <span className="auth-input-index">01</span>

                <input
                  id="register-organization"
                  type="text"
                  value={organization}
                  onChange={(event) => setOrganization(event.target.value)}
                  placeholder="Your organization"
                  autoComplete="organization"
                  required
                />
              </div>
            </div>

            <div className="auth-field">
              <label htmlFor="register-name">
                Administrator name
              </label>

              <div className="auth-input-wrapper">
                <span className="auth-input-index">02</span>

                <input
                  id="register-name"
                  type="text"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Your full name"
                  autoComplete="name"
                  required
                />
              </div>
            </div>

            <div className="auth-field">
              <label htmlFor="register-email">
                Organization email
              </label>

              <div className="auth-input-wrapper">
                <span className="auth-input-index">03</span>

                <input
                  id="register-email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@organization.com"
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            <div className="auth-field">
              <label htmlFor="register-password">
                Password
              </label>

              <div className="auth-input-wrapper">
                <span className="auth-input-index">04</span>

                <input
                  id="register-password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Create a password"
                  autoComplete="new-password"
                  required
                />

                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowPassword((current) => !current)}
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword ? "HIDE" : "SHOW"}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="button button-primary auth-submit"
            >
              <span>Create Organization</span>
              <span aria-hidden="true">↗</span>
            </button>
          </form>

          <div className="auth-divider">
            <span />
            <span>OR</span>
            <span />
          </div>

          <p className="auth-register-text">
            Already have an organization account?{" "}
            <NavLink to="/login">Sign in</NavLink>
          </p>

          <NavLink to="/" className="auth-back-link">
            <span aria-hidden="true">←</span>
            Back to CyberGuard
          </NavLink>

          <div className="auth-card-footer">
            <span>CYBERGUARD</span>
            <span>SECURE ORGANIZATIONAL SETUP</span>
          </div>
        </section>
      </div>
    </div>
  );
}