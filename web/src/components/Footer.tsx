import { NavLink } from "react-router-dom";

const footerLinks = [
  { label: "Home", path: "/" },
  { label: "Features", path: "/features" },
  { label: "How It Works", path: "/how-it-works" },
  { label: "Download", path: "/download" },
];

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-container">
        <div className="footer-main">
          <div className="footer-brand">
            <NavLink to="/" className="footer-logo">
              <span className="footer-logo-mark">C</span>
              <span>CyberGuard</span>
            </NavLink>

            <p className="footer-description">
              Unified cybersecurity protection for individuals and
              organizations.
            </p>
          </div>

          <nav className="footer-navigation" aria-label="Footer navigation">
            <span className="footer-heading">Explore</span>

            {footerLinks.map((link) => (
              <NavLink key={link.path} to={link.path}>
                {link.label}
              </NavLink>
            ))}
          </nav>

          <div className="footer-navigation">
            <span className="footer-heading">Organization</span>

            <NavLink to="/login">Login</NavLink>
            <NavLink to="/register">Register</NavLink>
          </div>
        </div>

        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} CyberGuard</span>
          <span>Cybersecurity. Simplified.</span>
        </div>
      </div>
    </footer>
  );
}