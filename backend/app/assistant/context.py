from typing import Protocol
from uuid import UUID

from .contracts import AssistantContext


class ContextBuilder(Protocol):
    def build(
        self,
        *,
        user_id: UUID,
        context_id: UUID,
        question: str,
        detection: object,
        explanation: object,
    ) -> AssistantContext:
        """Build a tenant-scoped context using only necessary information."""
        ...