import { useState, type ReactNode } from "react";
import { NavLink, useLocation } from "react-router-dom";

import Sidebar from "../components/Sidebar";
import ThemeToggle from "../components/ThemeToggle";

interface AuthenticatedLayoutProps {
  children: ReactNode;
}

const getPageName = (pathname: string): string => {
  const pages: Record<string, string> = {
    "/dashboard": "Overview",
    "/threats": "Threat Center",
    "/incidents": "Incidents",
    "/cyber-score": "Cyber Score",
    "/departments": "Departments",
    "/employees": "Employees",
    "/devices": "Devices",
    "/policies": "Policies",
    "/settings": "Settings",
  };

  return pages[pathname] ?? "Organization Portal";
};

export default function AuthenticatedLayout({
  children,
}: AuthenticatedLayoutProps) {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const location = useLocation();

  const currentPage = getPageName(location.pathname);

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
                CYBERGUARD
              </span>

              <span className="organization-heading-divider">
                /
              </span>

              <span className="organization-heading-current">
                {currentPage}
              </span>
            </div>
          </div>

          <div className="topbar-actions">
            <div className="topbar-security-status">
              <span className="topbar-status-dot" />
              <span>MONITORING ACTIVE</span>
            </div>

            <ThemeToggle />

            <NavLink
              to="/settings"
              className="topbar-settings"
              aria-label="Open settings"
            >
              ⚙
            </NavLink>
          </div>
        </header>

        <main className="authenticated-main">
          {children}
        </main>
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