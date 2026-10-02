import { useState } from "react";
import type { FormEvent } from "react";
import { NavLink } from "react-router-dom";

export default function Register() {
  const [organization, setOrganization] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
  };

  return (
    <div className="auth-page">
      <div className="auth-container register-container">
        <section className="auth-intro">
          <span className="home-eyebrow">CYBERGUARD ORGANIZATION</span>

          <h1>
            Build your
            <span> security workspace.</span>
          </h1>

          <p>
            Create an organization account to bring your security monitoring,
            threat visibility, and organizational controls together in one
            workspace.
          </p>

          <div className="auth-intro-line">
            <span />
            <span />
            <span />
          </div>
        </section>

        <section className="auth-card">
          <div className="auth-card-heading">
            <span className="auth-card-label">CREATE WORKSPACE</span>

            <h2>Register</h2>

            <p>Set up your organization account to get started.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <label htmlFor="register-organization">
              Organization name
            </label>

            <input
              id="register-organization"
              type="text"
              value={organization}
              onChange={(event) => setOrganization(event.target.value)}
              placeholder="Your organization"
              autoComplete="organization"
              required
            />

            <label htmlFor="register-name">
              Administrator name
            </label>

            <input
              id="register-name"
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Your full name"
              autoComplete="name"
              required
            />

            <label htmlFor="register-email">
              Organization email
            </label>

            <input
              id="register-email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@organization.com"
              autoComplete="email"
              required
            />

            <label htmlFor="register-password">
              Password
            </label>

            <input
              id="register-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Create a password"
              autoComplete="new-password"
              required
            />

            <button
              type="submit"
              className="button button-primary auth-submit"
            >
              Create Organization
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
            ← Back to CyberGuard
          </NavLink>
        </section>
      </div>
    </div>
  );
}