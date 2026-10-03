from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PlaybookAction:
    id: str
    action: str
    description: str
    approval_required: bool


@dataclass(frozen=True)
class Playbook:
    name: str
    version: str
    threat_category: str
    actions: tuple[PlaybookAction, ...]


def load_account_takeover_playbook(
    path: Path | None = None,
) -> Playbook:

    if path is None:
        path = (
            Path(__file__).resolve().parent
            / "playbooks"
            / "account_takeover.yaml"
        )

    if not path.exists():
        raise FileNotFoundError(path)

    # The project playbook is intentionally simple and declarative.
    # Parse its known fields without requiring an external YAML package.
    lines = [
        line.rstrip()
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    name = ""
    version = ""
    category = ""
    actions: list[PlaybookAction] = []

    current: dict[str, str] = {}

    def flush_action() -> None:
        if not current:
            return

        actions.append(
            PlaybookAction(
                id=current["id"],
                action=current["action"],
                description=current["description"],
                approval_required=(
                    current["approval_required"].lower() == "true"
                ),
            )
        )

        current.clear()

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("name:"):
            name = stripped.split(":", 1)[1].strip()

        elif stripped.startswith("version:"):
            version = stripped.split(":", 1)[1].strip().strip('"')

        elif stripped.startswith("threat_category:"):
            category = stripped.split(":", 1)[1].strip()

        elif stripped.startswith("- id:"):
            flush_action()
            current["id"] = stripped.split(":", 1)[1].strip()

        elif stripped.startswith("action:"):
            current["action"] = stripped.split(":", 1)[1].strip()

        elif stripped.startswith("description:"):
            current["description"] = (
                stripped.split(":", 1)[1].strip()
            )

        elif stripped.startswith("approval_required:"):
            current["approval_required"] = (
                stripped.split(":", 1)[1].strip()
            )

    flush_action()

    return Playbook(
        name=name,
        version=version,
        threat_category=category,
        actions=tuple(actions),
    )
