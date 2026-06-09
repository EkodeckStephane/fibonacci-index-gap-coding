import os

import pytest

from fibcodec.codec import decode, encode


@pytest.mark.parametrize(
    "payload",
    [
        b"",
        b"\x00",
        b"\x00\x00\x01",
        b"Hi",
        b"Fibonacci-inspired entropy reduction",
        bytes(range(256)),
        b"A" * 4096,
        os.urandom(4096),
    ],
)
@pytest.mark.parametrize("block_size", [1, 7, 16, 64, 256, 1024])
def test_roundtrip(payload, block_size):
    assert decode(encode(payload, block_size=block_size)) == payload


def test_forced_fibonacci_roundtrip_with_leading_zeros():
    payload = b"\x00\x00\x01\x02\x03"
    assert decode(encode(payload, block_size=5, allow_raw=False)) == payload


def test_corrupt_magic_rejected():
    with pytest.raises(ValueError):
        decode(b"NOPE")


def test_independent_per_block_magic_is_fipb():
    assert encode(b"baseline").startswith(b"FIPB\x01")
