"""Bit-length models for standard positive-integer universal codes."""

from __future__ import annotations

from .transform import largest_fibonacci_index


def gamma_bits(value: int) -> int:
    if value <= 0:
        raise ValueError("Elias gamma codes positive integers")
    return 2 * (value.bit_length() - 1) + 1


def delta_bits(value: int) -> int:
    if value <= 0:
        raise ValueError("Elias delta codes positive integers")
    length = value.bit_length()
    return gamma_bits(length) + length - 1


def fibonacci_code_bits(value: int) -> int:
    if value <= 0:
        raise ValueError("Fibonacci universal codes positive integers")
    # Standard code uses F_2=1 and appends a terminal one. If F_n is the
    # largest term, positions 2..n plus the terminator occupy n bits.
    return largest_fibonacci_index(value)


def leb128_bits(value: int) -> int:
    if value < 0:
        raise ValueError("unsigned LEB128 requires non-negative integers")
    return 8 * max(1, (value.bit_length() + 6) // 7)


def rice_bits(value: int, parameter: int) -> int:
    if value <= 0 or parameter < 0:
        raise ValueError("Rice input must be positive and parameter non-negative")
    mapped = value - 1
    return (mapped >> parameter) + 1 + parameter

