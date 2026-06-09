from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    source = ROOT / "results" / "native_fisa.csv"
    frame = pd.read_csv(source)
    numeric = [
        "original_bytes",
        "encoded_bytes",
        "ratio",
        "encode_seconds",
        "decode_seconds",
        "encode_mib_s",
        "decode_mib_s",
    ]
    frame[numeric] = frame[numeric].apply(pd.to_numeric)

    summary_rows = []
    for corpus, group in frame.groupby("corpus", sort=False):
        original = group["original_bytes"].sum()
        encoded = group["encoded_bytes"].sum()
        summary_rows.append(
            {
                "corpus": corpus,
                "files": len(group),
                "original_bytes": original,
                "encoded_bytes": encoded,
                "weighted_ratio": encoded / original,
                "compressed_files": int((group["ratio"] < 1).sum()),
                "encode_mib_s": original
                / 1048576
                / group["encode_seconds"].sum(),
                "decode_mib_s": original
                / 1048576
                / group["decode_seconds"].sum(),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(ROOT / "results" / "native_fisa_summary.csv", index=False)

    report = [
        "# Compiled Full-Corpus FISA Evaluation",
        "",
        "The Java implementation uses `BigInteger`, serializes the complete FISA",
        "stream, and verifies exact decode-after-encode equality for every file.",
        "Measurements use 256-byte blocks and no benchmark warmup.",
        "",
        "## Corpus summary",
        "",
        summary.to_markdown(index=False, floatfmt=".6f"),
        "",
        "## Per-file results",
        "",
        frame[
            [
                "corpus",
                "file",
                "original_bytes",
                "ratio",
                "encode_mib_s",
                "decode_mib_s",
            ]
        ].to_markdown(index=False, floatfmt=".6f"),
        "",
        "Ratios slightly above one correspond to the stream-level raw fallback",
        "plus its magic, mode, and length framing. The complete Silesia results",
        "supersede conclusions drawn from the fixed 64 KiB samples.",
        "",
    ]
    (ROOT / "reports" / "16_native_full_corpus.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
