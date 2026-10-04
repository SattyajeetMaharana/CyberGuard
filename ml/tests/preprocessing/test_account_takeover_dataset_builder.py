from ml.preprocessing.account_takeover.build_dataset import (
    _reservoir_sample,
)


def test_reservoir_sample_stays_within_target_size():
    reservoir = []
    seen = [0]

    import random

    rng = random.Random(42)

    for value in range(1000):
        seen[0] += 1

        _reservoir_sample(
            reservoir=reservoir,
            row={"value": value},
            target_size=50,
            seen_count=seen[0],
            rng=rng,
        )

    assert len(reservoir) == 50


def test_reservoir_sample_reaches_larger_target_size():
    reservoir = []
    seen = [0]

    import random

    rng = random.Random(42)

    # Simulate the target growing as positives are discovered.
    for value in range(100):
        seen[0] += 1

        target_size = 10 if value < 50 else 20

        _reservoir_sample(
            reservoir=reservoir,
            row={"value": value},
            target_size=target_size,
            seen_count=seen[0],
            rng=rng,
        )

    assert len(reservoir) == 20


def test_reservoir_sample_is_reproducible():
    import random

    def generate_sample():
        reservoir = []
        seen = [0]
        rng = random.Random(42)

        for value in range(500):
            seen[0] += 1

            _reservoir_sample(
                reservoir=reservoir,
                row={"value": value},
                target_size=25,
                seen_count=seen[0],
                rng=rng,
            )

        return reservoir

    assert generate_sample() == generate_sample()