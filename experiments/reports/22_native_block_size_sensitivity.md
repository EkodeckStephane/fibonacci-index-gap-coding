# Native FISA Block-Size Sensitivity

All values use complete files and include stream framing.

| Corpus | Block bytes | Weighted ratio | Compressed files | Shared blocks (%) |
|---|---:|---:|---:|---:|
| canterbury | 16 | 0.927384 | 1 | 12.956 |
| silesia | 16 | 0.997784 | 1 | 3.084 |
| canterbury | 32 | 0.921490 | 1 | 11.353 |
| silesia | 32 | 0.993006 | 1 | 2.745 |
| canterbury | 64 | 0.935432 | 1 | 9.136 |
| silesia | 64 | 0.990500 | 1 | 2.497 |
| canterbury | 128 | 0.959251 | 1 | 6.100 |
| silesia | 128 | 0.989998 | 1 | 2.227 |
| canterbury | 256 | 0.971250 | 1 | 3.750 |
| silesia | 256 | 0.987821 | 2 | 1.938 |

Canterbury is smallest at 32 bytes; Silesia is smallest at 256 bytes.
No tested size produces broad file-level compression.
