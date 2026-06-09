# Reference Implementation and Verification

The exact implementation is in `experiments/src/fibcodec/`.

- `transform.py`: exact Fibonacci fast doubling, greedy Zeckendorf
  decomposition, gap reduction, inverse lifting, and reconstruction.
- `shared_codec.py`: normative FISA 1.0 stream, shared alphabet, stream and
  block fallback, encoder, decoder, and malformed-stream rejection.
- `codec.py`: independent per-block `FIPB` experimental baseline.
- `varint.py` and `bitpack.py`: unsigned LEB128 and fixed-width bit packing.
- `universal_codes.py`: gamma, delta, Fibonacci, Rice, and LEB128 length
  baselines.

The test suite covers every integer from 1 through 9,999, multiple arbitrary
byte strings, leading zero bytes, block sizes, malformed streams, and
universal-code length identities. The final verification run on 9 June 2026
reported:

`10119 passed`

Every experimental FISA encoding is decoded and compared byte-for-byte with
its input before its measurement row is accepted.
