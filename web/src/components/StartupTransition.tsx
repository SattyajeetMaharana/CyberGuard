import { useEffect, useState, type ReactNode } from "react";

import CyberGuardLogo from "./CyberGuardLogo";
import { useTheme } from "../context/ThemeContext";

interface StartupTransitionProps {
  children: ReactNode;
}

export default function StartupTransition({
  children,
}: StartupTransitionProps) {
  const { theme } = useTheme();

  const [showIntro, setShowIntro] = useState(true);
  const [logoVisible, setLogoVisible] = useState(false);
  const [logoLeaving, setLogoLeaving] = useState(false);

  useEffect(() => {
    setShowIntro(true);
    setLogoVisible(false);
    setLogoLeaving(false);

    const logoTimer = window.setTimeout(() => {
      setLogoVisible(true);
    }, 50);

    const leaveTimer = window.setTimeout(() => {
      setLogoLeaving(true);
    }, 900);

    const finishTimer = window.setTimeout(() => {
      setShowIntro(false);
    }, 1350);

    return () => {
      window.clearTimeout(logoTimer);
      window.clearTimeout(leaveTimer);
      window.clearTimeout(finishTimer);
    };
  }, []);

  return (
    <>
      <div
        className={`startup-transition startup-transition-${theme} ${
          showIntro ? "startup-transition-active" : ""
        }`}
      >
        <div
          className={`startup-logo ${
            logoVisible ? "startup-logo-visible" : ""
          } ${
            logoLeaving ? "startup-logo-leaving" : ""
          }`}
        >
          <CyberGuardLogo
            className="startup-logo-link"
            aria-label="CyberGuard"
          />
        </div>
      </div>

      <div
        className={`startup-content ${
          !showIntro ? "startup-content-visible" : ""
        }`}
      >
        {children}
      </div>
    </>
  );
}