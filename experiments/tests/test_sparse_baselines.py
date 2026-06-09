import pytest

from fibcodec.sparse_baselines import (
    decode_zero_block_bitmap,
    decode_zero_trim,
    encode_zero_block_bitmap,
    encode_zero_trim,
)


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"\x00",
        b"\x00" * 4096,
        bytes(range(256)) * 4,
        b"\x00" * 200 + b"payload" + b"\x00" * 500,
    ],
)
@pytest.mark.parametrize("block_size", [16, 64, 256])
def test_sparse_baseline_roundtrips(data: bytes, block_size: int) -> None:
    bitmap = encode_zero_block_bitmap(data, block_size)
    trimmed = encode_zero_trim(data, block_size)
    assert decode_zero_block_bitmap(bitmap) == data
    assert decode_zero_trim(trimmed) == data
