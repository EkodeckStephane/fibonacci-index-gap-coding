"""Deterministic complete-stream baseline codecs."""

from __future__ import annotations

import bz2
import lzma
import zlib

import brotli
import pyppmd
import zstandard


def raw(data: bytes) -> bytes:
    return data


def rle(data: bytes) -> bytes:
    """Simple byte RLE with explicit count-byte pairs."""
    if not data:
        return b""
    output = bytearray()
    current = data[0]
    count = 1
    for byte in data[1:]:
        if byte == current and count < 255:
            count += 1
        else:
            output.extend((count, current))
            current = byte
            count = 1
    output.extend((count, current))
    return bytes(output)


CODECS = {
    "raw": raw,
    "rle": rle,
    "zlib_9": lambda data: zlib.compress(data, level=9),
    "bzip2_9": lambda data: bz2.compress(data, compresslevel=9),
    "lzma_9": lambda data: lzma.compress(data, preset=9),
    "brotli_11": lambda data: brotli.compress(data, quality=11),
    "zstd_19": lambda data: zstandard.ZstdCompressor(level=19).compress(data),
    "ppmd_6": lambda data: pyppmd.compress(data, max_order=6),
}
