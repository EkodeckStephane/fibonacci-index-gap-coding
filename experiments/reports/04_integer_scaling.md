# Integer-Range Scaling

The comparison is exhaustive at every integer up to the selected limit.
It counts only the reduced-index representation and excludes all
container metadata.

| Range | Gain | Equal | Expansion | Mean gain (bits/value) |
|---|---:|---:|---:|---:|
| `1..1,000,000` | 36.87% | 17.46% | 45.67% | -0.1304 |
| `1..2,000,000` | 37.17% | 17.06% | 45.77% | -0.1301 |
| `1..5,000,000` | 39.23% | 16.51% | 44.26% | -0.0218 |
| `1..10,000,000` | 40.18% | 15.93% | 43.89% | 0.0233 |

The increasing favorable fraction does not establish complete-stream
compression because alphabet, length, framing, and padding costs are
excluded.
