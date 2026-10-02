import type { ReactNode } from "react";

interface PublicLayoutProps {
  children: ReactNode;
}

export default function PublicLayout({ children }: PublicLayoutProps) {
  return (
    <div className="min-h-screen">
      <header>
        <nav>
          <strong>CyberGuard</strong>
        </nav>
      </header>

      <main>{children}</main>

      <footer>
        <p>CyberGuard</p>
      </footer>
    </div>
  );
}