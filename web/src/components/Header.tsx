interface HeaderProps {
  title?: string;
}

export default function Header({ title = "CyberGuard" }: HeaderProps) {
  return (
    <header>
      <h1>{title}</h1>
    </header>
  );
}