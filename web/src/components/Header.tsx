import { NavLink } from "react-router-dom";

import CyberGuardLogo from "./CyberGuardLogo";
import ThemeToggle from "./ThemeToggle";

const navigation = [
  { label: "Home", path: "/" },
  { label: "Features", path: "/features" },
  { label: "How It Works", path: "/how-it-works" },
  { label: "Download", path: "/download" },
];

export default function Header() {
  return (
    <header className="site-header">
      <div className="header-container">
        <CyberGuardLogo className="site-header-logo" />

        <nav className="desktop-nav" aria-label="Main navigation">
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="header-actions">
          <ThemeToggle />

          <NavLink to="/login" className="login-link">
            Login
          </NavLink>

          <NavLink to="/register" className="register-button">
            Register
          </NavLink>
        </div>
      </div>
    </header>
  );
}