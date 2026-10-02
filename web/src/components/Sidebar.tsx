const navigationItems = [
  "Dashboard",
  "Threat Center",
  "Incidents",
  "Cyber Score",
];

export default function Sidebar() {
  return (
    <aside>
      <h2>CyberGuard</h2>

      <nav>
        <ul>
          {navigationItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}