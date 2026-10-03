import { useState } from "react";

type ThreatSeverity = "Critical" | "High" | "Medium";

type Threat = {
  id: string;
  type: string;
  source: string;
  severity: ThreatSeverity;
  time: string;
};

type ThreatVote = "Confirmed Threat" | "False Positive" | "Needs Review";

const threats: Threat[] = [
  {
    id: "THR-001",
    type: "Phishing URL",
    source: "Web Analysis",
    severity: "Critical",
    time: "10:42 AM",
  },
  {
    id: "THR-002",
    type: "Suspicious QR Code",
    source: "QR Analysis",
    severity: "High",
    time: "09:36 AM",
  },
  {
    id: "THR-003",
    type: "Malicious File",
    source: "File Analysis",
    severity: "High",
    time: "09:12 AM",
  },
  {
    id: "THR-004",
    type: "Suspicious Activity",
    source: "Behavior Analysis",
    severity: "Medium",
    time: "08:48 AM",
  },
];

const voteOptions: ThreatVote[] = [
  "Confirmed Threat",
  "False Positive",
  "Needs Review",
];

export default function Threats() {
  const [selectedThreat, setSelectedThreat] = useState<Threat | null>(null);
  const [votes, setVotes] = useState<Record<string, ThreatVote>>({});

  const selectedVote = selectedThreat
    ? votes[selectedThreat.id]
    : undefined;

  const handleVote = (vote: ThreatVote) => {
    if (!selectedThreat) {
      return;
    }

    setVotes((current) => ({
      ...current,
      [selectedThreat.id]: vote,
    }));
  };

  const closeThreatPanel = () => {
    setSelectedThreat(null);
  };

  return (
    <div className="organization-section">
      <header className="organization-section-header">
        <div>
          <span className="organization-section-eyebrow">
            SECURITY MONITORING
          </span>

          <h1>Threat Center</h1>

          <p>
            Monitor detected threats and review security events across your
            organization.
          </p>
        </div>

        <button type="button" className="button button-secondary">
          Export Report
        </button>
      </header>

      <section className="threat-stat-grid">
        <article className="organization-stat-card">
          <span>Total Threats</span>
          <strong>12</strong>
          <p>Detected today</p>
        </article>

        <article className="organization-stat-card">
          <span>Critical</span>
          <strong>02</strong>
          <p>Immediate attention</p>
        </article>

        <article className="organization-stat-card">
          <span>High</span>
          <strong>04</strong>
          <p>Requires review</p>
        </article>

        <article className="organization-stat-card">
          <span>Resolved</span>
          <strong>08</strong>
          <p>Handled threats</p>
        </article>
      </section>

      <section className="organization-panel threat-table-panel">
        <div className="organization-panel-header">
          <div>
            <span>DETECTED EVENTS</span>
            <h2>Recent threats</h2>
          </div>

          <span className="organization-panel-meta">Today</span>
        </div>

        <div className="threat-list">
          {threats.map((threat) => {
            const vote = votes[threat.id];

            return (
              <button
                type="button"
                className="threat-row threat-row-button"
                key={threat.id}
                onClick={() => setSelectedThreat(threat)}
                aria-label={`Review ${threat.type}, ${threat.id}`}
              >
                <span className="threat-id">{threat.id}</span>

                <span className="threat-main">
                  <strong>{threat.type}</strong>
                  <span>{threat.source}</span>
                </span>

                <span
                  className={`threat-severity threat-${threat.severity.toLowerCase()}`}
                >
                  {threat.severity}
                </span>

                <span className="threat-time">{threat.time}</span>

                {vote ? (
                  <span className="threat-vote-state">
                    {vote}
                  </span>
                ) : (
                  <span className="threat-review-action">
                    Review →
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </section>

      {selectedThreat && (
        <div
          className="threat-modal-backdrop"
          role="presentation"
          onClick={closeThreatPanel}
        >
          <section
            className="threat-detail-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="threat-detail-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="threat-detail-header">
              <div>
                <span className="organization-section-eyebrow">
                  THREAT REVIEW
                </span>

                <h2 id="threat-detail-title">
                  {selectedThreat.type}
                </h2>

                <p>{selectedThreat.id}</p>
              </div>

              <button
                type="button"
                className="threat-modal-close"
                onClick={closeThreatPanel}
                aria-label="Close threat review"
              >
                ×
              </button>
            </div>

            <div className="threat-detail-status-row">
              <span
                className={`threat-severity threat-${selectedThreat.severity.toLowerCase()}`}
              >
                {selectedThreat.severity}
              </span>

              <span className="threat-detail-source">
                {selectedThreat.source}
              </span>

              <span className="threat-detail-time">
                {selectedThreat.time}
              </span>
            </div>

            <div className="threat-detail-summary">
              <div>
                <span>THREAT ID</span>
                <strong>{selectedThreat.id}</strong>
              </div>

              <div>
                <span>DETECTION SOURCE</span>
                <strong>{selectedThreat.source}</strong>
              </div>

              <div>
                <span>DETECTED</span>
                <strong>{selectedThreat.time}</strong>
              </div>
            </div>

            <div className="threat-voting-section">
              <div>
                <span className="organization-section-eyebrow">
                  SECURITY ASSESSMENT
                </span>

                <h3>How should this event be classified?</h3>

                <p>
                  Record your organization's assessment of this detected
                  event.
                </p>
              </div>

              <div className="threat-vote-options">
                {voteOptions.map((option) => {
                  const isSelected = selectedVote === option;

                  return (
                    <button
                      type="button"
                      key={option}
                      className={`threat-vote-button ${
                        isSelected ? "selected" : ""
                      }`}
                      onClick={() => handleVote(option)}
                    >
                      <span
                        className="threat-vote-indicator"
                        aria-hidden="true"
                      >
                        {isSelected ? "✓" : ""}
                      </span>

                      <span>
                        <strong>{option}</strong>
                        <small>
                          {option === "Confirmed Threat"
                            ? "Treat this event as a genuine security threat."
                            : option === "False Positive"
                              ? "Mark this detection as non-malicious."
                              : "Keep this event open for further investigation."}
                        </small>
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {selectedVote && (
              <div className="threat-vote-confirmation">
                <span aria-hidden="true">✓</span>

                <div>
                  <strong>Assessment recorded</strong>
                  <span>
                    {selectedVote} selected for {selectedThreat.id}.
                  </span>
                </div>
              </div>
            )}

            <div className="threat-detail-footer">
              <span>
                Frontend assessment state · Backend persistence pending
              </span>

              <button
                type="button"
                className="button button-primary"
                onClick={closeThreatPanel}
              >
                Done
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}