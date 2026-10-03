from __future__ import annotations

import re
from datetime import UTC, datetime
from uuid import uuid4

from .contracts import AssistantConversation, AssistantMessage


_SECRET_PATTERNS = (
    re.compile(r"(?i)\b(password|passwd)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b(api[_-]?key)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b(access[_-]?token)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b(refresh[_-]?token)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b(secret)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bauthorization\s*:\s*\S+"),
)


def _sanitize_text(value: str) -> str:
    sanitized = value

    for pattern in _SECRET_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)

    return sanitized


class AssistantConversationService:
    def __init__(self) -> None:
        self._conversations: dict[str, AssistantConversation] = {}
        self._messages: dict[str, list[AssistantMessage]] = {}

    def create(
        self,
        threat_context: str,
    ) -> AssistantConversation:
        conversation = AssistantConversation(
            id=str(uuid4()),
            created_at=datetime.now(UTC),
            threat_context=_sanitize_text(threat_context),
        )

        self._conversations[conversation.id] = conversation
        self._messages[conversation.id] = []

        return conversation

    def create_conversation(
        self,
        threat_context: str,
    ) -> AssistantConversation:
        return self.create(threat_context)

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> AssistantMessage:
        if conversation_id not in self._conversations:
            raise ValueError("Conversation not found")

        if role not in {"user", "assistant", "system"}:
            raise ValueError("Invalid conversation role")

        message = AssistantMessage(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=_sanitize_text(content),
            created_at=datetime.now(UTC),
        )

        self._messages[conversation_id].append(message)

        return message

    def get_conversation(
        self,
        conversation_id: str,
    ) -> AssistantConversation:
        try:
            return self._conversations[conversation_id]
        except KeyError as exc:
            raise ValueError("Conversation not found") from exc

    def get_messages(
        self,
        conversation_id: str,
    ) -> tuple[AssistantMessage, ...]:
        if conversation_id not in self._messages:
            raise ValueError("Conversation not found")

        return tuple(self._messages[conversation_id])

    def messages(
        self,
        conversation_id: str,
    ) -> tuple[AssistantMessage, ...]:
        return self.get_messages(conversation_id)


assistant_conversation_service = AssistantConversationService()
