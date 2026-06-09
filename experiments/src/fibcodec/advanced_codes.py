"""Complete experimental encodings for Fibonacci-derived integer sequences."""

from __future__ import annotations

import heapq
from collections import Counter

from .bitpack import pack, unpack
from .transform import lift_gaps, reconstruct
from .varint import decode_uvarint, encode_uvarint


class _BitWriter:
    def __init__(self) -> None:
        self._value = 0
        self._bits = 0
        self._output = bytearray()

    def write(self, value: int, width: int) -> None:
        if width < 0 or value < 0 or value >= (1 << width):
            raise ValueError("invalid fixed-width value")
        self._value = (self._value << width) | value
        self._bits += width
        while self._bits >= 8:
            self._bits -= 8
            self._output.append((self._value >> self._bits) & 0xFF)
            self._value &= (1 << self._bits) - 1 if self._bits else 0

    def finish(self) -> bytes:
        if self._bits:
            self._output.append((self._value << (8 - self._bits)) & 0xFF)
            self._value = 0
            self._bits = 0
        return bytes(self._output)


class _BitReader:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._position = 0

    def read(self, width: int) -> int:
        if width < 0 or self._position + width > len(self._data) * 8:
            raise ValueError("truncated bit stream")
        value = 0
        for _ in range(width):
            byte = self._data[self._position // 8]
            shift = 7 - self._position % 8
            value = (value << 1) | ((byte >> shift) & 1)
            self._position += 1
        return value


def _huffman_lengths(values: list[int]) -> dict[int, int]:
    counts = Counter(values)
    if not counts:
        return {}
    if len(counts) == 1:
        return {next(iter(counts)): 1}
    order = 0
    heap: list[tuple[int, int, tuple]] = []
    for symbol, count in sorted(counts.items()):
        heapq.heappush(heap, (count, order, ("leaf", symbol)))
        order += 1
    while len(heap) > 1:
        left_count, _, left = heapq.heappop(heap)
        right_count, _, right = heapq.heappop(heap)
        heapq.heappush(
            heap, (left_count + right_count, order, ("node", left, right))
        )
        order += 1
    lengths: dict[int, int] = {}

    def visit(node: tuple, depth: int) -> None:
        if node[0] == "leaf":
            lengths[node[1]] = max(1, depth)
            return
        visit(node[1], depth + 1)
        visit(node[2], depth + 1)

    visit(heap[0][2], 0)
    return lengths


def _canonical_codes(lengths: dict[int, int]) -> dict[int, tuple[int, int]]:
    ordered = sorted((length, symbol) for symbol, length in lengths.items())
    codes: dict[int, tuple[int, int]] = {}
    code = 0
    previous = 0
    for length, symbol in ordered:
        code <<= length - previous
        codes[symbol] = (code, length)
        code += 1
        previous = length
    return codes


def encode_huffman(values: list[int]) -> bytes:
    lengths = _huffman_lengths(values)
    codes = _canonical_codes(lengths)
    writer = _BitWriter()
    for value in values:
        code, width = codes[value]
        writer.write(code, width)
    packed = writer.finish()
    output = bytearray()
    output += encode_uvarint(len(values))
    output += encode_uvarint(len(lengths))
    for symbol in sorted(lengths):
        output += encode_uvarint(symbol)
        output += encode_uvarint(lengths[symbol])
    output += encode_uvarint(len(packed))
    output += packed
    return bytes(output)


def decode_huffman(data: bytes) -> list[int]:
    count, offset = decode_uvarint(data)
    alphabet_size, offset = decode_uvarint(data, offset)
    lengths: dict[int, int] = {}
    for _ in range(alphabet_size):
        symbol, offset = decode_uvarint(data, offset)
        length, offset = decode_uvarint(data, offset)
        if length <= 0:
            raise ValueError("invalid Huffman code length")
        lengths[symbol] = length
    packed_length, offset = decode_uvarint(data, offset)
    packed = data[offset : offset + packed_length]
    if len(packed) != packed_length or offset + packed_length != len(data):
        raise ValueError("invalid Huffman payload length")
    if count == 0:
        return []
    inverse = {
        (code, width): symbol
        for symbol, (code, width) in _canonical_codes(lengths).items()
    }
    maximum = max(lengths.values())
    reader = _BitReader(packed)
    output = []
    for _ in range(count):
        code = 0
        for width in range(1, maximum + 1):
            code = (code << 1) | reader.read(1)
            symbol = inverse.get((code, width))
            if symbol is not None:
                output.append(symbol)
                break
        else:
            raise ValueError("invalid Huffman code")
    return output


def encode_rice(values: list[int], parameter: int) -> bytes:
    if parameter < 0 or parameter > 63:
        raise ValueError("Rice parameter out of range")
    writer = _BitWriter()
    for value in values:
        if value <= 0:
            raise ValueError("Rice coding requires positive integers")
        mapped = value - 1
        quotient = mapped >> parameter
        for _ in range(quotient):
            writer.write(1, 1)
        writer.write(0, 1)
        if parameter:
            writer.write(mapped & ((1 << parameter) - 1), parameter)
    packed = writer.finish()
    return (
        encode_uvarint(len(values))
        + bytes([parameter])
        + encode_uvarint(len(packed))
        + packed
    )


def decode_rice(data: bytes) -> list[int]:
    count, offset = decode_uvarint(data)
    if offset >= len(data):
        raise ValueError("truncated Rice payload")
    parameter = data[offset]
    packed_length, offset = decode_uvarint(data, offset + 1)
    packed = data[offset : offset + packed_length]
    if len(packed) != packed_length or offset + packed_length != len(data):
        raise ValueError("invalid Rice payload length")
    reader = _BitReader(packed)
    output = []
    for _ in range(count):
        quotient = 0
        while reader.read(1):
            quotient += 1
        remainder = reader.read(parameter) if parameter else 0
        output.append((quotient << parameter) + remainder + 1)
    return output


def best_rice(values: list[int], maximum_parameter: int = 16) -> tuple[int, bytes]:
    def payload_bits(parameter: int) -> int:
        return sum(((value - 1) >> parameter) + 1 + parameter for value in values)

    parameter = min(range(maximum_parameter + 1), key=payload_bits)
    return parameter, encode_rice(values, parameter)


def encode_elias_fano(values: list[int]) -> bytes:
    if any(a >= b for a, b in zip(values, values[1:])):
        raise ValueError("Elias-Fano requires strictly increasing values")
    if any(value < 0 for value in values):
        raise ValueError("Elias-Fano requires non-negative values")
    count = len(values)
    universe = values[-1] + 1 if values else 0
    lower_width = (
        max(0, (universe // count).bit_length() - 1) if count and universe else 0
    )
    low_mask = (1 << lower_width) - 1
    lows = pack([value & low_mask for value in values], lower_width)
    high_length = (universe >> lower_width) + count if count else 0
    high = bytearray((high_length + 7) // 8)
    for index, value in enumerate(values):
        position = (value >> lower_width) + index
        high[position // 8] |= 1 << (7 - position % 8)
    return (
        encode_uvarint(count)
        + encode_uvarint(universe)
        + bytes([lower_width])
        + encode_uvarint(len(lows))
        + lows
        + encode_uvarint(len(high))
        + high
    )


def decode_elias_fano(data: bytes) -> list[int]:
    count, offset = decode_uvarint(data)
    universe, offset = decode_uvarint(data, offset)
    if offset >= len(data):
        raise ValueError("truncated Elias-Fano payload")
    lower_width = data[offset]
    low_length, offset = decode_uvarint(data, offset + 1)
    lows_data = data[offset : offset + low_length]
    offset += low_length
    high_length, offset = decode_uvarint(data, offset)
    high = data[offset : offset + high_length]
    if len(high) != high_length or offset + high_length != len(data):
        raise ValueError("invalid Elias-Fano payload length")
    lows = unpack(lows_data, count, lower_width)
    output = []
    seen = 0
    for position in range(len(high) * 8):
        if high[position // 8] & (1 << (7 - position % 8)):
            high_value = position - seen
            output.append((high_value << lower_width) | lows[seen])
            seen += 1
            if seen == count:
                break
    if len(output) != count or (output and output[-1] >= universe):
        raise ValueError("invalid Elias-Fano high-bit vector")
    return output


def gaps_to_bytes(gaps: list[int], original_length: int) -> bytes:
    value = reconstruct(lift_gaps(gaps))
    if value.bit_length() > original_length * 8:
        raise ValueError("decoded value exceeds block length")
    return value.to_bytes(original_length, "big")
