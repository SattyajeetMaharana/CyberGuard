from .contracts import AssistantResponse


def validate_response(response: AssistantResponse) -> bool:
    return bool(response.message.strip())