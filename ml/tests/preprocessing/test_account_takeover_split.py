import pandas as pd

from ml.preprocessing.account_takeover.split_dataset import (
    DatasetSplit,
    split_by_user,
    verify_no_user_overlap,
)


def make_sample_data() -> pd.DataFrame:
    rows = []

    # 30 users.
    # Users 1–6 contain ATO events.
    for user_number in range(1, 31):
        user_id = f"user_{user_number}"

        for event_number in range(5):
            rows.append(
                {
                    "Login Timestamp": (
                        f"2026-01-{event_number + 1:02d} "
                        "10:00:00"
                    ),
                    "User ID": user_id,
                    "Is Account Takeover": (
                        user_number <= 6
                        and event_number == 0
                    ),
                }
            )

    return pd.DataFrame(rows)


def test_split_by_user():
    data = make_sample_data()

    split = split_by_user(
        data,
        random_state=42,
    )

    assert isinstance(split, DatasetSplit)

    assert len(split.train) > 0
    assert len(split.validation) > 0
    assert len(split.test) > 0

    # All events must be preserved.
    assert (
        len(split.train)
        + len(split.validation)
        + len(split.test)
        == len(data)
    )


def test_no_user_overlap():
    data = make_sample_data()

    split = split_by_user(
        data,
        random_state=42,
    )

    verify_no_user_overlap(split)

    train_users = set(
        split.train["User ID"]
    )
    validation_users = set(
        split.validation["User ID"]
    )
    test_users = set(
        split.test["User ID"]
    )

    assert not train_users & validation_users
    assert not train_users & test_users
    assert not validation_users & test_users


def test_every_user_is_assigned_once():
    data = make_sample_data()

    split = split_by_user(
        data,
        random_state=42,
    )

    original_users = set(
        data["User ID"]
    )

    split_users = (
        set(split.train["User ID"])
        | set(split.validation["User ID"])
        | set(split.test["User ID"])
    )

    assert split_users == original_users


def test_target_events_are_preserved():
    data = make_sample_data()

    split = split_by_user(
        data,
        random_state=42,
    )

    original_ato = int(
        data["Is Account Takeover"].sum()
    )

    split_ato = (
        int(split.train["Is Account Takeover"].sum())
        + int(split.validation["Is Account Takeover"].sum())
        + int(split.test["Is Account Takeover"].sum())
    )

    assert split_ato == original_ato


if __name__ == "__main__":
    data = make_sample_data()

    split = split_by_user(
        data,
        random_state=42,
    )

    verify_no_user_overlap(split)

    print("ATO SPLIT TEST")
    print("=" * 60)
    print(f"Total events: {len(data)}")
    print(f"Train events: {len(split.train)}")
    print(f"Validation events: {len(split.validation)}")
    print(f"Test events: {len(split.test)}")
    print("User overlap: NONE")
    print("TEST PASSED")