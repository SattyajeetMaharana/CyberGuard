import { NavLink } from "react-router-dom";

import logo from "../assets/logo.png";

interface CyberGuardLogoProps {
  to?: string;
  className?: string;
  showName?: boolean;
  alt?: string;
}

export default function CyberGuardLogo({
  to = "/",
  className = "",
  showName = false,
  alt = "CyberGuard",
}: CyberGuardLogoProps) {
  return (
    <NavLink
      to={to}
      className={`cyberguard-logo ${className}`.trim()}
      aria-label="CyberGuard Home"
    >
      <img
        src={logo}
        alt={alt}
        className="cyberguard-logo-image"
        draggable={false}
      />

      {showName && (
        <span className="cyberguard-logo-name">
          CyberGuard
        </span>
      )}
    </NavLink>
  );
}