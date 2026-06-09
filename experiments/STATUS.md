# FISA 1.0 Release Status

The release package is complete.

## Included evidence

- Complete lossless FISA 1.0 format specification.
- Exact encoder, decoder, serializer, and malformed-stream checks.
- Correctness proofs and complexity analysis.
- Exhaustive integer scaling over `1..10,000,000`.
- Synthetic, Canterbury, complete Silesia, and enwik8 measurements.
- Compiled Java FISA implementation with encode/decode throughput.
- Lucas, binary-position, zero-bitmap, and zero-trim structural controls.
- Universal integer-code, Huffman, Rice, Elias--Fano, and modern-codec
  comparisons.
- Statistical analysis, entropy measurements, ablations, and sensitivity
  results.
- Elsevier manuscript, bibliography, figures, graphical abstract, and PDF.

## Verification

- Automated tests: `10,119 passed`.
- Exact decode-after-encode verification for every measured FISA stream.
- Five authors with approved affiliation, contact, ORCID, and CRediT metadata.
- Complete serialized-size accounting, including alphabets, lengths, headers,
  padding, mode indicators, and raw fallback.
