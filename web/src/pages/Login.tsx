import { useState } from "react";
import type { FormEvent } from "react";
import { NavLink } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <section className="auth-intro">
          <span className="home-eyebrow">CYBERGUARD ORGANIZATION</span>

          <h1>
            Welcome
            <span> back.</span>
          </h1>

          <p>
            Sign in to access your organization's cybersecurity workspace,
            monitor threats, and manage your security environment.
          </p>

          <div className="auth-intro-line">
            <span />
            <span />
            <span />
          </div>
        </section>

        <section className="auth-card">
          <div className="auth-card-heading">
            <span className="auth-card-label">SECURE ACCESS</span>

            <h2>Sign in</h2>

            <p>Enter your organization credentials to continue.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <label htmlFor="login-email">
              Organization email
            </label>

            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@organization.com"
              autoComplete="email"
              required
            />

            <label htmlFor="login-password">
              Password
            </label>

            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              autoComplete="current-password"
              required
            />

            <button type="submit" className="button button-primary auth-submit">
              Sign In
            </button>
          </form>

          <div className="auth-divider">
            <span />
            <span>OR</span>
            <span />
          </div>

          <p className="auth-register-text">
            Don't have an organization account?{" "}
            <NavLink to="/register">Create one</NavLink>
          </p>

          <NavLink to="/" className="auth-back-link">
            ← Back to CyberGuard
          </NavLink>
        </section>
      </div>
    </div>
  );
}