from app.response.contracts import ResponseAction
from app.response.service import recommend_response


def test_response_recommendation():
    result = recommend_response(
        ResponseAction.NOTIFY_ADMIN,
        "High-risk detection"
    )

    assert result.action == ResponseAction.NOTIFY_ADMIN
    assert result.requires_approval is True