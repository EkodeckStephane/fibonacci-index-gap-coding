# Fibonacci-Inspired Entropy Reduction Experiments

This directory contains the reproducible implementation and evidence used to
evaluate the Fibonacci-inspired transform reported in the manuscript under
`paper/`.

## Reproducibility workflow

1. Formalize the complete lossless bitstream.
2. Build an exact reference implementation.
3. Correct the mathematical foundations and complexity claims.
4. Test viability before making compression claims.
5. Establish a reproducible protocol.
6. Implement scientifically relevant baselines.
7. Produce statistical analysis and ablations.
8. Evaluate empirical entropy and redundancy.
9. Verify the state of the art and bibliography.
10. Establish the scientific positioning from measured results.
11. Build the Elsevier submission package and traceability record.

Release status is recorded in `STATUS.md`.

## Layout

- `src/fibcodec/`: exact codec and analysis library.
- `native/java/`: compiled FISA implementation and full-corpus benchmark.
- `tests/`: correctness and format tests.
- `scripts/`: corpus preparation, experiments, analysis, and reporting.
- `data/`: downloaded or generated corpora.
- `results/`: machine-readable measurements.
- `figures/`: generated publication-quality figures.
- `reports/`: theory notes, audits, and scientific positioning.
- `config/`: pinned experiment configuration.

Downloaded third-party corpora are excluded from version control. The
preparation scripts retrieve or reconstruct the required inputs, while fixed
samples, generated data, configurations, and derived measurements needed to
audit the reported results remain in the repository.

## Quick start

```powershell
python -m pip install -r experiments/requirements.txt
python -m pytest experiments/tests -q
.\experiments\run_reproducibility.ps1
```

The full runner regenerates all measured tables and may take several hours.
`experiments/results/completion_audit.json` records the final artifact audit.
FISA 1.0 uses a shared-alphabet stream with exact raw fallback. The `FIPB`
container is retained only as an independent per-block experimental baseline.
Advanced comparisons include complete Huffman and Rice gap codes, Elias--Fano
on monotone sequences, Lucas and binary positional controls, zero-structure
baselines, Zstandard, PPMd, complete Silesia, and enwik8.
