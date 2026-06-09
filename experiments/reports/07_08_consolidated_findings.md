# Consolidated Experimental Findings

## Integer viability

- Gain: 368,697 (36.87%)
- Equal: 174,558 (17.46%)
- Expansion: 456,745 (45.67%)
- Mean raw gap-representation gain: -0.1304 bits/value

## Canterbury

- Best FIPB configuration per file has mean ratio `0.9782`.
- Best modern baseline per file has mean ratio `0.2456`.
- FIPB's median size is `3.61x` the
  best modern codec size.
- A FIPB configuration beats raw storage on
  `1/11` files.
- Forced Fibonacci beats raw storage on
  `1/11` files.

## Interpretation

The reduced-gap transform sometimes shortens the optimistic representation,
but complete serialization confines that effect to a narrow regime. The
scientific contribution is a complete-cost evaluation framework for amortized
positional transforms, calibrated with Fibonacci, alternative bases, and
zero-structure controls.
