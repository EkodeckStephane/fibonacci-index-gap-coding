from __future__ import annotations

import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.metrics import shannon_entropy


def conditional_entropy_order1(data: bytes) -> float:
    """Empirical H(X_t | X_{t-1}) in bits per byte."""
    if len(data) < 2:
        return 0.0
    previous = Counter(data[:-1])
    pairs = Counter(zip(data[:-1], data[1:]))
    total = len(data) - 1
    entropy = 0.0
    for (left, _), count in pairs.items():
        entropy -= (count / total) * math.log2(count / previous[left])
    return entropy


def corpus_entropy_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for corpus in ("canterbury", "silesia_sample"):
        root = ROOT / "data" / corpus
        for path in sorted(root.iterdir()):
            if not path.is_file():
                continue
            data = path.read_bytes()
            h0 = shannon_entropy(data)
            h1 = conditional_entropy_order1(data)
            rows.append(
                {
                    "corpus": corpus,
                    "file": path.name,
                    "bytes": len(data),
                    "h0_bits_per_byte": h0,
                    "h1_bits_per_byte": h1,
                    "h0_minus_h1": h0 - h1,
                }
            )
    return rows


def paired_statistics() -> pd.DataFrame:
    outputs = []
    for csv_name in ("benchmark_canterbury.csv", "benchmark_silesia_sample.csv"):
        frame = pd.read_csv(ROOT / "results" / csv_name)
        corpus = str(frame["corpus"].iloc[0])
        fib = frame[frame["method"].str.startswith("fipb_")]
        modern = frame[
            frame["method"].isin(["zlib_9", "bzip2_9", "lzma_9", "brotli_11"])
        ]
        paired = pd.DataFrame(
            {
                "best_fipb": fib.groupby("file")["ratio"].min(),
                "best_modern": modern.groupby("file")["ratio"].min(),
            }
        ).dropna()
        differences = paired["best_fipb"] - paired["best_modern"]
        test = wilcoxon(
            differences,
            alternative="greater",
            zero_method="wilcox",
            method="auto",
        )
        outputs.append(
            {
                "corpus": corpus,
                "files": len(paired),
                "mean_best_fipb": paired["best_fipb"].mean(),
                "mean_best_modern": paired["best_modern"].mean(),
                "median_ratio_factor": (paired["best_fipb"] / paired["best_modern"]).median(),
                "fipb_wins": int((differences < 0).sum()),
                "ties": int((differences == 0).sum()),
                "modern_wins": int((differences > 0).sum()),
                "wilcoxon_statistic": float(test.statistic),
                "one_sided_p_value": float(test.pvalue),
            }
        )
    return pd.DataFrame(outputs)


def main() -> None:
    rows = corpus_entropy_rows()
    entropy_path = ROOT / "results" / "entropy_order1.csv"
    with entropy_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    paired = paired_statistics()
    paired.to_csv(ROOT / "results" / "paired_statistics.csv", index=False)

    by_corpus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_corpus[str(row["corpus"])].append(row)

    report = [
        "# Entropy and Paired Statistical Analysis",
        "",
        "Empirical `H0` and first-order conditional entropy `H1` are descriptive",
        "statistics, not universal finite-file lower bounds.",
        "",
        "## Entropy",
        "",
        "| Corpus | Files | Mean H0 | Mean H1 | Mean H0-H1 |",
        "|---|---:|---:|---:|---:|",
    ]
    for corpus, group in by_corpus.items():
        count = len(group)
        mean_h0 = sum(float(row["h0_bits_per_byte"]) for row in group) / count
        mean_h1 = sum(float(row["h1_bits_per_byte"]) for row in group) / count
        report.append(
            f"| {corpus} | {count} | {mean_h0:.4f} | {mean_h1:.4f} | "
            f"{mean_h0 - mean_h1:.4f} |"
        )

    report.extend(
        [
            "",
            "## Paired comparison",
            "",
            "For each file, the oracle selects the smallest measured FIPB variant and",
            "the smallest modern baseline. The one-sided Wilcoxon signed-rank test",
            "tests whether `FIPB ratio - modern ratio` is greater than zero.",
            "",
            "| Corpus | Files | FIPB wins | Modern wins | Median factor | p-value |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in paired.to_dict("records"):
        report.append(
            f"| {row['corpus']} | {row['files']} | {row['fipb_wins']} | "
            f"{row['modern_wins']} | {row['median_ratio_factor']:.3f} | "
            f"{row['one_sided_p_value']:.6g} |"
        )
    report.extend(
        [
            "",
            "All files favor the modern-codec oracle. This is consistent with the",
            "serialization and ablation results: reduced gaps can be locally shorter,",
            "but alphabet and symbol-stream costs dominate the complete format.",
        ]
    )
    output = ROOT / "reports" / "08_entropy_and_statistics.md"
    output.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Wrote {entropy_path}, paired_statistics.csv, and {output}")


if __name__ == "__main__":
    main()
