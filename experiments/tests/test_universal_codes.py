from fibcodec.universal_codes import (
    delta_bits,
    fibonacci_code_bits,
    gamma_bits,
    leb128_bits,
    rice_bits,
)


def test_known_lengths():
    assert gamma_bits(1) == 1
    assert gamma_bits(8) == 7
    assert delta_bits(1) == 1
    assert delta_bits(8) == 8
    assert fibonacci_code_bits(1) == 2
    assert fibonacci_code_bits(2) == 3
    assert leb128_bits(127) == 8
    assert leb128_bits(128) == 16
    assert rice_bits(1, 0) == 1

