import { useState, type ReactNode } from "react";
import { NavLink } from "react-router-dom";

import Sidebar from "../components/Sidebar";
import ThemeToggle from "../components/ThemeToggle";

interface AuthenticatedLayoutProps {
  children: ReactNode;
}

export default function AuthenticatedLayout({
  children,
}: AuthenticatedLayoutProps) {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <div className="authenticated-layout">
      <Sidebar />

      <div className="authenticated-content">
        <header className="organization-topbar">
          <div className="topbar-left">
            <button
              type="button"
              className="mobile-menu-button"
              onClick={() => setMobileSidebarOpen(true)}
              aria-label="Open navigation"
              aria-expanded={mobileSidebarOpen}
            >
              <span />
              <span />
              <span />
            </button>

            <div className="organization-heading">
              <span className="organization-heading-label">
                Organization Portal
              </span>

              <span className="organization-heading-divider">/</span>

              <span className="organization-heading-current">
                Dashboard
              </span>
            </div>
          </div>

          <div className="topbar-actions">
            <ThemeToggle />

            <NavLink to="/settings" className="topbar-settings">
              Settings
            </NavLink>
          </div>
        </header>

        <main className="authenticated-main">{children}</main>
      </div>

      <button
        type="button"
        className={`mobile-sidebar-overlay ${
          mobileSidebarOpen ? "visible" : ""
        }`}
        onClick={() => setMobileSidebarOpen(false)}
        aria-label="Close navigation"
      />

      <div
        className={`mobile-sidebar ${
          mobileSidebarOpen ? "open" : ""
        }`}
      >
        <Sidebar />
      </div>
    </div>
  );
}