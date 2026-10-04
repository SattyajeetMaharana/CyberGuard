import pandas as pd

from ml.preprocessing.account_takeover.feature_extractor import (
    FEATURE_COLUMNS,
    extract_features,
    fit_feature_statistics,
    fit_transform_features,
    transform_features,
)


def make_sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Login Timestamp": "2026-01-01 08:00:00",
                "User ID": "user_1",
                "Country": "Norway",
                "Region": "Viken",
                "City": "Oslo",
                "ASN": 12345,
                "Browser Name and Version": "Chrome",
                "OS Name and Version": "Windows",
                "Device Type": "desktop",
                "Login Successful": True,
            },
            {
                "Login Timestamp": "2026-01-01 23:30:00",
                "User ID": "user_1",
                "Country": "Norway",
                "Region": "Viken",
                "City": "Oslo",
                "ASN": 12345,
                "Browser Name and Version": "Chrome",
                "OS Name and Version": "Windows",
                "Device Type": "desktop",
                "Login Successful": False,
            },
            {
                "Login Timestamp": "2026-01-02 10:00:00",
                "User ID": "user_2",
                "Country": "India",
                "Region": "Odisha",
                "City": "Bhubaneswar",
                "ASN": 54321,
                "Browser Name and Version": "Firefox",
                "OS Name and Version": "Linux",
                "Device Type": "mobile",
                "Login Successful": True,
            },
        ]
    )


def test_feature_extraction():
    data = make_sample_data()

    features = extract_features(data)

    assert list(features.columns) == FEATURE_COLUMNS
    assert len(features) == 3
    assert features.shape[1] == 18
    assert features.isna().sum().sum() == 0


def test_training_statistics_are_reused_for_unseen_values():
    train = make_sample_data()

    test = pd.DataFrame(
        [
            {
                "Login Timestamp": "2026-01-03 12:00:00",
                "User ID": "new_user",
                "Country": "Japan",
                "Region": "Tokyo",
                "City": "Tokyo",
                "ASN": 99999,
                "Browser Name and Version": "Edge",
                "OS Name and Version": "Linux",
                "Device Type": "tablet",
                "Login Successful": True,
            }
        ]
    )

    statistics = fit_feature_statistics(train)
    test_features = transform_features(test, statistics)

    assert len(test_features) == 1
    assert test_features.shape[1] == 18

    # Completely unseen categorical values must receive
    # the training-statistics fallback of zero.
    assert test_features["country_frequency"].iloc[0] == 0.0
    assert test_features["region_frequency"].iloc[0] == 0.0
    assert test_features["city_frequency"].iloc[0] == 0.0
    assert test_features["asn_frequency"].iloc[0] == 0.0


def test_historical_features_do_not_use_current_event():
    data = make_sample_data()

    features, _ = fit_transform_features(data)

    # First event of every user has no previous history.
    assert features.loc[0, "user_login_count"] == 0
    assert features.loc[0, "user_failure_count"] == 0
    assert features.loc[0, "user_unique_countries"] == 0
    assert features.loc[0, "user_unique_devices"] == 0
    assert features.loc[0, "time_since_previous_login_seconds"] == -1

    # Second event of user_1 sees only the first event.
    assert features.loc[1, "user_login_count"] == 1
    assert features.loc[1, "user_failure_count"] == 0
    assert features.loc[1, "user_unique_countries"] == 1
    assert features.loc[1, "user_unique_devices"] == 1
    assert features.loc[1, "time_since_previous_login_seconds"] > 0


def test_training_and_test_transform_have_same_schema():
    train = make_sample_data()

    statistics = fit_feature_statistics(train)
    transformed = transform_features(train, statistics)

    assert list(transformed.columns) == FEATURE_COLUMNS
    assert transformed.shape[1] == 18
    assert transformed.shape[1] == len(FEATURE_COLUMNS)


if __name__ == "__main__":
    test_feature_extraction()
    test_training_statistics_are_reused_for_unseen_values()
    test_historical_features_do_not_use_current_event()
    test_training_and_test_transform_have_same_schema()

    print("ALL ATO FEATURE TESTS PASSED")