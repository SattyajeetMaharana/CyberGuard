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
        <span className="home-eyebrow">THE CYBERGUARD WORKFLOW</span>

        <h1>
          From a security signal
          <span> to an actionable result.</span>
        </h1>

        <p>
          CyberGuard connects detection, analysis, explanation, and security
          monitoring into a single organizational workflow.
        </p>
      </section>

      <section className="workflow-flow-section">
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
          <span className="home-eyebrow">HOW IT WORKS</span>

          <h2>A clear workflow for organizational security.</h2>
        </div>

        <div className="workflow-steps">
          {steps.map((step) => (
            <article className="workflow-step" key={step.number}>
              <span className="workflow-step-number">{step.number}</span>

              <div>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="workflow-cta">
        <div>
          <span className="home-eyebrow">READY TO BEGIN?</span>

          <h2>Put your organization's security in one place.</h2>
        </div>

        <p>
          Start with CyberGuard and build a centralized view of your
          organization's cybersecurity environment.
        </p>
      </section>
    </div>
  );
}