# FISA 1.0 Stream Format

## Scope

The normative format stores arbitrary byte strings losslessly. It shares one
gap alphabet across a complete input stream, permits raw fallback for
individual blocks, and selects a raw-stream branch when the complete
transformed stream is not shorter.

All integer fields use unsigned LEB128 unless stated otherwise.

## Stream header

| Field | Encoding |
|---|---|
| Magic | ASCII `FISA` |
| Format identifier | one byte, value `1` |
| Stream mode | one byte: `0` raw stream, `1` shared alphabet |
| Original byte length | uvarint |

Raw-stream mode stores exactly the declared number of original bytes.

Shared mode continues with:

| Field | Encoding |
|---|---|
| Nominal block size | uvarint |
| Number of blocks | uvarint |
| Alphabet size | uvarint |
| Fixed symbol width | one byte |
| Alphabet values | one uvarint per value |

## Block record

| Field | Encoding |
|---|---|
| Mode | one byte: `0` raw, `1` shared identifiers |
| Original block length | uvarint |
| Payload length | uvarint |
| Payload | exact number of bytes declared above |

Raw mode stores the original bytes directly.

## Shared-identifier payload

1. Interpret the block as a non-negative big-endian integer `d`. The original
   block length in the block header preserves leading zero bytes.
2. Compute the exact greedy Zeckendorf index sequence
   `I = (i_0 > ... > i_{m-1})`.
3. Apply the bijective gap transform
   `g_j = i_j - i_{j+1}` and `g_{m-1} = i_{m-1}`.
4. Build one stream-level alphabet `A` by descending frequency, breaking ties
   by first occurrence.
5. Replace each gap by its zero-based index in `A`.
6. Serialize:

| Field | Encoding |
|---|---|
| Symbol count | uvarint |
| Packed byte length | uvarint |
| Packed symbol IDs | fixed-width, MSB-first, zero-padded at end |

Every byte, selector, length, alphabet value, and padding bit is included in
reported compressed size. The separate `FIPB` implementation is an
independent-alphabet experimental baseline and is not the normative format.

## Decoder invariants

- The mode and all declared lengths must be valid.
- Every symbol ID must index the serialized alphabet.
- Gap lifting reconstructs the unique descending index sequence.
- Summing exact Fibonacci integers reconstructs `d`.
- `d` must fit in the declared original block length.
- The final decoded length must equal the stream header value.
- Trailing or truncated bytes are rejected.
