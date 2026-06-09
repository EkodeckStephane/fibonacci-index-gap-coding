# Mathematical Foundation and Complexity

## Correct uniqueness statement

For every positive integer `d`, Zeckendorf's theorem gives a unique sum of
non-consecutive Fibonacci numbers when the conventional sequence
`F_2 = 1, F_3 = 2, ...` is used. The greedy largest-term algorithm recovers
that representation.

For an index vector `I = (i_0, ..., i_{m-1})`, define

`R(I) = (i_0-i_1, ..., i_{m-2}-i_{m-1}, i_{m-1})`.

The inverse is the suffix-sum map:

`i_{m-1}=g_{m-1}` and `i_j=g_j+i_{j+1}`.

Therefore `R` is bijective. Uniqueness of the reduced index vector follows
from Zeckendorf uniqueness and does not require a permutation argument.

## Important negative result

A bijection cannot reduce Shannon entropy when applied to an isolated random
variable and the output is represented without changing the probability model:
`H(R(X)) = H(X)`. Compression can arise only from a code that exploits the
distribution or structure of the transformed representation, and all
side-information must be counted.

The empirical byte entropy `H0` is reported as a descriptive statistic. It is
not treated as a universal lower bound for finite files or compressors that
exploit runs, dictionaries, or higher-order context; such codecs can validly
produce fewer than `n H0` bits.

The claim that the reduced-index representation is always shorter than binary
is false. The experiments explicitly measure expansion, equality, and gain.

## Complexity

Let `b` be the bit length of a block integer and `m` the number of terms in its
Zeckendorf representation.

- Fast doubling computes `F_n` exactly in `O(M(b) log n)` bit operations,
  where `M(b)` is the cost of multiplying `b`-bit integers.
- Locating each largest Fibonacci index uses exponential bracketing and binary
  search. The reference implementation prioritizes clarity over caching.
- Greedy decomposition performs `m` exact big-integer subtractions and index
  searches. Since non-consecutive indices are selected and the largest index is
  `Theta(b)`, `m = O(b)`.
- Gap reduction and lifting are `O(m)`.
- Alphabet construction is expected `O(m)` with hashing plus
  `O(k log k)` sorting for `k` distinct gaps.
- Memory is `O(b + m)` bits excluding interpreter overhead.

These bounds do not justify a constant-time claim for Binet's formula.
Floating-point Binet evaluation is not exact for practical block sizes and is
not used.
