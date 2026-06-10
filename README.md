# Limits of Fibonacci Index-Gap Coding (FISA 1.0)

Reference implementation, experimental evidence, and Elsevier manuscript for:

> **Limits of Fibonacci Index-Gap Coding:
> Complete Stream Costs, Compression Bounds, and Structural Controls**

FISA is an exact lossless representation that interprets each byte block as a
non-negative integer, computes its greedy Zeckendorf decomposition, and encodes
the gaps between consecutive Fibonacci indices. The repository evaluates when
this structured representation is useful after all headers, alphabets, lengths,
mode indicators, and padding bits are counted.

The release includes the codec, tests, fixed configurations, generated and
public-corpus experiments, machine-readable results, statistical analyses,
publication figures, graphical abstract, and compiled manuscript.

## Contents

- [Scientific scope](#scientific-scope)
- [How FISA works](#how-fisa-works)
- [Container formats](#container-formats)
- [Key results](#key-results)
- [Repository structure](#repository-structure)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Python usage](#python-usage)
- [Reproducing the experiments](#reproducing-the-experiments)
- [Experimental datasets](#experimental-datasets)
- [Baselines and measurements](#baselines-and-measurements)
- [Building the manuscript](#building-the-manuscript)
- [Result traceability](#result-traceability)
- [Citation](#citation)
- [Authors and contact](#authors-and-contact)

## Scientific scope

A shorter intermediate representation is not necessarily a shorter serialized
bitstream. The evaluation separates five questions:

1. Is the Fibonacci index-gap transform exactly reversible?
2. For which integers are reduced indices shorter than the direct binary form?
3. How much space is consumed by alphabets, lengths, framing, and padding?
4. How does the complete representation compare with integer codes and
   established lossless codecs?
5. How strongly does the complete stream depend on block size?

The study treats FISA as an exactly specified experimental instance of
amortized positional coding. Lucas, binary-position, zero-block, and zero-trim
controls determine which effects are Fibonacci-specific. FISA is not presented
as a replacement for mature compressors or simpler sparse-data formats.

## How FISA works

For an input block `x`:

1. Interpret `x` as a big-endian non-negative integer `d`.
2. Compute the greedy Zeckendorf representation
   `d = F(i_0) + F(i_1) + ... + F(i_k)`, with descending, non-consecutive
   indices.
3. Replace the index sequence with the bijective gap sequence:

   ```text
   g_j = i_j - i_(j+1),  for 0 <= j < k
   g_k = i_k
   ```

4. Build a frequency-ordered alphabet of distinct gaps.
5. Replace each gap by its alphabet identifier and bit-pack the identifiers.
6. Serialize every parameter required for exact decoding.
7. Store the raw bytes when the complete transformed representation is not
   shorter.

Leading zero bytes are preserved through the declared original block length.
The decoder rejects invalid modes, truncated payloads, out-of-range symbols,
inconsistent lengths, and trailing bytes.

## Container formats

The implementation provides two exact formats.

### Independent per-block baseline: `FIPB`

Implemented in
[`experiments/src/fibcodec/codec.py`](experiments/src/fibcodec/codec.py).

| Field | Encoding |
|---|---|
| Magic | ASCII `FIPB` |
| Format identifier | One byte, value `1` |
| Nominal block size | Unsigned LEB128 |
| Original stream length | Unsigned LEB128 |
| Number of blocks | Unsigned LEB128 |
| Block mode | `0` for raw, `1` for Fibonacci |
| Block and payload lengths | Unsigned LEB128 |
| Payload | Raw bytes or complete Fibonacci payload |

Each payload carries its own alphabet and packed symbol stream. This format is
an experimental baseline, not the normative format.

### Shared-alphabet stream: `FISA`

Implemented in
[`experiments/src/fibcodec/shared_codec.py`](experiments/src/fibcodec/shared_codec.py).

| Field | Encoding |
|---|---|
| Magic | ASCII `FISA` |
| Format identifier | One byte, value `1` |
| Stream mode | `0` for raw, `1` for shared-alphabet coding |
| Shared metadata | Block size, block count, alphabet, and symbol width |
| Block records | Mode, original length, payload length, and payload |

`FISA` amortizes one gap alphabet across the stream. It also compares the
complete transformed stream with a raw-stream representation and keeps the
shorter one.

The normative field description is available in
[`experiments/reports/01_format_specification.md`](experiments/reports/01_format_specification.md).

## Key results

All ratios below are `serialized bytes / original bytes`; smaller is better.
Complete-codec results include framing and side information.

### Integer-level characterization

The integer-range evaluation enumerates every value in `1..10,000,000`.
This finite range reaches about 24 bits; larger block integers are evaluated
through the corpus experiments:

| Upper limit | Reduced | Equal | Expanded | Mean gain before metadata |
|---:|---:|---:|---:|---:|
| `10^6` | 36.87% | 17.46% | 45.67% | -0.1304 bits/value |
| `2 x 10^6` | 37.17% | 17.06% | 45.77% | -0.1301 bits/value |
| `5 x 10^6` | 39.23% | 16.51% | 44.26% | -0.0218 bits/value |
| `10^7` | **40.18%** | 15.93% | 43.89% | **+0.0233 bits/value** |

### Calibrated sufficient threshold

For complete 256-byte blocks, the sufficient threshold is `k* = 390..392`
terms across Canterbury files and `k* = 326` across Silesia files. Only
`3.70%` of Canterbury blocks and `1.94%` of Silesia blocks satisfy the bound;
the observed shared-mode fractions are `3.75%` and `1.94%`.

Lekkerkerker's theorem predicts about `0.3981 x bit_length` Zeckendorf terms
for generic large integers. A deterministic 5,000-sample check gives a mean of
`815.63` terms for 2048-bit integers, and none of those samples falls below
the measured 256-byte thresholds. The favorable corpus blocks are therefore
strongly non-generic.

The raw fallback bounds every FISA stream above by
`1 + framing/input_size`. At the opposite extreme, the exact all-zero formula
gives ratio `0.02345` for a 1 MiB stream with 256-byte blocks. This constructive
case shows that FISA can represent highly structured data compactly, although
the zero-trim and bitmap controls remain better explanations of the corpus
gains.

### Complete positional representations

Full-corpus FISA block-size sensitivity:

| Block bytes | Canterbury | Silesia |
|---:|---:|---:|
| 16 | 0.9274 | 0.9978 |
| 32 | **0.9215** | 0.9930 |
| 64 | 0.9354 | 0.9905 |
| 128 | 0.9593 | 0.9900 |
| 256 | 0.9713 | **0.9878** |

Only one Canterbury file compresses at every tested size. Silesia has one
compressed file through 128 bytes and two at 256 bytes. On enwik8, the
256-byte format selects the raw-stream branch and writes `100,000,010` bytes
for a `100,000,000`-byte input, a ratio of `1.0000001`.

Matched structural-control sweeps remain smaller. Their best weighted ratios
are `0.8936` for the zero-block bitmap and `0.8942` for zero trim on
Canterbury, and `0.9774` and `0.9833` on Silesia.

On complete files, the modern-codec oracle wins all `11/11` Canterbury and
`12/12` Silesia paired comparisons. Runtime measurements remain available in
the result files, but the paper makes no cross-codec speed claim because the
implementations use different runtimes and bindings.

Within the compiled FISA implementation, Canterbury encodes at `0.758 MiB/s`
and decodes at `113.3 MiB/s`; Silesia encodes at `1.423 MiB/s` and decodes at
`1305.9 MiB/s`. Encoding decomposes every candidate block, whereas decoding
mostly copies raw blocks.

A reversible byte-order sensitivity check changes the 256-byte weighted ratio
from `0.971250` to `0.971170` on Canterbury and from `0.960765` to `0.958045`
on fixed Silesia prefixes. The format remains normatively big-endian; this
control shows that endianness does not change the conclusion.

### Established codec comparison

Best measured full-corpus weighted ratios:

| Corpus | Best measured baseline | Weighted ratio |
|---|---|---:|
| Canterbury | Brotli quality 11 | **0.1746** |
| Silesia | LZMA preset 9 | **0.2302** |

These results delimit the contribution precisely: the work provides a
stream-level cost analysis and structural controls for an amortized positional
transform, while established codecs remain substantially more effective on
standard corpora.

Authoritative values are stored in
[`experiments/results/`](experiments/results/) and mapped to manuscript claims
in [`paper/RESULT_TRACEABILITY.md`](paper/RESULT_TRACEABILITY.md).

## Repository structure

```text
.
|-- README.md
|-- experiments/
|   |-- config/       Pinned experiment configurations
|   |-- data/         Generated data and fixed evaluation samples
|   |-- figures/      Generated analysis figures
|   |-- reports/      Format, protocol, theory, and positioning documents
|   |-- results/      CSV and JSON measurements
|   |-- scripts/      Corpus preparation, experiments, and analysis
|   |-- src/fibcodec/ Reference Python implementation
|   |-- native/java/  Compiled FISA implementation
|   |-- tests/        Correctness and malformed-stream tests
|   `-- run_reproducibility.ps1
`-- paper/
    |-- fibonacci_inspired_entropy_reduction.tex
    |-- fibonacci_inspired_entropy_reduction.pdf
    |-- cas-refs.bib
    |-- figures/
    |-- graphical_abstract.tex
    |-- graphical_abstract.pdf
    `-- RESULT_TRACEABILITY.md
```

Downloaded third-party corpora are excluded from version control. Fixed
samples, generated datasets, configurations, derived measurements, and scripts
needed to audit the reported claims are included.

## Requirements

- Python 3.10 or newer
- Java 8 or newer (`javac` and `java`) for the compiled full-corpus evaluation
- PowerShell for the one-command reproduction workflow
- A LaTeX distribution providing `pdflatex` and `bibtex` to rebuild the paper

Python dependencies are pinned in
[`experiments/requirements.txt`](experiments/requirements.txt):

- NumPy, pandas, SciPy, and tabulate for analysis
- Matplotlib for figures
- Brotli, PPMd, and Zstandard bindings for codec baselines
- pytest for verification

## Quick start

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r experiments\requirements.txt
python -m pytest experiments\tests -q
```

Expected verification result for FISA 1.0:

```text
10119 passed
```

On Linux or macOS, activate the environment with:

```bash
source .venv/bin/activate
python -m pip install -r experiments/requirements.txt
python -m pytest experiments/tests -q
```

## Python usage

The project uses a `src` layout and is not packaged on PyPI. Add
`experiments/src` to `PYTHONPATH` when importing it directly.

### Shared-alphabet FISA 1.0

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path("experiments/src").resolve()))

from fibcodec.shared_codec import decode, encode

source = b"\x00\x00Fibonacci index-gap coding example"
container = encode(source, block_size=256)
restored = decode(container)

assert restored == source
print(f"input={len(source)} bytes")
print(f"container={len(container)} bytes")
print(f"magic={container[:4]!r}")
```

### Per-block FIPB baseline

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path("experiments/src").resolve()))

from fibcodec import decode, encode

source = Path("input.bin").read_bytes()
container = encode(source, block_size=256, allow_raw=True)
restored = decode(container)

assert restored == source
Path("input.fipb").write_bytes(container)
```

The implementation is a clarity-oriented research reference. Runtime
comparisons with optimized native compressors should therefore be interpreted
as descriptive rather than implementation-equivalent.

## Reproducing the experiments

### Complete workflow

From the repository root on Windows:

```powershell
.\experiments\run_reproducibility.ps1
```

The runner performs the following operations in order:

1. Execute the complete test suite.
2. Generate deterministic synthetic corpora.
3. Generate integer-sequence corpora.
4. Characterize integer scaling through `10,000,000`.
5. Run synthetic, Canterbury, and fixed Silesia-sample experiments.
6. Run full general-purpose codec baselines.
7. Run enwik8 baselines.
8. Run format ablations.
9. Compare universal integer codes.
10. Compare shared-alphabet, Huffman, Rice, and Elias-Fano variants.
11. Run compiled FISA on complete Canterbury, Silesia, and enwik8.
12. Compare Lucas, binary-position, zero-bitmap, and zero-trim controls.
13. Compute entropy, sparsity, and statistical analyses.
14. Consolidate results and verify all required release artifacts.

The complete campaign downloads or prepares public corpora and can take
several hours.

### Individual stages

Each stage can also be executed separately:

```powershell
python experiments\scripts\generate_synthetic_corpus.py
python experiments\scripts\generate_integer_sequence_corpus.py
python experiments\scripts\characterize_integers.py
python experiments\scripts\run_experiments.py --config experiments\config\experiment.json
python experiments\scripts\run_experiments.py --config experiments\config\canterbury.json
python experiments\scripts\prepare_silesia_sample.py
python experiments\scripts\run_experiments.py --config experiments\config\silesia_sample.json
python experiments\scripts\run_full_baselines.py
python experiments\scripts\run_enwik8_baselines.py
python experiments\scripts\run_ablation.py
python experiments\scripts\compare_universal_codes.py
python experiments\scripts\compare_advanced_codes.py
python experiments\scripts\analyze_entropy_statistics.py
python experiments\scripts\summarize_all.py
python experiments\scripts\verify_completion.py
```

The final artifact audit is written to
[`experiments/results/completion_audit.json`](experiments/results/completion_audit.json).

## Experimental datasets

| Dataset | Use in the study |
|---|---|
| Deterministic synthetic files | Controlled structure and sensitivity analysis |
| Integers `1..10,000,000` | Finite-range representation-level scaling |
| Canterbury corpus | Standard lossless-compression evaluation |
| Silesia corpus | Full modern-codec baselines |
| Fixed 64 KiB sample of each Silesia file | Prefix sensitivity and ablation |
| enwik8 | Large text-compression reference |
| Generated monotone integer sequences | Universal codes and Elias-Fano |

The synthetic generator uses seed `20260608`. Corpus preparation, archive
hashes, block sizes, repetition counts, and measurement rules are documented
in [`experiments/reports/05_protocol.md`](experiments/reports/05_protocol.md)
and [`experiments/config/`](experiments/config/).

## Baselines and measurements

### Compared representations

- Raw bytes and byte-level run-length encoding
- zlib level 9
- bzip2 level 9
- LZMA preset 9
- Brotli quality 11
- Zstandard level 19
- PPMd
- Fibonacci, Elias gamma, and Elias delta integer codes
- Complete Huffman and Rice coding of Fibonacci gaps
- Elias-Fano on monotone integer sequences
- Greedy Lucas and binary set-position gaps
- Complete zero-block bitmap and per-block zero trimming

### Reported measurements

- Complete serialized size and compression ratio
- Bits per input byte
- Exact encode/decode round-trip validation
- Wall-clock encoding time and throughput
- Peak Python allocation for selected campaigns
- Byte-level empirical entropy
- Ablation and block-size sensitivity
- Paired non-parametric statistical tests

Payload-only tables are explicitly labelled where framing or parameter
signalling is excluded. Complete-codec tables count every serialized field.

## Building the manuscript

The compiled manuscript is available at
[`paper/fibonacci_inspired_entropy_reduction.pdf`](paper/fibonacci_inspired_entropy_reduction.pdf).

To rebuild it:

```powershell
Set-Location paper
pdflatex -interaction=nonstopmode -halt-on-error fibonacci_inspired_entropy_reduction.tex
bibtex fibonacci_inspired_entropy_reduction
pdflatex -interaction=nonstopmode -halt-on-error fibonacci_inspired_entropy_reduction.tex
pdflatex -interaction=nonstopmode -halt-on-error fibonacci_inspired_entropy_reduction.tex
```

To rebuild the graphical abstract:

```powershell
Set-Location paper
pdflatex -interaction=nonstopmode -halt-on-error graphical_abstract.tex
```

The Elsevier CAS class, bibliography style, bibliography, figures, and
thumbnail dependencies required by the manuscript are included under
[`paper/`](paper/).

## Result traceability

The repository is organized so that every numerical manuscript claim can be
traced to a CSV, JSON, report, or generation script.

| Evidence | Location |
|---|---|
| Claim-to-result map | [`paper/RESULT_TRACEABILITY.md`](paper/RESULT_TRACEABILITY.md) |
| Release status | [`experiments/STATUS.md`](experiments/STATUS.md) |
| Complete format | [`experiments/reports/01_format_specification.md`](experiments/reports/01_format_specification.md) |
| Experimental protocol | [`experiments/reports/05_protocol.md`](experiments/reports/05_protocol.md) |
| Scientific positioning | [`experiments/reports/10_scientific_positioning.md`](experiments/reports/10_scientific_positioning.md) |
| Machine-readable results | [`experiments/results/`](experiments/results/) |
| Figure generator | [`experiments/scripts/generate_paper_figures.py`](experiments/scripts/generate_paper_figures.py) |

## Citation

Until a journal DOI is assigned, cite the manuscript and repository as:

```bibtex
@misc{Ekodeck2026FISA,
  author       = {Stéphane Gaël R. Ekodeck and Hervé Talé Kalachi and
                  Serge Alain Ebélé and Norbert Djong Wang and
                  Chantal Marguerite Mveh-Abia},
  title        = {Limits of Fibonacci Index-Gap Coding:
                  Complete Stream Costs, Compression Bounds,
                  and Structural Controls},
  year         = {2026},
  howpublished = {\url{https://github.com/EkodeckStephane/fibonacci-index-gap-coding}},
  note         = {FISA 1.0}
}
```

## Authors and contact

- Stéphane Gaël R. Ekodeck
- Hervé Talé Kalachi
- Serge Alain Ebélé
- Norbert Djong Wang, ORCID [`0009-0008-6902-0233`](https://orcid.org/0009-0008-6902-0233)
- Chantal Marguerite Mveh-Abia, ORCID [`0009-0005-9398-1067`](https://orcid.org/0009-0005-9398-1067)

Corresponding author:
[stephane-gael.ekodeck@facsciences-uy1.cm](mailto:stephane-gael.ekodeck@facsciences-uy1.cm)

Repository:
[github.com/EkodeckStephane/fibonacci-index-gap-coding](https://github.com/EkodeckStephane/fibonacci-index-gap-coding)
