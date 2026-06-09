# Numeration-Basis Comparison

Exhaustive range: `1..1,000,000`.

All methods encode gaps between greedy term indices using the same
optimistic sum of individual gap bit lengths. Container metadata is
excluded. Fibonacci uses the canonical Zeckendorf basis `(1, 2, ...)`.
Lucas uses the greedy basis `(1, 3, 4, ...)`; unlike Zeckendorf, this
representation is not claimed to be unique. Binary sparse coding uses
the positions of set bits.

| Method | Gain | Equal | Expansion | Mean gap bits | Mean terms | Unique best |
|---|---:|---:|---:|---:|---:|---:|
| fibonacci | 36.87% | 17.46% | 45.67% | 19.0818 | 7.8945 | 5.36% |
| lucas_greedy | 48.35% | 18.07% | 33.59% | 18.4216 | 8.1328 | 9.62% |
| binary_sparse | 98.39% | 1.61% | 0.00% | 15.4673 | 9.8850 | 73.67% |

Cross-method ties for best optimistic length: 11.35%.
