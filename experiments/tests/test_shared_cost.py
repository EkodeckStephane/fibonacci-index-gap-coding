import pytest

from fibcodec.shared_codec import decode, encode
from fibcodec.shared_cost import exact_shared_cost, sufficient_term_threshold


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"\x00",
        b"\x00" * 4096,
        bytes(range(256)) * 4,
        b"Fibonacci gap alphabet" * 100,
    ],
)
@pytest.mark.parametrize("block_size", [16, 64, 256])
def test_exact_cost_matches_serializer(data: bytes, block_size: int) -> None:
    cost = exact_shared_cost(data, block_size)
    assert cost.selected_stream_bytes == len(encode(data, block_size))


def test_sufficient_threshold_increases_with_block_size() -> None:
    small = sufficient_term_threshold(64, 5, 20, 100)
    large = sufficient_term_threshold(256, 5, 20, 100)
    assert 0 <= small < large


def test_sufficient_threshold_decreases_with_symbol_width() -> None:
    narrow = sufficient_term_threshold(256, 3, 20, 100)
    wide = sufficient_term_threshold(256, 8, 20, 100)
    assert narrow > wide


def test_normative_stream_magic_is_fisa() -> None:
    container = encode(b"normative stream")
    assert container.startswith(b"FISA\x01")
    assert decode(container) == b"normative stream"
