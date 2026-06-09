# Result Traceability

| Manuscript claim | Authoritative experiment artifact |
|---|---|
| 36.87% gain, 17.46% equality, 45.67% expansion; mean -0.1304 bits/value | `experiments/reports/04_integer_viability.md` and `experiments/results/integer_viability.csv` |
| Scaling to 40.18% favorable and +0.0233 bits/value through 10^7 | `experiments/results/integer_scaling.csv` |
| Exact shared-stream inequality and sufficient term threshold | `experiments/reports/15_shared_stream_bounds.md` and `experiments/src/fibcodec/shared_cost.py` |
| Full-corpus FISA sensitivity from 16 to 256 bytes | `experiments/results/native_fisa_block_sizes_summary.csv` and `experiments/reports/22_native_block_size_sensitivity.md` |
| Exploratory per-block fallback sensitivity | `experiments/results/key_findings.json` and `experiments/results/canterbury_oracle_comparison.csv` |
| Ablation ratios, including Canterbury 256-byte gap 0.9439 and payload 1.6279 | `experiments/results/ablation_summary.csv` |
| Universal-code ratios | `experiments/results/universal_codes_summary.csv` |
| Full-corpus Canterbury and Silesia modern-codec ratios | `experiments/results/full_baselines_summary.csv` |
| H0, H1, and conditional-entropy differences | `experiments/results/entropy_order1.csv` and `experiments/reports/08_entropy_and_statistics.md` |
| Compiled FISA: 0.9713 Canterbury, 0.9878 complete Silesia, 1.0000001 enwik8 | `experiments/results/native_fisa_summary.csv` |
| Empirical k-star ranges and block fractions | `experiments/results/k_star_validation.csv` |
| Complete-file paired win counts and median size factors | `experiments/results/full_paired_statistics.csv` |
| Fixed-prefix versus complete-file degradation | `experiments/results/prefix_full_comparison.csv` |
| Lucas, binary-position, and matched multi-size zero-structure controls | `experiments/results/numeration_base_comparison.csv`, `experiments/results/sparse_structure_baselines.csv`, and `experiments/reports/20_sparse_structure_baselines.md` |
| Complete Huffman/Rice and per-block FIPB ratios | `experiments/results/advanced_gap_codes_summary.csv` |
| Elias--Fano and monotone-sequence results | `experiments/results/integer_sequence_codes.csv` |
| Zstandard and PPMd on complete Canterbury/Silesia | `experiments/results/full_baselines_summary.csv` |
| enwik8 ratios and SHA-256 | `experiments/results/enwik8_baselines.csv` |
| 10,119 passing tests | Final `python -m pytest experiments/tests -q` run |
| Figure 2(a)--(c) | `experiments/scripts/generate_paper_figures.py` and `paper/figures/empirical_overview.pdf` |
| Graphical abstract | `paper/graphical_abstract.tex` and `paper/graphical_abstract.pdf` |

All complete-codec ratios include serialized framing. Universal-code tables are
explicitly identified as payload-only where framing or parameter signalling is
excluded.
