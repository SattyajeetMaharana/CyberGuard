const steps = [
  {
    number: "01",
    title: "Connect your organization",
    description:
      "Create your organization workspace and bring your departments, employees, and managed devices into one security environment.",
  },
  {
    number: "02",
    title: "Analyze potential threats",
    description:
      "CyberGuard processes security-related inputs through its detection modules to identify potentially harmful activity.",
  },
  {
    number: "03",
    title: "Understand the result",
    description:
      "Detection results are presented with security context and explanations to make the analysis easier to understand.",
  },
  {
    number: "04",
    title: "Monitor your security posture",
    description:
      "Use the organization dashboard, threat center, incidents, and Cyber Score to maintain visibility over your security environment.",
  },
];

const flowItems = [
  "Input",
  "Detection",
  "Analysis",
  "Explanation",
  "Response",
];

export default function HowItWorks() {
  return (
    <div className="how-it-works-page">
      <section className="workflow-hero">
        <div className="workflow-hero-content">
          <span className="home-eyebrow">THE CYBERGUARD WORKFLOW</span>

          <h1>
            From a security signal
            <span> to an actionable result.</span>
          </h1>

          <p>
            CyberGuard connects detection, analysis, explanation, and security
            monitoring into a single organizational workflow.
          </p>
        </div>

        <div className="workflow-hero-indicator" aria-hidden="true">
          <span className="workflow-pulse" />
          <span>SECURITY FLOW</span>
          <strong>01—05</strong>
        </div>
      </section>

      <section className="workflow-flow-section">
        <div className="workflow-flow-header">
          <span className="home-eyebrow">SECURITY PIPELINE</span>
          <span className="workflow-flow-label">CONTINUOUS ANALYSIS</span>
        </div>

        <div className="workflow-flow">
          {flowItems.map((item, index) => (
            <div className="workflow-flow-item" key={item}>
              <div className="workflow-flow-node">
                <span>{String(index + 1).padStart(2, "0")}</span>
              </div>

              <strong>{item}</strong>

              {index < flowItems.length - 1 && (
                <span className="workflow-flow-arrow" aria-hidden="true">
                  →
                </span>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="workflow-steps-section">
        <div className="workflow-section-heading">
          <div>
            <span className="home-eyebrow">HOW IT WORKS</span>

            <h2>A clear workflow for organizational security.</h2>
          </div>

          <span className="workflow-heading-index">/ 04</span>
        </div>

        <div className="workflow-steps">
          {steps.map((step) => (
            <article className="workflow-step" key={step.number}>
              <div className="workflow-step-top">
                <span className="workflow-step-number">
                  {step.number}
                </span>

                <span className="workflow-step-arrow" aria-hidden="true">
                  ↗
                </span>
              </div>

              <div className="workflow-step-content">
                <h3>{step.title}</h3>

                <p>{step.description}</p>
              </div>

              <div className="workflow-step-line" aria-hidden="true" />
            </article>
          ))}
        </div>
      </section>

      <section className="workflow-cta">
        <div className="workflow-cta-content">
          <span className="home-eyebrow">READY TO BEGIN?</span>

          <h2>
            Put your organization's
            <span> security in one place.</span>
          </h2>

          <p>
            Start with CyberGuard and build a centralized view of your
            organization's cybersecurity environment.
          </p>
        </div>

        <div className="workflow-cta-orbit" aria-hidden="true">
          <span />
          <span />
          <strong>CG</strong>
        </div>
      </section>
    </div>
  );
}