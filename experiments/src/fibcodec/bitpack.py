"""Fixed-width integer packing with explicit symbol counts."""

from __future__ import annotations


def pack(values: list[int], width: int) -> bytes:
    if width < 0:
        raise ValueError("width must be non-negative")
    if not values or width == 0:
        return b""
    limit = 1 << width
    accumulator = 0
    bits = 0
    output = bytearray()
    for value in values:
        if value < 0 or value >= limit:
            raise ValueError(f"value {value} does not fit in {width} bits")
        accumulator = (accumulator << width) | value
        bits += width
        while bits >= 8:
            bits -= 8
            output.append((accumulator >> bits) & 0xFF)
            accumulator &= (1 << bits) - 1 if bits else 0
    if bits:
        output.append((accumulator << (8 - bits)) & 0xFF)
    return bytes(output)


def unpack(data: bytes, count: int, width: int) -> list[int]:
    if count < 0 or width < 0:
        raise ValueError("count and width must be non-negative")
    if count == 0:
        return []
    if width == 0:
        return [0] * count
    required = (count * width + 7) // 8
    if len(data) != required:
        raise ValueError("packed payload length does not match count and width")
    accumulator = 0
    bits = 0
    output: list[int] = []
    for byte in data:
        accumulator = (accumulator << 8) | byte
        bits += 8
        while bits >= width and len(output) < count:
            bits -= width
            output.append((accumulator >> bits) & ((1 << width) - 1))
            accumulator &= (1 << bits) - 1 if bits else 0
    if len(output) != count:
        raise ValueError("truncated packed payload")
    return output

