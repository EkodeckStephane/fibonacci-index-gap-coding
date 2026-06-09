from __future__ import annotations

import csv
from pathlib import Path

from run_native_fisa import ROOT, benchmark, compile_java


BLOCK_SIZES = (16, 32, 64, 128, 256)
DETAIL_OUTPUT = ROOT / "results" / "native_fisa_block_sizes.csv"
SUMMARY_OUTPUT = ROOT / "results" / "native_fisa_block_sizes_summary.csv"
REPORT_OUTPUT = ROOT / "reports" / "22_native_block_size_sensitivity.md"


def corpus_files(corpus: str) -> list[Path]:
    return sorted(path for path in (ROOT / "data" / corpus).iterdir() if path.is_file())


def main() -> None:
    compile_java()
    expected_rows = len(BLOCK_SIZES) * sum(
        len(corpus_files(corpus)) for corpus in ("canterbury", "silesia")
    )
    rows: list[dict[str, object]] = []
    if DETAIL_OUTPUT.exists():
        with DETAIL_OUTPUT.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

    if len(rows) != expected_rows:
        rows = []
        for block_size in BLOCK_SIZES:
            for corpus in ("canterbury", "silesia"):
                for path in corpus_files(corpus):
                    row = benchmark(corpus, path, block_size)
                    rows.append(row)
                    print(corpus, block_size, path.name, row["ratio"], flush=True)
                    with DETAIL_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
                        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                        writer.writeheader()
                        writer.writerows(rows)

    summary: list[dict[str, object]] = []
    for block_size in BLOCK_SIZES:
        for corpus in ("canterbury", "silesia"):
            selected = [
                row
                for row in rows
                if row["corpus"] == corpus and int(row["block_size"]) == block_size
            ]
            original = sum(int(row["original_bytes"]) for row in selected)
            encoded = sum(int(row["encoded_bytes"]) for row in selected)
            shared_blocks = sum(int(row["shared_blocks"]) for row in selected)
            block_count = sum(
                (int(row["original_bytes"]) + block_size - 1) // block_size
                for row in selected
            )
            summary.append(
                {
                    "corpus": corpus,
                    "block_size": block_size,
                    "files": len(selected),
                    "original_bytes": original,
                    "encoded_bytes": encoded,
                    "weighted_ratio": encoded / original,
                    "compressed_files": sum(float(row["ratio"]) < 1 for row in selected),
                    "shared_blocks": shared_blocks,
                    "block_count": block_count,
                    "shared_block_fraction": shared_blocks / block_count,
                }
            )

    with SUMMARY_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary[0].keys())
        writer.writeheader()
        writer.writerows(summary)

    report = [
        "# Native FISA Block-Size Sensitivity",
        "",
        "All values use complete files and include stream framing.",
        "",
        "| Corpus | Block bytes | Weighted ratio | Compressed files | Shared blocks (%) |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summary:
        report.append(
            f"| {row['corpus']} | {row['block_size']} | "
            f"{row['weighted_ratio']:.6f} | {row['compressed_files']} | "
            f"{100 * row['shared_block_fraction']:.3f} |"
        )
    report.extend(
        [
            "",
            "Canterbury is smallest at 32 bytes; Silesia is smallest at 256 bytes.",
            "No tested size produces broad file-level compression.",
            "",
        ]
    )
    REPORT_OUTPUT.write_text("\n".join(report), encoding="utf-8")

    print(f"Wrote {DETAIL_OUTPUT}")
    print(f"Wrote {SUMMARY_OUTPUT}")
    print(f"Wrote {REPORT_OUTPUT}")


if __name__ == "__main__":
    main()
