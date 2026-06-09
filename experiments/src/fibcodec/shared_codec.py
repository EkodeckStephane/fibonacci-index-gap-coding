"""FISA 1.0 stream with one gap alphabet shared by all blocks."""

from __future__ import annotations

from collections import Counter

from .bitpack import pack, unpack
from .transform import lift_gaps, reconstruct, reduce_indices, zeckendorf_indices
from .varint import decode_uvarint, encode_uvarint

MAGIC = b"FISA"
VERSION = 1
MODE_RAW = 0
MODE_SHARED = 1


def _encode_shared_body(data: bytes, block_size: int) -> bytes:
    blocks = [data[i : i + block_size] for i in range(0, len(data), block_size)]
    gap_blocks = [
        reduce_indices(zeckendorf_indices(int.from_bytes(block, "big")))
        for block in blocks
    ]
    counts = Counter(value for gaps in gap_blocks for value in gaps)
    first: dict[int, int] = {}
    for gaps in gap_blocks:
        for value in gaps:
            first.setdefault(value, len(first))
    alphabet = sorted(counts, key=lambda value: (-counts[value], first[value]))
    lookup = {value: index for index, value in enumerate(alphabet)}
    width = (len(alphabet) - 1).bit_length() if alphabet else 0

    output = bytearray()
    output += encode_uvarint(block_size)
    output += encode_uvarint(len(blocks))
    output += encode_uvarint(len(alphabet))
    output.append(width)
    for value in alphabet:
        output += encode_uvarint(value)
    for block, gaps in zip(blocks, gap_blocks):
        symbols = [lookup[value] for value in gaps]
        packed = pack(symbols, width)
        shared_payload = encode_uvarint(len(symbols)) + encode_uvarint(len(packed)) + packed
        if len(shared_payload) < len(block):
            mode, payload = MODE_SHARED, shared_payload
        else:
            mode, payload = MODE_RAW, block
        output.append(mode)
        output += encode_uvarint(len(block))
        output += encode_uvarint(len(payload))
        output += payload
    return bytes(output)


def encode(data: bytes, block_size: int = 256) -> bytes:
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    shared = _encode_shared_body(data, block_size)
    raw = bytes([MODE_RAW]) + encode_uvarint(len(data)) + data
    transformed = bytes([MODE_SHARED]) + encode_uvarint(len(data)) + shared
    payload = transformed if len(transformed) < len(raw) else raw
    return MAGIC + bytes([VERSION]) + payload


def decode(container: bytes) -> bytes:
    if not container.startswith(MAGIC):
        raise ValueError("invalid shared-alphabet magic")
    offset = len(MAGIC)
    if offset >= len(container) or container[offset] != VERSION:
        raise ValueError("unsupported shared-alphabet format identifier")
    offset += 1
    if offset >= len(container):
        raise ValueError("truncated stream mode")
    stream_mode = container[offset]
    original_length, offset = decode_uvarint(container, offset + 1)
    if stream_mode == MODE_RAW:
        payload = container[offset:]
        if len(payload) != original_length:
            raise ValueError("raw stream length mismatch")
        return payload
    if stream_mode != MODE_SHARED:
        raise ValueError("unknown stream mode")
    block_size, offset = decode_uvarint(container, offset)
    if block_size <= 0:
        raise ValueError("invalid block size")
    block_count, offset = decode_uvarint(container, offset)
    alphabet_size, offset = decode_uvarint(container, offset)
    if offset >= len(container):
        raise ValueError("truncated shared alphabet")
    width = container[offset]
    offset += 1
    alphabet = []
    for _ in range(alphabet_size):
        value, offset = decode_uvarint(container, offset)
        alphabet.append(value)
    output = bytearray()
    for _ in range(block_count):
        if offset >= len(container):
            raise ValueError("truncated block")
        mode = container[offset]
        block_length, offset = decode_uvarint(container, offset + 1)
        payload_length, offset = decode_uvarint(container, offset)
        payload = container[offset : offset + payload_length]
        offset += payload_length
        if len(payload) != payload_length:
            raise ValueError("truncated block payload")
        if mode == MODE_RAW:
            if len(payload) != block_length:
                raise ValueError("raw block length mismatch")
            output += payload
        elif mode == MODE_SHARED:
            count, payload_offset = decode_uvarint(payload)
            packed_length, payload_offset = decode_uvarint(payload, payload_offset)
            packed = payload[payload_offset : payload_offset + packed_length]
            if payload_offset + packed_length != len(payload):
                raise ValueError("invalid shared payload")
            symbols = unpack(packed, count, width)
            if any(symbol >= len(alphabet) for symbol in symbols):
                raise ValueError("shared alphabet index out of range")
            gaps = [alphabet[symbol] for symbol in symbols]
            value = reconstruct(lift_gaps(gaps))
            if value.bit_length() > block_length * 8:
                raise ValueError("decoded block exceeds declared length")
            output += value.to_bytes(block_length, "big")
        else:
            raise ValueError("unknown shared block mode")
    if offset != len(container) or len(output) != original_length:
        raise ValueError("invalid shared stream length")
    return bytes(output)
