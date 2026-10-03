from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4

from .contracts import (
    AssistantConversation,
    AssistantMessage,
)


class AssistantConversationService:
    """
    Minimal conversation service.

    Stores only threat context and assistant/user messages.
    Secrets are not intentionally persisted by this service.
    """

    def __init__(self):
        self._conversations: dict[str, AssistantConversation] = {}
        self._messages: dict[str, list[AssistantMessage]] = {}

    def create(
        self,
        *,
        threat_context: str,
    ) -> AssistantConversation:

        conversation = AssistantConversation(
            id=str(uuid4()),
            created_at=datetime.now(UTC),
            threat_context=str(threat_context),
        )

        self._conversations[conversation.id] = conversation
        self._messages[conversation.id] = []

        return conversation

    def add_message(
        self,
        *,
        conversation_id: str,
        role: str,
        content: str,
    ) -> AssistantMessage:

        if conversation_id not in self._conversations:
            raise KeyError(
                f"Conversation {conversation_id} not found"
            )

        message = AssistantMessage(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=str(content),
            created_at=datetime.now(UTC),
        )

        self._messages[conversation_id].append(message)

        return message

    def get(
        self,
        conversation_id: str,
    ) -> AssistantConversation | None:

        return self._conversations.get(conversation_id)

    def messages(
        self,
        conversation_id: str,
    ) -> list[AssistantMessage]:

        return list(
            self._messages.get(conversation_id, [])
        )


assistant_conversation_service = AssistantConversationService()
