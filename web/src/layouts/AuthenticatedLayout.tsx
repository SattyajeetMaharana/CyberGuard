import type { ReactNode } from "react";

interface AuthenticatedLayoutProps {
  children: ReactNode;
}

export default function AuthenticatedLayout({
  children,
}: AuthenticatedLayoutProps) {
  return (
    <div className="min-h-screen">
      <aside>
        <nav>
          <strong>CyberGuard</strong>

          <ul>
            <li>Dashboard</li>
            <li>Threat Center</li>
            <li>Incidents</li>
            <li>Cyber Score</li>
          </ul>
        </nav>
      </aside>

      <section>
        <header>
          <p>Organization Portal</p>
        </header>

        <main>{children}</main>
      </section>
    </div>
  );
}