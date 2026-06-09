# Entropy and Paired Statistical Analysis

Empirical `H0` and first-order conditional entropy `H1` are descriptive
statistics, not universal finite-file lower bounds.

## Entropy

| Corpus | Files | Mean H0 | Mean H1 | Mean H0-H1 |
|---|---:|---:|---:|---:|
| canterbury | 11 | 4.4051 | 3.0015 | 1.4036 |
| silesia_sample | 12 | 5.0498 | 3.4052 | 1.6446 |

## Paired comparison

For each file, the oracle selects the smallest measured FIPB variant and
the smallest modern baseline. The one-sided Wilcoxon signed-rank test
tests whether `FIPB ratio - modern ratio` is greater than zero.

| Corpus | Files | FIPB wins | Modern wins | Median factor | p-value |
|---|---:|---:|---:|---:|---:|
| canterbury | 11 | 0 | 11 | 3.606 | 0.000488281 |
| silesia_sample | 12 | 0 | 12 | 3.469 | 0.000244141 |

All files favor the modern-codec oracle. This is consistent with the
serialization and ablation results: reduced gaps can be locally shorter,
but alphabet and symbol-stream costs dominate the complete format.
