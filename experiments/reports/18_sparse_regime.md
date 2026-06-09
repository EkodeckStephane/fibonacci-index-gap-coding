# Controlled Sparse-Byte Regime

Each 1 MiB file contains independently positioned non-zero bytes with
uniform values in `1..255`; all remaining bytes are zero. The generator
uses fixed seed `20260609 + density_percent`.

## Complete-stream ratios

|   density |   brotli_11 |   bzip2_9 |   fisa_native |   lzma_9 |   ppmd_6 |   zlib_9 |   zstd_19 |
|----------:|------------:|----------:|--------------:|---------:|---------:|---------:|----------:|
|  0.010000 |    0.024609 |  0.022598 |      0.864998 | 0.030186 | 0.021719 | 0.032732 |  0.026866 |
|  0.050000 |    0.103278 |  0.095105 |      1.000009 | 0.102341 | 0.091765 | 0.119860 |  0.104939 |
|  0.100000 |    0.191172 |  0.180824 |      1.000009 | 0.183685 | 0.173307 | 0.206865 |  0.193039 |
|  0.250000 |    0.374527 |  0.416308 |      1.000009 | 0.384945 | 0.383692 | 0.426072 |  0.374326 |
|  0.500000 |    0.625531 |  0.732597 |      1.000009 | 0.639198 | 0.666609 | 0.714670 |  0.626188 |
|  0.750000 |    0.857746 |  0.938292 |      1.000009 | 0.864151 | 0.897079 | 0.897266 |  0.857418 |
|  1.000000 |    1.000005 |  1.004601 |      1.000009 | 1.000107 | 1.025405 | 1.000311 |  1.000031 |

This experiment tests whether zero dominance alone provides a
competitive application regime. It does not use domain labels or
select files after observing codec performance.
