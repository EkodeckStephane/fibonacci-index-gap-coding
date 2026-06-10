from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

REQUIRED = [
    "reports/01_format_specification.md",
    "reports/02_reference_implementation.md",
    "src/fibcodec/codec.py",
    "reports/03_theory_and_complexity.md",
    "results/integer_viability.csv",
    "results/integer_scaling.csv",
    "results/numeration_base_comparison.csv",
    "reports/05_protocol.md",
    "results/universal_codes_summary.csv",
    "results/advanced_gap_codes_summary.csv",
    "results/integer_sequence_codes.csv",
    "reports/13_advanced_baselines.md",
    "reports/14_sota_2020_2026_update.md",
    "results/paired_statistics.csv",
    "results/entropy_order1.csv",
    "reports/10_scientific_positioning.md",
    "reports/11_elsevier_preparation.md",
    "reports/11_author_metadata_snapshot.md",
    "results/benchmark_canterbury.csv",
    "results/benchmark_silesia_sample.csv",
    "results/full_baselines.csv",
    "results/enwik8_baselines.csv",
    "native/java/FisaBenchmark.java",
    "results/native_fisa_summary.csv",
    "results/k_star_validation.csv",
    "results/full_paired_statistics.csv",
    "results/throughput_comparison.csv",
    "results/prefix_full_comparison.csv",
    "results/sparse_regime.csv",
    "results/sparse_structure_baselines.csv",
    "results/zeckendorf_term_scaling.csv",
    "results/byte_order_sensitivity.csv",
    "reports/15_shared_stream_bounds.md",
    "reports/16_native_full_corpus.md",
    "reports/17_numeration_base_comparison.md",
    "reports/18_sparse_regime.md",
    "reports/20_sparse_structure_baselines.md",
    "reports/21_revision_metrics.md",
    "reports/22_zeckendorf_term_scaling.md",
    "reports/23_byte_order_sensitivity.md",
    "requirements.txt",
]


def main() -> None:
    missing = [relative for relative in REQUIRED if not (ROOT / relative).is_file()]
    empty = [
        relative
        for relative in REQUIRED
        if (ROOT / relative).is_file() and (ROOT / relative).stat().st_size == 0
    ]
    paper = PROJECT / "paper" / "fibonacci_inspired_entropy_reduction.tex"
    digest = hashlib.sha256(paper.read_bytes()).hexdigest().upper()
    paper_text = paper.read_text(encoding="utf-8", errors="replace")
    authors = sum(
        line.lstrip().startswith("\\author[") for line in paper_text.splitlines()
    )
    evidence = {
        "release_version": "1.0",
        "manuscript_status": "final",
        "required_artifacts": len(REQUIRED),
        "missing": missing,
        "empty": empty,
        "paper_sha256": digest,
        "paper_author_commands": authors,
    }
    (ROOT / "results" / "completion_audit.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )
    if missing or empty or authors != 5:
        raise SystemExit(f"Completion audit failed: {evidence}")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
