import type { ReactNode } from "react";

interface OrganizationSectionProps {
  eyebrow: string;
  title: string;
  description: string;
  actionLabel?: string;
  children?: ReactNode;
}

export default function OrganizationSection({
  eyebrow,
  title,
  description,
  actionLabel,
  children,
}: OrganizationSectionProps) {
  return (
    <div className="organization-section">
      <header className="organization-section-header">
        <div>
          <span className="organization-section-eyebrow">{eyebrow}</span>

          <h1>{title}</h1>

          <p>{description}</p>
        </div>

        {actionLabel && (
          <button type="button" className="button button-primary">
            {actionLabel}
          </button>
        )}
      </header>

      {children}
    </div>
  );
}