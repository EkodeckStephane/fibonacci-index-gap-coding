"""Exact Zeckendorf decomposition and reduced-index transform."""

from __future__ import annotations


def _fib_pair(n: int) -> tuple[int, int]:
    """Return (F(n), F(n+1)) using exact fast doubling."""
    if n < 0:
        raise ValueError("Fibonacci index must be non-negative")
    if n == 0:
        return 0, 1
    a, b = _fib_pair(n >> 1)
    c = a * ((b << 1) - a)
    d = a * a + b * b
    if n & 1:
        return d, c + d
    return c, d


def fibonacci(n: int) -> int:
    return _fib_pair(n)[0]


def largest_fibonacci_index(value: int) -> int:
    """Largest n such that F(n) <= value, using integer-only search."""
    if value < 1:
        raise ValueError("value must be positive")
    low, high = 2, 4
    while fibonacci(high) <= value:
        low = high
        high <<= 1
    while low + 1 < high:
        mid = (low + high) // 2
        if fibonacci(mid) <= value:
            low = mid
        else:
            high = mid
    return low


def zeckendorf_indices(value: int) -> list[int]:
    """Return descending non-consecutive Fibonacci indices for value."""
    if value < 0:
        raise ValueError("value must be non-negative")
    if value == 0:
        return []
    # Build each Fibonacci integer once. This is substantially faster for
    # practical blocks than repeated binary searches with fast doubling.
    fibs = [0, 1, 1]
    while fibs[-1] <= value:
        fibs.append(fibs[-1] + fibs[-2])
    indices: list[int] = []
    remainder = value
    index = len(fibs) - 2
    while remainder:
        while fibs[index] > remainder:
            index -= 1
        indices.append(index)
        remainder -= fibs[index]
        index -= 2
    return indices


def reduce_indices(indices: list[int]) -> list[int]:
    if not indices:
        return []
    if any(a <= b for a, b in zip(indices, indices[1:])):
        raise ValueError("indices must be strictly descending")
    return [
        indices[i] - indices[i + 1] for i in range(len(indices) - 1)
    ] + [indices[-1]]


def lift_gaps(gaps: list[int]) -> list[int]:
    if not gaps:
        return []
    if any(gap < 0 for gap in gaps):
        raise ValueError("gaps must be non-negative")
    indices = [0] * len(gaps)
    indices[-1] = gaps[-1]
    for i in range(len(gaps) - 2, -1, -1):
        indices[i] = gaps[i] + indices[i + 1]
    return indices


def reconstruct(indices: list[int]) -> int:
    return sum(fibonacci(index) for index in indices)
