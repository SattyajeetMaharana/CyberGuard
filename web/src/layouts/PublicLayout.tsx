import type { ReactNode } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";

interface PublicLayoutProps {
  children: ReactNode;
}

export default function PublicLayout({ children }: PublicLayoutProps) {
  return (
    <div className="public-layout">
      <Header />

      <main className="public-main">
        {children}
      </main>

      <Footer />
    </div>
  );
}