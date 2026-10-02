import { useState } from "react";
import { NavLink } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";

interface NavigationItem {
  label: string;
  path: string;
  icon: string;
}

const mainNavigation: NavigationItem[] = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: "▦",
  },
  {
    label: "Threat Center",
    path: "/threats",
    icon: "◈",
  },
  {
    label: "Incidents",
    path: "/incidents",
    icon: "◇",
  },
  {
    label: "Cyber Score",
    path: "/cyber-score",
    icon: "◉",
  },
];

const organizationNavigation: NavigationItem[] = [
  {
    label: "Departments",
    path: "/departments",
    icon: "▤",
  },
  {
    label: "Employees",
    path: "/employees",
    icon: "◎",
  },
  {
    label: "Devices",
    path: "/devices",
    icon: "▣",
  },
  {
    label: "Policies",
    path: "/policies",
    icon: "▥",
  },
];

const secondaryNavigation: NavigationItem[] = [
  {
    label: "Settings",
    path: "/settings",
    icon: "⚙",
  },
];

interface SidebarProps {
  onSignOut?: () => void;
}

export default function Sidebar({ onSignOut }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  const renderNavigation = (items: NavigationItem[]) => (
    <ul className="sidebar-navigation-list">
      {items.map((item) => (
        <li key={item.path}>
          <NavLink
            to={item.path}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
            title={collapsed ? item.label : undefined}
          >
            <span className="sidebar-link-icon" aria-hidden="true">
              {item.icon}
            </span>

            {!collapsed && (
              <span className="sidebar-link-label">{item.label}</span>
            )}
          </NavLink>
        </li>
      ))}
    </ul>
  );

  return (
    <aside className={`organization-sidebar ${collapsed ? "collapsed" : ""}`}>
      <div className="sidebar-header">
        <NavLink to="/dashboard" className="sidebar-brand">
          <span className="sidebar-brand-mark">C</span>

          {!collapsed && (
            <span className="sidebar-brand-name">CyberGuard</span>
          )}
        </NavLink>

        <button
          type="button"
          className="sidebar-collapse-button"
          onClick={() => setCollapsed((value) => !value)}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? "›" : "‹"}
        </button>
      </div>

      <div className="sidebar-content">
        <section className="sidebar-section">
          {!collapsed && (
            <h2 className="sidebar-section-title">Main</h2>
          )}

          {renderNavigation(mainNavigation)}
        </section>

        <section className="sidebar-section">
          {!collapsed && (
            <h2 className="sidebar-section-title">Organization</h2>
          )}

          {renderNavigation(organizationNavigation)}
        </section>

        <section className="sidebar-section sidebar-section-bottom">
          {renderNavigation(secondaryNavigation)}

          <button
            type="button"
            className="sidebar-link sidebar-signout"
            onClick={onSignOut}
            title={collapsed ? "Sign Out" : undefined}
          >
            <span className="sidebar-link-icon" aria-hidden="true">
              ↪
            </span>

            {!collapsed && (
              <span className="sidebar-link-label">Sign Out</span>
            )}
          </button>

          <div className="sidebar-theme">
            <ThemeToggle />
          </div>
        </section>
      </div>
    </aside>
  );
}