"""Independent per-block Fibonacci index-gap baseline.

The codec is experimental. Each block independently selects raw storage or the
Fibonacci transform, so the complete container never expands by more than its
format overhead solely because the transform is unfavorable.
"""

from __future__ import annotations

from collections import Counter

from .bitpack import pack, unpack
from .transform import lift_gaps, reconstruct, reduce_indices, zeckendorf_indices
from .varint import decode_uvarint, encode_uvarint

MAGIC = b"FIPB"
VERSION = 1
MODE_RAW = 0
MODE_FIB = 1


def _alphabetize(gaps: list[int]) -> tuple[list[int], list[int]]:
    counts = Counter(gaps)
    first = {value: i for i, value in enumerate(gaps)}
    alphabet = sorted(counts, key=lambda value: (-counts[value], first[value]))
    lookup = {value: i for i, value in enumerate(alphabet)}
    return alphabet, [lookup[value] for value in gaps]


def _encode_fib_payload(block: bytes) -> bytes:
    value = int.from_bytes(block, "big")
    gaps = reduce_indices(zeckendorf_indices(value))
    alphabet, symbols = _alphabetize(gaps)
    width = (len(alphabet) - 1).bit_length() if alphabet else 0
    packed = pack(symbols, width)

    output = bytearray()
    output += encode_uvarint(len(alphabet))
    output += encode_uvarint(len(symbols))
    output.append(width)
    for item in alphabet:
        output += encode_uvarint(item)
    output += encode_uvarint(len(packed))
    output += packed
    return bytes(output)


def _decode_fib_payload(payload: bytes, original_length: int) -> bytes:
    offset = 0
    alphabet_size, offset = decode_uvarint(payload, offset)
    symbol_count, offset = decode_uvarint(payload, offset)
    if offset >= len(payload):
        raise ValueError("truncated Fibonacci payload")
    width = payload[offset]
    offset += 1
    alphabet = []
    for _ in range(alphabet_size):
        value, offset = decode_uvarint(payload, offset)
        alphabet.append(value)
    packed_length, offset = decode_uvarint(payload, offset)
    packed = payload[offset : offset + packed_length]
    offset += packed_length
    if offset != len(payload):
        raise ValueError("trailing bytes in Fibonacci payload")
    symbols = unpack(packed, symbol_count, width)
    if any(symbol >= len(alphabet) for symbol in symbols):
        raise ValueError("alphabet index out of range")
    gaps = [alphabet[symbol] for symbol in symbols]
    value = reconstruct(lift_gaps(gaps))
    if value.bit_length() > original_length * 8:
        raise ValueError("decoded integer exceeds original block length")
    return value.to_bytes(original_length, "big")


def encode(data: bytes, block_size: int = 256, allow_raw: bool = True) -> bytes:
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    output = bytearray(MAGIC)
    output.append(VERSION)
    output += encode_uvarint(block_size)
    output += encode_uvarint(len(data))
    blocks = [data[i : i + block_size] for i in range(0, len(data), block_size)]
    output += encode_uvarint(len(blocks))
    for block in blocks:
        fib_payload = _encode_fib_payload(block)
        if allow_raw and len(block) <= len(fib_payload):
            mode, payload = MODE_RAW, block
        else:
            mode, payload = MODE_FIB, fib_payload
        output.append(mode)
        output += encode_uvarint(len(block))
        output += encode_uvarint(len(payload))
        output += payload
    return bytes(output)


def decode(container: bytes) -> bytes:
    if not container.startswith(MAGIC):
        raise ValueError("invalid magic")
    offset = len(MAGIC)
    if offset >= len(container) or container[offset] != VERSION:
        raise ValueError("unsupported version")
    offset += 1
    _, offset = decode_uvarint(container, offset)
    original_length, offset = decode_uvarint(container, offset)
    block_count, offset = decode_uvarint(container, offset)
    output = bytearray()
    for _ in range(block_count):
        if offset >= len(container):
            raise ValueError("truncated block header")
        mode = container[offset]
        offset += 1
        block_length, offset = decode_uvarint(container, offset)
        payload_length, offset = decode_uvarint(container, offset)
        payload = container[offset : offset + payload_length]
        offset += payload_length
        if len(payload) != payload_length:
            raise ValueError("truncated block payload")
        if mode == MODE_RAW:
            if payload_length != block_length:
                raise ValueError("raw block length mismatch")
            block = payload
        elif mode == MODE_FIB:
            block = _decode_fib_payload(payload, block_length)
        else:
            raise ValueError(f"unknown block mode {mode}")
        output += block
    if offset != len(container):
        raise ValueError("trailing bytes after final block")
    if len(output) != original_length:
        raise ValueError("decoded stream length mismatch")
    return bytes(output)
