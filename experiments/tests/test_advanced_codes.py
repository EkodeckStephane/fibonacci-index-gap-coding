import os

import pytest

from fibcodec.advanced_codes import (
    best_rice,
    decode_elias_fano,
    decode_huffman,
    decode_rice,
    encode_elias_fano,
    encode_huffman,
    encode_rice,
)
from fibcodec.shared_codec import decode as shared_decode
from fibcodec.shared_codec import encode as shared_encode


@pytest.mark.parametrize(
    "values",
    [[], [1], [2, 2, 2], [1, 2, 1, 3, 1, 2], list(range(1, 80))],
)
def test_huffman_roundtrip(values):
    assert decode_huffman(encode_huffman(values)) == values


@pytest.mark.parametrize("parameter", range(0, 8))
def test_rice_roundtrip(parameter):
    values = [1, 2, 3, 5, 8, 13, 21, 34]
    assert decode_rice(encode_rice(values, parameter)) == values


def test_best_rice_is_decodable():
    values = [2, 2, 3, 2, 4, 2, 10]
    _, payload = best_rice(values)
    assert decode_rice(payload) == values


@pytest.mark.parametrize(
    "values",
    [[], [0], [1, 3, 8, 20], list(range(0, 1000, 7))],
)
def test_elias_fano_roundtrip(values):
    assert decode_elias_fano(encode_elias_fano(values)) == values


@pytest.mark.parametrize(
    "payload",
    [b"", b"\x00" * 4096, b"abc" * 1000, bytes(range(256)), os.urandom(4096)],
)
@pytest.mark.parametrize("block_size", [16, 64, 256])
def test_shared_alphabet_roundtrip(payload, block_size):
    assert shared_decode(shared_encode(payload, block_size)) == payload
