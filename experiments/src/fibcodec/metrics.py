"""Compression and information-theoretic measurements."""

from __future__ import annotations

import math
from collections import Counter


def shannon_entropy(data: bytes) -> float:
    """Zero-order empirical entropy in bits per byte."""
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((count / n) * math.log2(count / n) for count in counts.values())


def compression_metrics(original_size: int, compressed_size: int) -> dict[str, float]:
    if original_size == 0:
        return {
            "ratio": 1.0 if compressed_size == 0 else math.inf,
            "saving_fraction": 0.0,
            "bits_per_byte": 0.0 if compressed_size == 0 else math.inf,
        }
    return {
        "ratio": compressed_size / original_size,
        "saving_fraction": 1.0 - compressed_size / original_size,
        "bits_per_byte": 8.0 * compressed_size / original_size,
    }

