# Reproducible Experimental Protocol

## Corpora

- Synthetic: seven deterministic 64 KiB files generated with seed `20260608`.
- Canterbury: all 11 files from the standard official archive.
- Silesia: all 12 files from the official archive.
- Silesia sample: first 64 KiB of each Silesia file, retained for block-size
  sensitivity and direct comparison with the Python reference.
- Complete Silesia: all files evaluated by the compiled FISA implementation.
- enwik8: complete 100,000,000-byte benchmark evaluated by compiled FISA and
  general-purpose baselines.

Archive SHA-256:

- Canterbury: `405FEE48AA1625BBFA13064FBEFB03AB92B92AF69D3DBF586214804ED9F171BF`
- Silesia: `0626E25F45C0FFB5DC801F13B7C82A3B75743BA07E3A71835A41E3D9F63C77AF`

## Measurements

- Complete serialized bytes and compressed/original ratio.
- Bits per input byte.
- Median wall-clock encoding time and throughput.
- Peak Python allocation measured by `tracemalloc` for prototype campaigns.
- Byte-level empirical `H0` as a descriptive statistic.
- Exact decode-after-encode verification for every FISA run.

## Baselines

- Raw bytes.
- Byte RLE.
- zlib level 9.
- bzip2 level 9.
- LZMA preset 9.
- Brotli quality 11.

The modern baselines are run on complete Canterbury and Silesia files.

## Prototype configurations

- Block sizes: 64, 256, and 512 bytes for standard-corpus campaigns.
- Both forced Fibonacci and per-block raw-fallback modes.
- One run for expensive prototype campaigns; deterministic output size.
- Synthetic exploratory campaign uses three repetitions.

Compiled FISA measurements report complete encode and decode times after exact
round-trip verification. Timing comparisons remain implementation-specific:
FISA uses Java `BigInteger`, while mature baselines use optimized native
libraries. Compression sizes are directly comparable because every format is
complete and decodable.
