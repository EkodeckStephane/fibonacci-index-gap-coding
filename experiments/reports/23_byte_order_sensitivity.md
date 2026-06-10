# Byte-Order Sensitivity

Each little-endian candidate reverses bytes inside every block before
encoding and reverses them again after decoding. The transform is therefore
exactly reversible and differs only in the integer interpretation.

| Corpus | Order | Block (bytes) | Weighted ratio |
|---|---|---:|---:|
| canterbury | big | 256 | 0.971250 |
| canterbury | little | 256 | 0.971170 |
| silesia_sample | big | 256 | 0.960765 |
| silesia_sample | little | 256 | 0.958045 |

The small differences do not alter the corpus-level conclusion.
Silesia uses the fixed 64 KiB prefixes for this sensitivity test.
