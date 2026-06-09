"""Complete lossless baselines for block-level zero structure."""

from __future__ import annotations

from .bitpack import pack, unpack
from .varint import decode_uvarint, encode_uvarint


def encode_zero_block_bitmap(data: bytes, block_size: int = 256) -> bytes:
    blocks = [data[start : start + block_size] for start in range(0, len(data), block_size)]
    present = [int(any(block)) for block in blocks]
    bitmap = pack(present, 1)
    output = bytearray(b"ZBB1")
    output += encode_uvarint(block_size)
    output += encode_uvarint(len(data))
    output += encode_uvarint(len(blocks))
    output += encode_uvarint(len(bitmap))
    output += bitmap
    for flag, block in zip(present, blocks):
        if flag:
            output += block
    return bytes(output)


def decode_zero_block_bitmap(container: bytes) -> bytes:
    if not container.startswith(b"ZBB1"):
        raise ValueError("invalid zero-block bitmap magic")
    offset = 4
    block_size, offset = decode_uvarint(container, offset)
    original_length, offset = decode_uvarint(container, offset)
    block_count, offset = decode_uvarint(container, offset)
    bitmap_length, offset = decode_uvarint(container, offset)
    bitmap = container[offset : offset + bitmap_length]
    offset += bitmap_length
    present = unpack(bitmap, block_count, 1)
    output = bytearray()
    for index, flag in enumerate(present):
        length = min(block_size, original_length - index * block_size)
        if flag:
            block = container[offset : offset + length]
            if len(block) != length:
                raise ValueError("truncated nonzero block")
            output += block
            offset += length
        else:
            output += bytes(length)
    if offset != len(container) or len(output) != original_length:
        raise ValueError("invalid zero-block bitmap stream")
    return bytes(output)


def encode_zero_trim(data: bytes, block_size: int = 256) -> bytes:
    blocks = [data[start : start + block_size] for start in range(0, len(data), block_size)]
    output = bytearray(b"ZTR1")
    output += encode_uvarint(block_size)
    output += encode_uvarint(len(data))
    output += encode_uvarint(len(blocks))
    for block in blocks:
        left = 0
        while left < len(block) and block[left] == 0:
            left += 1
        right = len(block)
        while right > left and block[right - 1] == 0:
            right -= 1
        payload = block[left:right]
        output += encode_uvarint(left)
        output += encode_uvarint(len(payload))
        output += payload
    return bytes(output)


def decode_zero_trim(container: bytes) -> bytes:
    if not container.startswith(b"ZTR1"):
        raise ValueError("invalid zero-trim magic")
    offset = 4
    block_size, offset = decode_uvarint(container, offset)
    original_length, offset = decode_uvarint(container, offset)
    block_count, offset = decode_uvarint(container, offset)
    output = bytearray()
    for index in range(block_count):
        block_length = min(block_size, original_length - index * block_size)
        left, offset = decode_uvarint(container, offset)
        payload_length, offset = decode_uvarint(container, offset)
        if left + payload_length > block_length:
            raise ValueError("invalid trimmed block")
        payload = container[offset : offset + payload_length]
        if len(payload) != payload_length:
            raise ValueError("truncated trimmed payload")
        offset += payload_length
        output += bytes(left) + payload + bytes(block_length - left - payload_length)
    if offset != len(container) or len(output) != original_length:
        raise ValueError("invalid zero-trim stream")
    return bytes(output)
