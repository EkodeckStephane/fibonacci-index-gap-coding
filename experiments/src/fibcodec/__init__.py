"""Exact Fibonacci-inspired lossless codec and evaluation helpers."""

from .codec import decode, encode
from .transform import (
    fibonacci,
    lift_gaps,
    reduce_indices,
    zeckendorf_indices,
)

__all__ = [
    "decode",
    "encode",
    "fibonacci",
    "lift_gaps",
    "reduce_indices",
    "zeckendorf_indices",
]

