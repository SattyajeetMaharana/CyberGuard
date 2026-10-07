import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { NavLink, useNavigate } from "react-router-dom";

import { ApiError } from "../services/api";
import { useAuth } from "../context/AuthContext";

function getLoginErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "Invalid email or password.";
    }

    if (error.status >= 500) {
      return "The CyberGuard server is currently unavailable. Please try again.";
    }

    return error.message || "Unable to sign in. Please try again.";
  }

  if (error instanceof TypeError) {
    return "Unable to connect to CyberGuard. Check your network connection.";
  }

  return "Something went wrong while signing in. Please try again.";
}

export default function Login() {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isEntering, setIsEntering] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    return () => {
      document.body.classList.remove("auth-transition-active");
    };
  }, []);

  useEffect(() => {
    if (isAuthenticated && !isEntering) {
      navigate("/dashboard", { replace: true });
    }
  }, [isAuthenticated, isEntering, navigate]);

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (isSubmitting || isEntering) {
      return;
    }

    setErrorMessage("");
    setIsSubmitting(true);

    try {
      await login(email.trim(), password);

      setIsEntering(true);
      document.body.classList.add("auth-transition-active");

      window.setTimeout(() => {
        navigate("/dashboard", {
          replace: true,
          state: {
            fromLogin: true,
          },
        });
      }, 850);
    } catch (error) {
      setErrorMessage(getLoginErrorMessage(error));
      setIsSubmitting(false);
    }
  };

  const isBusy = isSubmitting || isEntering;

  return (
    <>
      <div
        className={`auth-page ${
          isEntering ? "auth-page-transitioning" : ""
        }`}
      >
        <div className="auth-container">
          <section className="auth-intro">
            <div className="auth-intro-top">
              <span className="home-eyebrow">
                CYBERGUARD ORGANIZATION
              </span>

              <span className="auth-system-status">
                <span className="auth-status-dot" />
                SYSTEM ONLINE
              </span>
            </div>

            <div className="auth-intro-main">
              <span className="auth-index">/ 01</span>

              <h1>
                Welcome
                <span>back.</span>
              </h1>

              <p>
                Sign in to access your organization's cybersecurity
                workspace, monitor threats, and manage your security
                environment.
              </p>
            </div>

            <div className="auth-intro-line">
              <span />
              <span />
              <span />
            </div>

            <div className="auth-security-info">
              <div>
                <span>ACCESS LEVEL</span>
                <strong>ORGANIZATION</strong>
              </div>

              <div>
                <span>SECURITY</span>
                <strong>PROTECTED</strong>
              </div>
            </div>
          </section>

          <section className="auth-card">
            <div className="auth-card-heading">
              <div className="auth-card-topline">
                <span className="auth-card-label">
                  SECURE ACCESS
                </span>

                <span className="auth-card-number">
                  CG-AUTH
                </span>
              </div>

              <h2>
                {isEntering
                  ? "Entering workspace"
                  : "Sign in"}
              </h2>

              <p>
                {isEntering
                  ? "Preparing your secure organization workspace."
                  : "Enter your organization credentials to continue."}
              </p>
            </div>

            {errorMessage && !isEntering && (
              <div
                className="auth-error"
                role="alert"
              >
                <span className="auth-error-indicator">
                  !
                </span>

                <div>
                  <strong>Sign-in failed</strong>
                  <p>{errorMessage}</p>
                </div>
              </div>
            )}

            <form
              className={`auth-form ${
                isBusy ? "auth-form-disabled" : ""
              }`}
              onSubmit={handleSubmit}
            >
              <div className="auth-field">
                <label htmlFor="login-email">
                  Organization email
                </label>

                <div className="auth-input-wrapper">
                  <span className="auth-input-index">
                    01
                  </span>

                  <input
                    id="login-email"
                    type="email"
                    value={email}
                    onChange={(event) => {
                      setEmail(event.target.value);

                      if (errorMessage) {
                        setErrorMessage("");
                      }
                    }}
                    placeholder="you@organization.com"
                    autoComplete="email"
                    disabled={isBusy}
                    required
                  />
                </div>
              </div>

              <div className="auth-field">
                <label htmlFor="login-password">
                  Password
                </label>

                <div className="auth-input-wrapper">
                  <span className="auth-input-index">
                    02
                  </span>

                  <input
                    id="login-password"
                    type={
                      showPassword ? "text" : "password"
                    }
                    value={password}
                    onChange={(event) => {
                      setPassword(event.target.value);

                      if (errorMessage) {
                        setErrorMessage("");
                      }
                    }}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    disabled={isBusy}
                    required
                  />

                  <button
                    type="button"
                    className="auth-password-toggle"
                    onClick={() =>
                      setShowPassword(
                        (current) => !current,
                      )
                    }
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                    disabled={isBusy}
                  >
                    {showPassword ? "HIDE" : "SHOW"}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                className={`button button-primary auth-submit ${
                  isEntering
                    ? "auth-submit-loading"
                    : ""
                }`}
                disabled={isBusy}
              >
                {isSubmitting && !isEntering ? (
                  <>
                    <span className="auth-submit-loader" />
                    <span>Authenticating</span>
                  </>
                ) : isEntering ? (
                  <>
                    <span className="auth-submit-loader" />
                    <span>Entering Workspace</span>
                  </>
                ) : (
                  <>
                    <span>Sign In</span>
                    <span aria-hidden="true">↗</span>
                  </>
                )}
              </button>
            </form>

            {!isBusy && (
              <>
                <div className="auth-divider">
                  <span />
                  <span>OR</span>
                  <span />
                </div>

                <p className="auth-register-text">
                  Don't have an organization account?{" "}
                  <NavLink to="/register">
                    Create one
                  </NavLink>
                </p>

                <NavLink
                  to="/"
                  className="auth-back-link"
                >
                  <span aria-hidden="true">←</span>
                  Back to CyberGuard
                </NavLink>
              </>
            )}

            {isEntering && (
              <div className="auth-transition-status">
                <div className="auth-transition-status-line">
                  <span className="auth-transition-pulse" />
                  <span>
                    SECURE SESSION INITIALIZING
                  </span>
                </div>

                <div className="auth-transition-progress">
                  <span />
                </div>

                <div className="auth-transition-meta">
                  <span>CYBERGUARD</span>
                  <span>
                    AUTH → ORGANIZATION
                  </span>
                </div>
              </div>
            )}

            <div className="auth-card-footer">
              <span>CYBERGUARD</span>
              <span>
                SECURE ORGANIZATIONAL ACCESS
              </span>
            </div>
          </section>
        </div>
      </div>

      {isEntering && (
        <div
          className="auth-entry-overlay"
          aria-hidden="true"
        >
          <div className="auth-entry-logo">
            <div className="auth-entry-ring auth-entry-ring-one" />
            <div className="auth-entry-ring auth-entry-ring-two" />

            <div className="auth-entry-core">
              <span />
            </div>
          </div>

          <div className="auth-entry-label">
            <span>CYBERGUARD</span>
            <strong>SECURE ACCESS</strong>
          </div>
        </div>
      )}
    </>
  );
}