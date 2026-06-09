"""Exact byte-cost model for the FISA shared-alphabet stream."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from .transform import reduce_indices, zeckendorf_indices
from .varint import encode_uvarint


def uvarint_length(value: int) -> int:
    return len(encode_uvarint(value))


@dataclass(frozen=True)
class SharedCost:
    original_bytes: int
    blocks: int
    alphabet_size: int
    symbol_width: int
    global_metadata_bytes: int
    block_record_bytes: int
    transformed_stream_bytes: int
    raw_stream_bytes: int

    @property
    def selected_stream_bytes(self) -> int:
        return min(self.transformed_stream_bytes, self.raw_stream_bytes)


def exact_shared_cost(data: bytes, block_size: int = 256) -> SharedCost:
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    blocks = [data[start : start + block_size] for start in range(0, len(data), block_size)]
    gap_blocks = [
        reduce_indices(zeckendorf_indices(int.from_bytes(block, "big")))
        for block in blocks
    ]
    alphabet = sorted({gap for gaps in gap_blocks for gap in gaps})
    alphabet_size = len(alphabet)
    width = (alphabet_size - 1).bit_length() if alphabet else 0

    global_metadata = (
        uvarint_length(block_size)
        + uvarint_length(len(blocks))
        + uvarint_length(alphabet_size)
        + 1
        + sum(uvarint_length(value) for value in alphabet)
    )
    block_records = 0
    for block, gaps in zip(blocks, gap_blocks):
        packed_length = ceil(len(gaps) * width / 8)
        transformed_payload = (
            uvarint_length(len(gaps))
            + uvarint_length(packed_length)
            + packed_length
        )
        selected_payload = min(len(block), transformed_payload)
        block_records += (
            1
            + uvarint_length(len(block))
            + uvarint_length(selected_payload)
            + selected_payload
        )

    outer = 6 + uvarint_length(len(data))
    transformed = outer + global_metadata + block_records
    raw = outer + len(data)
    return SharedCost(
        original_bytes=len(data),
        blocks=len(blocks),
        alphabet_size=alphabet_size,
        symbol_width=width,
        global_metadata_bytes=global_metadata,
        block_record_bytes=block_records,
        transformed_stream_bytes=transformed,
        raw_stream_bytes=raw,
    )


def sufficient_term_threshold(
    block_bytes: int,
    symbol_width: int,
    global_metadata_bytes: int,
    blocks: int,
) -> int:
    """Largest term count satisfying the equal-amortization sufficient bound."""
    if block_bytes <= 0 or symbol_width < 0 or global_metadata_bytes < 0 or blocks <= 0:
        raise ValueError("invalid threshold parameters")
    amortized = ceil(global_metadata_bytes / blocks)
    threshold = -1
    for terms in range(0, block_bytes * 8 + 1):
        packed = ceil(terms * symbol_width / 8)
        payload = uvarint_length(terms) + uvarint_length(packed) + packed
        complete = (
            1
            + uvarint_length(block_bytes)
            + uvarint_length(payload)
            + payload
            + amortized
        )
        if complete < block_bytes:
            threshold = terms
        elif threshold >= 0:
            break
    return threshold
