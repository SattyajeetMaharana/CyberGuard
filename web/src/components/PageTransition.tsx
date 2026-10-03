import {
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useLocation } from "react-router-dom";

interface PageTransitionProps {
  children: ReactNode;
}

export default function PageTransition({
  children,
}: PageTransitionProps) {
  const location = useLocation();

  const [content, setContent] = useState(children);
  const [phase, setPhase] = useState<
    "idle" | "leaving" | "entering"
  >("idle");

  useEffect(() => {
    setPhase("leaving");

    const swapTimer = window.setTimeout(() => {
      setContent(children);
      setPhase("entering");
    }, 180);

    const finishTimer = window.setTimeout(() => {
      setPhase("idle");
    }, 560);

    return () => {
      window.clearTimeout(swapTimer);
      window.clearTimeout(finishTimer);
    };
  }, [location.pathname]);

  return (
    <div
      className={`page-transition page-transition-${phase}`}
    >
      {content}
    </div>
  );
}