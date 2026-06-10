# Final major-revision report

Date: 2026-06-10

Manuscript: *Limits of Fibonacci Index-Gap Coding: Complete Stream Costs,
Compression Bounds, and Structural Controls*

## Review validation

| Reviewer point | Validation | Action |
|---|---|---|
| Missing large-scale term-count analysis | Valid in substance, but the proposed coefficient `0.694 ell` is incorrect | Added Lekkerkerker scaling: `E[t] = ell / ((phi^2+1) log2(phi)) + O(1)`, with coefficient `0.3981`. |
| About 1,421 terms for a 2048-bit integer | Incorrect | The correct leading prediction is about 815 terms. |
| Link between generic blocks and `k*` | Valid | Added a deterministic 5,000-sample experiment at each exact bit length from 128 to 2048. The 2048-bit mean is 815.63; no sampled value meets the 326 or 392 thresholds. |
| The `1..10^7` integer study is not representative of 256-byte blocks | Valid and already acknowledged, but the theoretical bridge was missing | Kept the finite-range warning and added asymptotic term-count analysis plus large-integer simulation. No unsupported extrapolation of the favorable fraction was made. |
| Block-as-one-integer loses sequential structure | Valid as a modelling criticism, but not as information destruction | Strengthened the Discussion: the transform is invertible, yet its identifier model does not expose byte adjacency. The measured first-order reductions and 3.92--4.23 size factors are now linked explicitly. |
| ANS absent from related work | Valid | Added Duda et al. (PCS 2015) and the Zstandard FSE specification. The text states precisely what ANS can and cannot remove. |
| FISA presented as a proposed competitive method | Partly outdated | Renamed Section 4 to `FISA 1.0 test format` and stated that it exists to make the accounting experiment reproducible. |
| Missing best- and worst-case analysis | Valid | Added a universal raw-fallback upper bound and an exact all-zero constructive case. A 1 MiB zero stream at 256 bytes has ratio 0.02345. |
| `A` versus `mathcal{A}` notation | Valid | Standardized the alphabet notation throughout prose, equations, and pseudocode. |
| Abstract/Table range mismatch | Incorrect | Both ranges were already explicit. The abstract still states `1..10^7`; the numeration table states `1..10^6`. |
| `OpenAI Codex` is factually wrong | Incorrect | The work used the current OpenAI Codex coding agent. The declaration now says this explicitly to avoid confusion with the retired legacy model. |
| Python 3.13.5 did not exist | Incorrect | Python 3.13.5 is the locally recorded runtime and was released on 2025-06-11. It remains unchanged. |
| FibonacciTable appears to rebuild on every call | Partly valid as a pseudocode-reading concern | Added a note that the pseudocode is self-contained and the compiled implementation caches the table across blocks. |
| FIPB is not compared | Incorrect as stated | Figure 3 and its text already compare FIPB directly with FISA: 1.5849 vs 0.9713 on Canterbury and 1.5955 vs 0.9608 on Silesia prefixes. No redundant table was added. |
| Structural controls are not compared with modern codecs | Partly valid as a presentation issue | Added the direct weighted comparisons in the structural-control subsection. |
| Big-endian choice is untested | Valid | Added an exactly reversible little-endian sensitivity experiment. Differences are small and do not change the conclusion. |
| Reposition for Information Processing & Management | Venue concern is valid | No artificial information-retrieval claim was inserted. The manuscript remains better aligned with a general computer-science or compression venue unless an index-compression study is added. |

## New evidence

### Zeckendorf term scaling

- Seed: `20260610`
- Samples: `5,000` per exact bit length
- Bit lengths: `128, 256, 512, 1024, 2048`
- 2048-bit prediction: `815.35` terms
- 2048-bit simulated mean: `815.63`
- Simulated range: `748..873`
- Samples at or below 392 terms: `0/5000`
- Samples at or below 326 terms: `0/5000`

Artifacts:

- `experiments/scripts/analyze_zeckendorf_scaling.py`
- `experiments/results/zeckendorf_term_scaling.csv`
- `experiments/reports/22_zeckendorf_term_scaling.md`

### Byte-order sensitivity

At 256-byte blocks:

| Corpus | Big-endian | Reversible little-endian |
|---|---:|---:|
| Canterbury | 0.971250 | 0.971170 |
| Silesia fixed prefixes | 0.960765 | 0.958045 |

Artifacts:

- `experiments/scripts/evaluate_byte_order.py`
- `experiments/results/byte_order_sensitivity.csv`
- `experiments/reports/23_byte_order_sensitivity.md`

## Manuscript changes

- Added ANS to Related Work with a peer-reviewed primary citation.
- Added exact stream bounds and an all-zero cost formula.
- Added a formal expected-term-count subsection.
- Added a cited, editable term-scaling table.
- Replaced the misleading 40.18% highlight with the large-block term-count result.
- Strengthened the discussion of sequential dependence.
- Added direct structural-control versus modern-codec comparisons.
- Clarified byte-order sensitivity and the AI-tool identity.
- Kept all figures as separate vector files or editable TikZ.
- Kept all tables as editable LaTeX without vertical rules or shading.

## Verification

- `10,119` tests passed.
- All `41` required release artifacts are present and nonempty.
- The PDF compiles to 15 physical pages, including the unnumbered opening page.
- No undefined citation or cross-reference remains.
- Visual inspection covered the abstract, analytical bounds, expected-term
  section, new table, limitations, and references.
- `paper/generate_review.py` remains untracked and is excluded from Git.

## Second-check follow-up

The claim that the nine major revisions were absent from the LaTeX source was
checked against commit `19ef854` and found to be based on an older manuscript.
ANS, the FISA test-format title, term-count scaling, stream bounds, the revised
highlight, direct structural comparisons, byte-order sensitivity, and the
strengthened dependence discussion were already present.

The valid new observations were incorporated:

- enwik8 is now reported as exactly `1.0000001`, or 10 framing bytes above the
  100,000,000-byte raw input;
- the within-implementation encode/decode asymmetry is quantified and
  explained;
- zero controls are compared directly with both byte RLE and zlib;
- a compact per-file table reports `ptt5`, `mozilla`, `mr`, `ooffice`, and
  `x-ray`;
- the IP&M cover letter was replaced by an Information Sciences letter.

Information Sciences was selected because its official scope explicitly lists
information theory, algorithm design, computer-system evaluation, and data
compression. This retains the Elsevier CAS manuscript format without adding an
unsupported information-retrieval application.

## Toolchain note

The manuscript compiled successfully with explicit `pdflatex`, `bibtex`, and
subsequent `pdflatex` passes. The local MiKTeX installation currently cannot
run `latexmk` because Perl is unavailable. Some MiKTeX utilities also attempt
to initialize an obsolete roaming profile, but this did not prevent creation
of the final resolved PDF.
