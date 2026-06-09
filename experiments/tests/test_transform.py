import pytest

from fibcodec.transform import (
    fibonacci,
    lift_gaps,
    reconstruct,
    reduce_indices,
    zeckendorf_indices,
)


def test_fibonacci_known_values():
    assert [fibonacci(i) for i in range(11)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]


@pytest.mark.parametrize("value", range(1, 10_000))
def test_zeckendorf_roundtrip(value):
    indices = zeckendorf_indices(value)
    assert reconstruct(indices) == value
    assert all(a - b >= 2 for a, b in zip(indices, indices[1:]))
    assert lift_gaps(reduce_indices(indices)) == indices


def test_negative_value_rejected():
    with pytest.raises(ValueError):
        zeckendorf_indices(-1)

